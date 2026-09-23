"""Hidden task tools for the crop input desk of Prairie Ridge Cooperative Association.

Each function lands exactly one row on the member's crop input account and nothing else.
None of them aggregates the ledger, reads a tier table or weighs a policy condition: the
figures they take are worked out by the desk from the published schedules and the member's
records, and passed in already computed.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def issue_return_credit_6859ca91(ctx: ToolContext, account_id: str, invoice_number: str,
                                 delivery_ticket_number: str, product_category: str,
                                 credit_amount: float) -> str:
    """Write a credit memo on a member's crop input account for product that has come back to
    the plant, against the invoice the product was billed on.

    One call books a single credit memo line: the money named is credited to the account, so
    what the member owes on it falls by that amount the moment the line posts, and the credit
    memo carries the invoice number and the delivery ticket the product originally left on, so
    the member and the desk can both see which delivery it answers. The member sees the credit
    on the next statement against that invoice, and the call has completed when the confirmation
    below comes back carrying the credit memo's own reference.

    Args:
        account_id: Id class — the internal reference number identifying the crop input account the credit is
            written on; take it from the crop input account record pulled up for this member
            before the call.
        invoice_number: Fixed-format class — the number of the invoice the returned product was
            billed on, written in the shape IN- followed by seven digits, e.g. IN-4410287, exactly
            as it stands on the billing record; there is no empty-value form, and the number is
            passed with no spaces and no lower-case letters.
        delivery_ticket_number: Fixed-format class — the ticket the product left the plant on,
            written in the shape DT- followed by seven digits, e.g. DT-2210554, exactly as it
            stands on the billing record; there is no empty-value form, and the ticket is passed
            with no spaces and no lower-case letters.
        product_category: Enum class — the input class of the product coming back, one of:
            seed, used when the line is planting seed of any crop; dry_fertilizer, used for dry
            granular plant food and bulk blends; liquid_fertilizer, used for solution and
            suspension plant food pumped from the plant; crop_protection, used for herbicide,
            insecticide and fungicide; micronutrients, used for chelated and sulphate trace
            element products; seed_treatment, used for the coatings and inoculants put on seed
            before it is bagged; adjuvants, used for surfactants, drift agents and other tank
            additives that carry no nutrient or active of their own.
        credit_amount: Fixed-format class — the money credited to the account on this line, in
            USD to 2 decimal places, stated as a positive figure and rounded half away from zero
            to the cent at the moment of the call; there is no empty-value form and no currency
            symbol is passed.

    Returns:
        A confirmation sentence in plain text. It carries the credit memo's own internal
        reference (a string beginning crd_), the invoice number the credit was written against,
        the delivery ticket it answers and the credited money in USD to two decimal places. The
        sentence coming back is what indicates the credit memo has posted to the account; no
        other acknowledgement follows.
    """
    rid = ctx.make_id("crd_", account_id, invoice_number, delivery_ticket_number,
                      product_category, credit_amount)
    rows = ctx.find("agronomy_accounts", account_id=account_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    value = round(float(credit_amount), 2)
    ctx.create("agronomy_invoices", rid, invoice_id=rid, account_id=account_id,
               customer_id=customer_id, event_type="agronomy_credit_memo_issued",
               invoice_number=invoice_number, delivery_ticket_number=delivery_ticket_number,
               product_category=product_category, amount=-value,
               posted_date=ctx.now()[:10])
    return (f"Credit memo {rid} posted on account {account_id}: {value:.2f} USD credited against "
            f"invoice {invoice_number} for the product returned off ticket {delivery_ticket_number}.")


@tool(owner="agent", rw="write")
def assess_overdue_service_charge_aaf992aa(ctx: ToolContext, account_id: str, invoice_number: str,
                                           service_charge_amount: float) -> str:
    """Book a service charge on a member's crop input account against an invoice that has run
    past its due date.

    One call books a single service charge line: the money named is added to what the member
    owes, so the account balance rises by that amount the moment the line posts, and the line is
    attached to the overdue invoice it is charged over so the member's statement shows which
    delivery the charge answers. The member sees the charge on the next statement under that
    invoice number, and the call has completed when the confirmation below comes back carrying
    the charge line's own reference.

    Args:
        account_id: Id class — the internal reference number identifying the crop input account the charge is
            booked on; take it from the crop input account record pulled up for this member
            before the call.
        invoice_number: Fixed-format class — the number of the overdue invoice the charge is
            attached to, written in the shape IN- followed by seven
            digits, e.g. IN-4410287, exactly as it stands on the billing record; there is no empty-value form, and the
            number is passed with no spaces and no lower-case letters.
        service_charge_amount: Fixed-format class — the service charge booked on this line, in
            USD to 2 decimal places, stated as a positive figure and rounded half away from zero
            to the cent at the moment of the call; there is no empty-value form and no currency
            symbol is passed.

    Returns:
        A confirmation sentence in plain text. It carries the service charge line's own internal
        reference (a string beginning fcg_), the invoice number the charge was attached to and
        the charged money in USD to two decimal places. The sentence coming back is what
        indicates the charge has posted to the account; no other acknowledgement follows.
    """
    rid = ctx.make_id("fcg_", account_id, invoice_number, service_charge_amount)
    rows = ctx.find("agronomy_accounts", account_id=account_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    value = round(float(service_charge_amount), 2)
    ctx.create("agronomy_invoices", rid, invoice_id=rid, account_id=account_id,
               customer_id=customer_id, event_type="agronomy_finance_charge_assessed",
               invoice_number=invoice_number, finance_charge_amount=value, amount=value,
               posted_date=ctx.now()[:10])
    return (f"Service charge {rid} posted on account {account_id}: {value:.2f} USD charged "
            f"against overdue invoice {invoice_number}.")


@tool(owner="user", rw="write")
def post_member_arrears_payment_ad47b93a(ctx: ToolContext, account_id: str, payment_reference: str,
                                         payment_method: str, payment_amount: float) -> str:
    """Let the member themselves put a payment onto their crop input account to bring the arrears
    on it back inside the cooperative's terms.

    One call posts a single payment line in the member's own name: the money named is taken off
    what they owe, so the account balance falls by that amount the moment the line posts, and the
    line carries the remittance reference the member is sending the money under together with the
    route it is coming by, so the money can be matched when it lands. The member sees the payment
    on their account immediately and on the next statement, and the call has completed when the
    confirmation below comes back carrying the payment line's own reference.

    Args:
        account_id: Id class — the internal reference number identifying the crop input account the money is
            being put onto; take it from the crop input account record pulled up for this member
            before the call.
        payment_reference: Fixed-format class — the remittance reference the money is being sent
            under, written in the shape PY- followed by six digits, e.g. PY-901772; it is passed
            exactly in that shape, with no spaces and no lower-case letters, and there is no
            empty-value form.
        payment_method: Enum class — the route the money is coming by, one of: check, used when
            the member is mailing or handing over a paper draft; ach, used when the member is
            sending an electronic bank transfer from their own account; grain_settlement_transfer,
            used when the money is coming out of the proceeds of grain the member has sold to the
            cooperative; prepay_application, used when money already held to the member's credit
            ahead of the season is being drawn down onto the account; credit_card, used when the
            member is paying at the counter or over the telephone by card; patronage_credit, used
            when the money is coming out of an equity or patronage disbursement standing to the
            member.
        payment_amount: Fixed-format class — the money the member is putting onto the account on
            this line, in USD to 2 decimal places, stated as a positive figure and rounded half
            away from zero to the cent at the moment of the call; there is no empty-value form
            and no currency symbol is passed.

    Returns:
        A confirmation sentence in plain text. It carries the payment line's own internal
        reference (a string beginning pay_), the remittance reference the money is coming under,
        the route it is coming by and the money in USD to two decimal places. The sentence coming
        back is what indicates the payment has posted to the account; no other acknowledgement
        follows.
    """
    rid = ctx.make_id("pay_", account_id, payment_reference, payment_method, payment_amount)
    rows = ctx.find("agronomy_accounts", account_id=account_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    value = round(float(payment_amount), 2)
    ctx.create("agronomy_invoices", rid, invoice_id=rid, account_id=account_id,
               customer_id=customer_id, event_type="agronomy_payment_posted",
               payment_reference=payment_reference, payment_method=payment_method,
               amount=-value, posted_date=ctx.now()[:10])
    return (f"Payment {rid} posted on account {account_id}: {value:.2f} USD received under "
            f"remittance reference {payment_reference} by {payment_method}.")


@tool(owner="agent", rw="write")
def grant_season_volume_discount_cc5ed557(ctx: ToolContext, account_id: str, invoice_number: str,
                                          discount_amount: float) -> str:
    """Grant the season volume discount a member has earned on a crop input account and book it
    against the last invoice of the season it was earned in.

    One call books a single discount line of the volume kind: the money named is taken off what
    the member owes, so the account balance falls by that amount the moment the line posts, and
    the line is written against the named invoice so the member's statement shows the season the
    discount answers. The member sees the discount on their next statement, and the call has
    completed when the confirmation below comes back carrying the discount line's own reference.

    Args:
        account_id: Id class — the internal reference number identifying the crop input account the discount is
            granted on; take it from the crop input account record pulled up for this member
            before the call.
        invoice_number: Fixed-format class — the number of the invoice the discount line is
            written against, written in the shape IN- followed by seven
            digits, e.g. IN-4410287, exactly as it stands on the billing record; there is no empty-value form, and the
            number is passed with no spaces and no lower-case letters.
        discount_amount: Fixed-format class — the money taken off what the member owes by this
            discount, in USD to 2 decimal places, stated as a positive figure and rounded half
            away from zero to the cent at the moment of the call; there is no empty-value form
            and no currency symbol is passed.

    Returns:
        A confirmation sentence in plain text. It carries the discount line's own internal
        reference (a string beginning dsc_), the invoice number the discount was written against
        and the discounted money in USD to two decimal places. The sentence coming back is what
        indicates the discount has posted to the account; no other acknowledgement follows.
    """
    rid = ctx.make_id("dsc_", account_id, invoice_number, discount_amount)
    rows = ctx.find("agronomy_accounts", account_id=account_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    value = round(float(discount_amount), 2)
    ctx.create("agronomy_invoices", rid, invoice_id=rid, account_id=account_id,
               customer_id=customer_id, event_type="agronomy_discount_granted",
               invoice_number=invoice_number, discount_type="volume", discount_amount=value,
               amount=-value, posted_date=ctx.now()[:10])
    return (f"Volume discount {rid} posted on account {account_id}: {value:.2f} USD credited "
            f"against invoice {invoice_number}.")


@tool(owner="user", rw="write")
def book_prepay_commitment_189dfe27(ctx: ToolContext, account_id: str, order_id: str,
                                    product_name: str, booking_amount: float) -> str:
    """Let the member themselves put prepay money onto their crop input account against product
    they are naming for the coming season, answering a prepay request they have already signed
    and lodged with the agronomy desk.

    One call books a single prepay line in the member's own name: the money named is taken in and
    held to their credit, so the prepay standing on the account rises by that amount the moment
    the line posts, and the line carries the product the money is committed against together with
    a booking number the cooperative raises for it. The member can draw that money against
    deliveries of the named product as the season runs, and the call has completed when the
    confirmation below comes back carrying the booking number.

    Args:
        account_id: Id class — the internal reference number identifying the crop input account the prepay is
            held on; take it from the crop input account record pulled up for this member before
            the call.
        order_id: Id class — the internal reference number identifying the signed prepay request the member
            lodged with the agronomy desk that this booking answers; take it from the agronomy
            request records pulled up for this member before the call.
        product_name: Verbatim class — the product the money is committed against, taken from the
            member's own words in this conversation and copied character for character, keeping
            their wording, digits and punctuation, with nothing translated, normalised,
            summarised, added or removed (verbatim).
        booking_amount: Fixed-format class — the money taken in on this booking, in USD to 2
            decimal places, stated as a positive figure and rounded half away from zero to the
            cent at the moment of the call; there is no empty-value form and no currency symbol
            is passed.

    Returns:
        A confirmation sentence in plain text. It carries the prepay line's own internal
        reference (a string beginning ppy_), the booking number raised for it in the shape BK-
        followed by six digits, the product the money is committed against and the money taken in
        in USD to two decimal places. The sentence coming back is what indicates the prepay has
        been taken and is standing to the member's credit; no other acknowledgement follows.
    """
    rid = ctx.make_id("ppy_", account_id, order_id, product_name, booking_amount)
    rows = ctx.find("agronomy_accounts", account_id=account_id)
    customer_id = rows[0].get("customer_id") if rows else ""
    value = round(float(booking_amount), 2)
    booking_reference = "BK-" + str(int(rid[4:10], 16) % 1000000).zfill(6)
    ctx.create("agronomy_invoices", rid, invoice_id=rid, account_id=account_id,
               customer_id=customer_id, event_type="agronomy_prepay_booked",
               booking_reference=booking_reference, product_name=product_name,
               amount=value, invoice_date=ctx.now()[:10], posted_date=ctx.now()[:10])
    return (f"Prepay booking {booking_reference} ({rid}) taken on account {account_id}: "
            f"{value:.2f} USD held to the member's credit against {product_name}.")

"""Hidden task tools for the repair_and_emergency_service difficulty (category: service).

Each tool performs one atomic write on a service call's invoice and is reached only through the
unlock/call meta-tools, by the name an extended policy in service.extended.yaml gives as its
target_tool. No tool checks eligibility, prerequisites or amounts; it books what it is given.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_late_payment_charge_b790dc9b(ctx: ToolContext, ticket_id: str, amount: float) -> dict:
    """Post a late-payment charge on the invoice of one completed service call and raise the amount
    the customer owes on that call by the charge.

    One call adds one late_payment_charge line to the call's invoice, dated today, and increases the
    call's invoice balance by exactly the amount given; nothing else on the call changes. The new
    line is visible at once in the call's invoice lines and the new balance on the call itself.

    Args:
        ticket_id: Id class — reference number of the service call whose invoice is charged, read
            from the service call lookup before the call.
        amount: Fixed-format class — the late-payment charge being billed, in USD, 2 decimal places,
            always positive; a value with more decimals is rounded to the cent half up when booked.

    Returns:
        A dictionary receipt: line_id (text, the reference number of the new invoice line),
        ticket_id (text, the call charged), line_type (text, always late_payment_charge),
        amount (number, the USD amount booked to 2 decimal places), posted_date (text, YYYY-MM-DD,
        today's date) and ticket_balance (number, the call's invoice balance in USD after the
        charge). A receipt carrying a line_id means the charge is on the invoice.
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("svl_", "late_payment_charge", ticket_id, amt)
    ticket = ctx.find("service_tickets", ticket_id=ticket_id)
    customer_id = ticket[0].get("customer_id") if ticket else ""
    balance = round(float((ticket[0].get("ticket_balance") if ticket else 0) or 0) + amt, 2)
    ctx.create("service_lines", rid, line_id=rid, ticket_id=ticket_id, customer_id=customer_id,
               event_type="service_charge", line_type="late_payment_charge", task_code="",
               quantity=1, amount=amt, posted_date=ctx.now()[:10], source_line_id="",
               claim_id="", agreement_id="", payment_method="", payment_reference="")
    ctx.update("service_tickets", ticket_id, ticket_balance=balance)
    return {"line_id": rid, "ticket_id": ticket_id, "line_type": "late_payment_charge",
            "amount": amt, "posted_date": ctx.now()[:10], "ticket_balance": balance}


@tool(owner="agent", rw="write")
def post_on_time_credit_a011cbd0(ctx: ToolContext, ticket_id: str, source_line_id: str, customer_id: str,
                                 agreement_id: str, recall_of_ticket_id: str = "", amount: float = 0.0) -> dict:
    """Post the on-time arrival credit on the invoice of one service call whose technician arrived late,
    lowering the amount the customer owes on that call.

    One call adds one late_arrival_credit line to the call's invoice, dated today, naming the invoice
    line it is attached to and the Comfort Club agreement it was figured under, and lowers the call's
    invoice balance by exactly the amount given. The credit is visible at once among the call's
    invoice lines and in the call's new balance.

    Args:
        ticket_id: Id class — reference number of the service call being credited, read from the
            service call lookup before the call.
        source_line_id: Id class — reference number of the invoice line the credit names (the visit's
            diagnostic fee line), read from the call's invoice lines.
        customer_id: Id class — customer reference number of the account holder, read from the
            customer profile lookup.
        agreement_id: Id class — reference number of the customer's Comfort Club agreement, read from
            the agreement lookup.
        recall_of_ticket_id: Id class — reference number of the earlier call this visit returns to
            under the repair guarantee, copied from the call record; an empty string when the call
            record shows no earlier call.
        amount: Fixed-format class — the credit being posted, in USD, 2 decimal places, always
            positive; a value with more decimals is rounded to the cent half up when booked.

    Returns:
        A dictionary receipt: line_id (text, reference number of the new credit line), ticket_id
        (text), line_type (text, always late_arrival_credit), source_line_id (text, the line named),
        recall_of_ticket_id (text, as passed), amount (number, USD to 2 decimal places), posted_date
        (text, YYYY-MM-DD) and ticket_balance (number, the call's invoice balance in USD after the
        credit). A receipt carrying a line_id means the credit is on the invoice.
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("svl_", "late_arrival_credit", ticket_id, source_line_id, amt)
    ticket = ctx.find("service_tickets", ticket_id=ticket_id)
    balance = round(float((ticket[0].get("ticket_balance") if ticket else 0) or 0) - amt, 2)
    ctx.create("service_lines", rid, line_id=rid, ticket_id=ticket_id, customer_id=customer_id,
               event_type="service_discount", line_type="late_arrival_credit", task_code="",
               quantity=0, amount=amt, posted_date=ctx.now()[:10], source_line_id=source_line_id,
               claim_id="", agreement_id=agreement_id, payment_method="", payment_reference="")
    ctx.update("service_tickets", ticket_id, ticket_balance=balance)
    return {"line_id": rid, "ticket_id": ticket_id, "line_type": "late_arrival_credit",
            "source_line_id": source_line_id, "recall_of_ticket_id": recall_of_ticket_id,
            "amount": amt, "posted_date": ctx.now()[:10], "ticket_balance": balance}


@tool(owner="agent", rw="write")
def post_refrigerant_allowance_39aa6c52(ctx: ToolContext, ticket_id: str, source_line_id: str, customer_id: str,
                                        agreement_id: str, recall_of_ticket_id: str = "", quantity: float = 0.0,
                                        amount: float = 0.0) -> dict:
    """Post a Comfort Club refrigerant allowance against the refrigerant line of one service call's
    invoice, covering pounds of refrigerant free of charge and lowering what the customer owes.

    One call adds one member_refrigerant_allowance line to the call's invoice, dated today, naming the
    refrigerant line it reduces and the Comfort Club agreement whose benefit applies, recording the
    pounds covered, and lowers the call's invoice balance by exactly the amount given. The allowance
    is visible at once among the call's invoice lines and in the call's new balance.

    Args:
        ticket_id: Id class — reference number of the service call, read from the service call
            lookup before the call.
        source_line_id: Id class — reference number of the refrigerant line the allowance reduces,
            read from the call's invoice lines.
        customer_id: Id class — customer reference number of the account holder, read from the
            customer profile lookup.
        agreement_id: Id class — reference number of the customer's Comfort Club agreement, read from
            the agreement lookup.
        recall_of_ticket_id: Id class — reference number of the earlier call this visit returns to
            under the repair guarantee, copied from the call record; an empty string when the call
            record shows no earlier call.
        quantity: Fixed-format class — pounds of refrigerant the allowance covers, recorded as a
            number, up to 1 decimal place (pounds for refrigerant, units otherwise); for this line
            the value is pounds.
        amount: Fixed-format class — the value of the pounds covered, in USD, 2 decimal places,
            always positive; a value with more decimals is rounded to the cent half up when booked.

    Returns:
        A dictionary receipt: line_id (text, reference number of the new allowance line), ticket_id
        (text), line_type (text, always member_refrigerant_allowance), source_line_id (text),
        agreement_id (text), recall_of_ticket_id (text, as passed), quantity (number, pounds covered),
        amount (number, USD to 2 decimal places), posted_date (text, YYYY-MM-DD) and ticket_balance
        (number, the call's invoice balance in USD after the allowance). A receipt carrying a line_id
        means the allowance is on the invoice.
    """
    amt = round(float(amount), 2)
    qty = round(float(quantity), 1)
    rid = ctx.make_id("svl_", "member_refrigerant_allowance", ticket_id, source_line_id, qty, amt)
    ticket = ctx.find("service_tickets", ticket_id=ticket_id)
    balance = round(float((ticket[0].get("ticket_balance") if ticket else 0) or 0) - amt, 2)
    ctx.create("service_lines", rid, line_id=rid, ticket_id=ticket_id, customer_id=customer_id,
               event_type="service_discount", line_type="member_refrigerant_allowance", task_code="",
               quantity=qty, amount=amt, posted_date=ctx.now()[:10], source_line_id=source_line_id,
               claim_id="", agreement_id=agreement_id, payment_method="", payment_reference="")
    ctx.update("service_tickets", ticket_id, ticket_balance=balance)
    return {"line_id": rid, "ticket_id": ticket_id, "line_type": "member_refrigerant_allowance",
            "source_line_id": source_line_id, "agreement_id": agreement_id,
            "recall_of_ticket_id": recall_of_ticket_id, "quantity": qty, "amount": amt,
            "posted_date": ctx.now()[:10], "ticket_balance": balance}


@tool(owner="user", rw="write")
def pay_past_due_installment_4c600ae8(ctx: ToolContext, ticket_id: str, amount: float, payment_method: str) -> dict:
    """The customer pays, in person through the secure payment line, a payment toward the past-due
    invoice of one of their own service calls, lowering what they owe on that call.

    One call records one payment line on the call's invoice, dated today, with a newly issued payment
    confirmation number, and lowers the call's invoice balance by exactly the amount paid. The
    customer hears the confirmation number at once and the payment shows among the call's invoice
    lines.

    Args:
        ticket_id: Id class — reference number of the service call being paid, as the agent reads
            it from the service call lookup and gives it to the customer.
        amount: Fixed-format class — the payment amount, in USD, 2 decimal places, always positive;
            a value with more decimals is rounded to the cent half up when booked.
        payment_method: Enum class — how the customer pays: card when paying with a debit or credit
            card; ach when paying from a checking or savings account by bank transfer; check when
            paying by a mailed or handed-over paper check; cash when paying in cash at the office.

    Returns:
        A dictionary receipt: line_id (text, reference number of the payment line), ticket_id
        (text), amount (number, USD to 2 decimal places), payment_method (text, as passed),
        payment_reference (text, the confirmation number issued for this payment), posted_date
        (text, YYYY-MM-DD) and ticket_balance (number, the call's invoice balance in USD after the
        payment). A receipt carrying a payment_reference means the payment was taken.
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("svl_", "payment", ticket_id, amt, payment_method)
    ref = "HPY-" + ctx.make_id("", ticket_id, amt, payment_method, length=8).upper()
    ticket = ctx.find("service_tickets", ticket_id=ticket_id)
    customer_id = ticket[0].get("customer_id") if ticket else ""
    balance = round(float((ticket[0].get("ticket_balance") if ticket else 0) or 0) - amt, 2)
    ctx.create("service_lines", rid, line_id=rid, ticket_id=ticket_id, customer_id=customer_id,
               event_type="service_payment", line_type="payment", task_code="", quantity=0,
               amount=amt, posted_date=ctx.now()[:10], source_line_id="", claim_id="",
               agreement_id="", payment_method=payment_method, payment_reference=ref)
    ctx.update("service_tickets", ticket_id, ticket_balance=balance)
    return {"line_id": rid, "ticket_id": ticket_id, "amount": amt, "payment_method": payment_method,
            "payment_reference": ref, "posted_date": ctx.now()[:10], "ticket_balance": balance}


@tool(owner="agent", rw="write")
def post_member_premium_discount_f1d91bca(ctx: ToolContext, ticket_id: str, source_line_id: str, customer_id: str,
                                          agreement_id: str, recall_of_ticket_id: str = "", amount: float = 0.0) -> dict:
    """Post a Comfort Club member discount against the after-hours premium line of one service call's
    invoice, lowering the amount the customer owes on that call.

    One call adds one member_premium_discount line to the call's invoice, dated today, naming the
    premium line it reduces and the Comfort Club agreement whose benefit applies, and lowers the
    call's invoice balance by exactly the amount given. The discount is visible at once among the
    call's invoice lines and in the call's new balance.

    Args:
        ticket_id: Id class — reference number of the service call, read from the service call
            lookup before the call.
        source_line_id: Id class — reference number of the after-hours premium line the discount
            reduces, read from the call's invoice lines.
        customer_id: Id class — customer reference number of the account holder, read from the
            customer profile lookup.
        agreement_id: Id class — reference number of the customer's Comfort Club agreement, read from
            the agreement lookup.
        recall_of_ticket_id: Id class — reference number of the earlier call this visit returns to
            under the repair guarantee, copied from the call record; an empty string when the call
            record shows no earlier call.
        amount: Fixed-format class — the discount being posted, in USD, 2 decimal places, always
            positive; a value with more decimals is rounded to the cent half up when booked.

    Returns:
        A dictionary receipt: line_id (text, reference number of the new discount line), ticket_id
        (text), line_type (text, always member_premium_discount), source_line_id (text),
        agreement_id (text), recall_of_ticket_id (text, as passed), amount (number, USD to 2 decimal
        places), posted_date (text, YYYY-MM-DD) and ticket_balance (number, the call's invoice
        balance in USD after the discount). A receipt carrying a line_id means the discount is on the
        invoice.
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("svl_", "member_premium_discount", ticket_id, source_line_id, amt)
    ticket = ctx.find("service_tickets", ticket_id=ticket_id)
    balance = round(float((ticket[0].get("ticket_balance") if ticket else 0) or 0) - amt, 2)
    ctx.create("service_lines", rid, line_id=rid, ticket_id=ticket_id, customer_id=customer_id,
               event_type="service_discount", line_type="member_premium_discount", task_code="",
               quantity=0, amount=amt, posted_date=ctx.now()[:10], source_line_id=source_line_id,
               claim_id="", agreement_id=agreement_id, payment_method="", payment_reference="")
    ctx.update("service_tickets", ticket_id, ticket_balance=balance)
    return {"line_id": rid, "ticket_id": ticket_id, "line_type": "member_premium_discount",
            "source_line_id": source_line_id, "agreement_id": agreement_id,
            "recall_of_ticket_id": recall_of_ticket_id, "amount": amt,
            "posted_date": ctx.now()[:10], "ticket_balance": balance}


@tool(owner="agent", rw="write")
def post_courtesy_discount_1179d4e9(ctx: ToolContext, ticket_id: str, source_line_id: str, customer_id: str,
                                    agreement_id: str, recall_of_ticket_id: str = "", amount: float = 0.0) -> dict:
    """Post the courtesy program discount (senior, military veteran or first responder) against one
    charge line of a service call's invoice, lowering the amount the customer owes on that call.

    One call adds one discount_program line to the call's invoice, dated today, naming the charge
    line it reduces and the Comfort Club agreement it was figured with, and lowers the call's invoice
    balance by exactly the amount given. The discount is visible at once among the call's invoice
    lines and in the call's new balance.

    Args:
        ticket_id: Id class — reference number of the service call, read from the service call
            lookup before the call.
        source_line_id: Id class — reference number of the charge line the discount reduces, read
            from the call's invoice lines.
        customer_id: Id class — customer reference number of the account holder, read from the
            customer profile lookup.
        agreement_id: Id class — reference number of the customer's Comfort Club agreement, read from
            the agreement lookup.
        recall_of_ticket_id: Id class — reference number of the earlier call this visit returns to
            under the repair guarantee, copied from the call record; an empty string when the call
            record shows no earlier call.
        amount: Fixed-format class — the discount being posted, in USD, 2 decimal places, always
            positive; a value with more decimals is rounded to the cent half up when booked.

    Returns:
        A dictionary receipt: line_id (text, reference number of the new discount line), ticket_id
        (text), line_type (text, always discount_program), source_line_id (text), agreement_id
        (text), recall_of_ticket_id (text, as passed), amount (number, USD to 2 decimal places),
        posted_date (text, YYYY-MM-DD) and ticket_balance (number, the call's invoice balance in USD
        after the discount). A receipt carrying a line_id means the discount is on the invoice.
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("svl_", "discount_program", ticket_id, source_line_id, amt)
    ticket = ctx.find("service_tickets", ticket_id=ticket_id)
    balance = round(float((ticket[0].get("ticket_balance") if ticket else 0) or 0) - amt, 2)
    ctx.create("service_lines", rid, line_id=rid, ticket_id=ticket_id, customer_id=customer_id,
               event_type="service_discount", line_type="discount_program", task_code="",
               quantity=0, amount=amt, posted_date=ctx.now()[:10], source_line_id=source_line_id,
               claim_id="", agreement_id=agreement_id, payment_method="", payment_reference="")
    ctx.update("service_tickets", ticket_id, ticket_balance=balance)
    return {"line_id": rid, "ticket_id": ticket_id, "line_type": "discount_program",
            "source_line_id": source_line_id, "agreement_id": agreement_id,
            "recall_of_ticket_id": recall_of_ticket_id, "amount": amt,
            "posted_date": ctx.now()[:10], "ticket_balance": balance}


@tool(owner="user", rw="write")
def pay_special_order_deposit_ccffba41(ctx: ToolContext, ticket_id: str, amount: float, payment_method: str) -> dict:
    """The customer pays, in person through the secure payment line, the amount required to release
    a special-order part on one of their own service calls, lowering what they owe on that call.

    One call records one payment line on the call's invoice, dated today, with a newly issued payment
    confirmation number, and lowers the call's invoice balance by exactly the amount paid. The
    customer hears the confirmation number at once and the payment shows among the call's invoice
    lines.

    Args:
        ticket_id: Id class — reference number of the service call the special-order part was
            quoted on, as the agent reads it from the service call lookup and gives it to the
            customer.
        amount: Fixed-format class — the payment amount, in USD, 2 decimal places, always positive;
            a value with more decimals is rounded to the cent half up when booked.
        payment_method: Enum class — how the customer pays: card when paying with a debit or credit
            card; ach when paying from a checking or savings account by bank transfer; check when
            paying by a mailed or handed-over paper check; cash when paying in cash at the office.

    Returns:
        A dictionary receipt: line_id (text, reference number of the payment line), ticket_id
        (text), amount (number, USD to 2 decimal places), payment_method (text, as passed),
        payment_reference (text, the confirmation number issued for this payment), posted_date
        (text, YYYY-MM-DD) and ticket_balance (number, the call's invoice balance in USD after the
        payment). A receipt carrying a payment_reference means the payment was taken.
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("svl_", "special_order_payment", ticket_id, amt, payment_method)
    ref = "HSO-" + ctx.make_id("", "deposit", ticket_id, amt, payment_method, length=8).upper()
    ticket = ctx.find("service_tickets", ticket_id=ticket_id)
    customer_id = ticket[0].get("customer_id") if ticket else ""
    balance = round(float((ticket[0].get("ticket_balance") if ticket else 0) or 0) - amt, 2)
    ctx.create("service_lines", rid, line_id=rid, ticket_id=ticket_id, customer_id=customer_id,
               event_type="service_payment", line_type="payment", task_code="", quantity=0,
               amount=amt, posted_date=ctx.now()[:10], source_line_id="", claim_id="",
               agreement_id="", payment_method=payment_method, payment_reference=ref)
    ctx.update("service_tickets", ticket_id, ticket_balance=balance)
    return {"line_id": rid, "ticket_id": ticket_id, "amount": amt, "payment_method": payment_method,
            "payment_reference": ref, "posted_date": ctx.now()[:10], "ticket_balance": balance}

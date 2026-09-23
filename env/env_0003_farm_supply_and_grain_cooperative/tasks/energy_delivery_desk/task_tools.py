"""Hidden task tools for the energy delivery desk of Prairie Ridge Cooperative Association.

Each function performs one atomic write on the member's refined fuels and propane account.
None of them aggregates history, prices fuel, or judges whether a policy condition is met:
the member services agent works the figure out from the published desk manuals, the member's
records and the tier catalogue, and passes it in already formed.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def record_price_protection_credit_43e8349b(ctx: ToolContext, energy_account_id: str,
                                            contract_reference: str, gallons: float,
                                            posted_price_per_gallon: float,
                                            protection_credit_usd: float) -> str:
    """Credit downside price protection back to a member's refined fuels or propane account
    against one pre-buy booking held on it.

    One call writes a single protection credit line onto that account for the booking named:
    the money credited is taken off what the member owes on the account, the line carries the
    gallons it was measured on and the posted price it was measured against, and it is dated
    the day the desk works it out. The member sees the credit on the next statement for the
    account and the balance owed drops by exactly the money credited.

    Args:
        energy_account_id: Id class — the internal reference number identifying the refined fuels
            or propane account the credit is applied to, as returned by the energy account
            lookup.
        contract_reference: Fixed-format class — the pre-buy booking reference the protection
            was sold with, written as EC- followed by six digits, e.g. EC-330118, taken from the
            booking line on the account activity; no other form is accepted and it is never left
            empty.
        gallons: Fixed-format class — the gallons the credit was measured on, in US gallons to 1
            decimal place, passed as a decimal number and stored as given with no further
            rounding.
        posted_price_per_gallon: Fixed-format class — the posted price for the fuel the credit
            was measured against, in USD per gallon to 4 decimal places, passed as a decimal
            number and stored as given.
        protection_credit_usd: Fixed-format class — the money credited to the account, in USD to
            2 decimal places, passed as a positive decimal number, rounded half to even to 2
            decimal places on the way in, and carried onto the account as a credit.

    Returns:
        A confirmation sentence, as a plain string, naming the reference of the credit line
        written, the pre-buy booking reference it attaches to, the gallons it was measured on and
        the money credited in USD to 2 decimal places. Receiving that sentence is what indicates
        the credit line now stands on the account.
    """
    _rows = ctx.find("energy_accounts", energy_account_id=energy_account_id)
    acct = _rows[0] if _rows else {}
    rid = ctx.make_id("edl_", energy_account_id, contract_reference, gallons,
                      posted_price_per_gallon, protection_credit_usd)
    ctx.create("energy_deliveries", rid, delivery_id=rid, energy_account_id=energy_account_id,
               customer_id=acct.get("customer_id", ""),
               event_type="energy_price_protection_credited",
               contract_reference=contract_reference, product=acct.get("product", ""),
               gallons=round(float(gallons), 1),
               price_per_gallon=round(float(posted_price_per_gallon), 4),
               amount=-round(float(protection_credit_usd), 2),
               delivery_date=ctx.now()[:10], posted_date=ctx.now()[:10])
    return (f"Price protection credit {rid} recorded against booking {contract_reference} on "
            f"{round(float(gallons), 1)} gallons; {round(float(protection_credit_usd), 2)} USD credited.")


@tool(owner="agent", rw="write")
def bill_budget_plan_reconciliation_cfd56d13(ctx: ToolContext, energy_account_id: str,
                                             reconciliation_amount_usd: float) -> str:
    """Bill the budget plan true-up for a closed plan year onto a member's refined fuels or
    propane account.

    One call writes a single true-up line among the level instalments billed on that account,
    covering the plan month the desk works it out in: a positive figure is added to what the
    member owes and a negative figure is credited to them. The member sees one extra line on the
    plan statement and the balance owed moves by exactly that figure.

    Args:
        energy_account_id: Id class — the internal reference number identifying the refined fuels
            or propane account whose budget plan is being trued up, as returned by the energy
            account lookup.
        reconciliation_amount_usd: Fixed-format class — the true-up figure, in USD to 2 decimal
            places, passed as a decimal number which is positive where the member is billed and
            negative where the member is credited, rounded half to even to 2 decimal places on
            the way in.

    Returns:
        A confirmation sentence, as a plain string, naming the reference of the true-up line
        written, the plan month it was billed for as YYYY-MM, and the figure billed or credited
        in USD to 2 decimal places. Receiving that sentence is what indicates the true-up line
        now stands among the instalments on the account.
    """
    _rows = ctx.find("energy_accounts", energy_account_id=energy_account_id)
    acct = _rows[0] if _rows else {}
    rid = ctx.make_id("edl_", energy_account_id, reconciliation_amount_usd)
    ctx.create("energy_deliveries", rid, delivery_id=rid, energy_account_id=energy_account_id,
               customer_id=acct.get("customer_id", ""),
               event_type="energy_budget_installment_billed",
               billing_month=ctx.now()[:7],
               amount=round(float(reconciliation_amount_usd), 2),
               delivery_date=ctx.now()[:10], posted_date=ctx.now()[:10])
    return (f"Budget plan true-up {rid} billed for plan month {ctx.now()[:7]}; "
            f"{round(float(reconciliation_amount_usd), 2)} USD.")


@tool(owner="user", rw="write")
def post_energy_account_clearing_payment_6fe49ac6(ctx: ToolContext, energy_account_id: str,
                                                  invoice_number: str, payment_reference: str,
                                                  payment_method: str,
                                                  payment_amount_usd: float) -> str:
    """Pay money onto your own refined fuels or propane account and have it applied to the
    earliest-dated energy invoice standing unpaid on it.

    One call posts a single payment line onto that account against the invoice you name: the
    money is taken off what you owe, the line carries your remittance reference and how the money
    reached the cooperative, and it is dated the day you make it. You see the payment on the next
    statement for the account and the balance owed drops by exactly the money paid.

    Args:
        energy_account_id: Id class — the internal reference number of your refined fuels or
            propane account the money is paid onto, as the desk reads it back to you from the
            energy account lookup.
        invoice_number: Fixed-format class — the energy invoice the payment is applied to, which
            is the one standing unpaid on the account with the earliest date on it, written as EI-
            followed by six digits, e.g. EI-440820, as it appears on the statement line being paid;
            no other form is accepted and it is never left empty.
        payment_reference: Fixed-format class — your own remittance reference for this payment,
            written as EP- followed by six digits, e.g. EP-118093, copied exactly as your bank or
            cheque carries it; no other form is accepted and it is never left empty.
        payment_method: Enum class — how the money reaches the cooperative. check where you post
            or hand in a paper cheque drawn on your own account. ach where you send the money as
            a bank transfer from your own bank. budget_draft where the money is taken by the
            standing monthly draft authorised under a level payment plan. grain_settlement_transfer
            where the money comes across from the net proceeds of a grain settlement the
            cooperative owes you. credit_card where you give a card and the money is taken on it.
        payment_amount_usd: Fixed-format class — the money you are paying, in USD to 2 decimal
            places, passed as a positive decimal number, rounded half to even to 2 decimal places
            on the way in, and taken off what you owe on the account.

    Returns:
        A confirmation sentence, as a plain string, naming the reference of the payment line
        written, your remittance reference, the invoice it was applied to and the money paid in
        USD to 2 decimal places. Receiving that sentence is what indicates the payment now stands
        on the account.
    """
    _rows = ctx.find("energy_accounts", energy_account_id=energy_account_id)
    acct = _rows[0] if _rows else {}
    rid = ctx.make_id("edl_", energy_account_id, invoice_number, payment_reference,
                      payment_method, payment_amount_usd)
    ctx.create("energy_deliveries", rid, delivery_id=rid, energy_account_id=energy_account_id,
               customer_id=acct.get("customer_id", ""),
               event_type="energy_payment_posted", invoice_number=invoice_number,
               payment_reference=payment_reference, payment_method=payment_method,
               amount=-round(float(payment_amount_usd), 2),
               delivery_date=ctx.now()[:10], posted_date=ctx.now()[:10])
    return (f"Payment {rid} posted with remittance reference {payment_reference} against invoice "
            f"{invoice_number}; {round(float(payment_amount_usd), 2)} USD paid.")


@tool(owner="user", rw="write")
def lodge_contract_gallon_booking_8fcb503b(ctx: ToolContext, energy_account_id: str,
                                           energy_order_id: str, price_per_gallon: float,
                                           booked_gallons: float) -> str:
    """Put gallons you have signed for ahead of the season to your own credit on your refined fuels
    or propane account.

    One call writes a single pre-buy booking line onto that account: the gallons go to your credit
    at the fixed price you are booking them at, the money those gallons come to is committed on the
    booking, and the line is dated the day you lodge it. You see the booked gallons standing to your
    credit on the account from then on, and fuel drawn against them is priced at the booked price
    rather than the price of the day.

    Args:
        energy_account_id: Id class — the internal reference number identifying your refined fuels
            or propane account the gallons are credited to, as the desk reads it back to you from
            the energy account lookup.
        energy_order_id: Id class — the internal reference number identifying the signed pre-buy
            request you lodged with the energy desk that these gallons are being credited on, as
            the desk reads it back to you from the energy request lookup.
        price_per_gallon: Fixed-format class — the fixed price the booked gallons draw at, in USD
            per gallon to 4 decimal places, passed as a decimal number and stored as given.
        booked_gallons: Fixed-format class — the gallons going to your credit, in gallons to 1
            decimal place, passed as a decimal number and stored as given with no further
            rounding.

    Returns:
        A confirmation sentence, as a plain string, naming the reference of the booking line
        written, the signed request it was credited on, the gallons put to your credit and the money
        committed on them in USD to 2 decimal places. Receiving that sentence is what indicates the
        gallons now stand to your credit on the account.
    """
    _rows = ctx.find("energy_accounts", energy_account_id=energy_account_id)
    acct = _rows[0] if _rows else {}
    rid = ctx.make_id("edl_", energy_account_id, energy_order_id, price_per_gallon, booked_gallons)
    ctx.create("energy_deliveries", rid, delivery_id=rid, energy_account_id=energy_account_id,
               customer_id=acct.get("customer_id", ""),
               event_type="energy_contract_gallons_booked", product=acct.get("product", ""),
               gallons=round(float(booked_gallons), 1),
               price_per_gallon=round(float(price_per_gallon), 4),
               amount=round(float(booked_gallons) * float(price_per_gallon), 2),
               delivery_date=ctx.now()[:10], posted_date=ctx.now()[:10])
    return (f"Pre-buy booking {rid} lodged on signed request {energy_order_id}; "
            f"{round(float(booked_gallons), 1)} gallons to your credit, "
            f"{round(float(booked_gallons) * float(price_per_gallon), 2)} USD committed.")


@tool(owner="agent", rw="write")
def update_contract_price_of_record_9db7726a(ctx: ToolContext, energy_account_id: str,
                                             account_number: str,
                                             contract_price_per_gallon: float) -> str:
    """Rewrite the contracted price of record carried on a member's refined fuels or propane
    account.

    One call replaces the fixed price shown on that account with the price supplied: from then on
    the account shows that price as the one its booked gallons draw at, and delivery tickets and
    statements for the account quote it. Nothing else on the account is touched and no money moves.

    Args:
        energy_account_id: Id class — the internal reference number identifying the refined fuels
            or propane account whose contracted price is being rewritten, as returned by the energy
            account lookup.
        account_number: Fixed-format class — the account number printed on that account's delivery
            tickets and statements, written as EA- followed by six digits, e.g. EA-512044, copied
            from the account record; no other form is accepted and it is never left empty.
        contract_price_per_gallon: Fixed-format class — the contracted price now carried on the
            account, in USD per gallon to 4 decimal places, passed as a decimal number, rounded half
            to even to 4 decimal places on the way in, and stored as given.

    Returns:
        A confirmation sentence, as a plain string, naming the account number the price was written
        against and the contracted price now carried on it in USD per gallon to 4 decimal places.
        Receiving that sentence is what indicates the account now shows that price.
    """
    ctx.update("energy_accounts", energy_account_id,
               contract_price_per_gallon=round(float(contract_price_per_gallon), 4))
    return (f"Contracted price of record on account {account_number} rewritten to "
            f"{round(float(contract_price_per_gallon), 4)} USD per gallon.")


@tool(owner="agent", rw="write")
def settle_undrawn_contract_gallons_1dbcf678(ctx: ToolContext, energy_account_id: str,
                                             gallons: float, settlement_price_per_gallon: float,
                                             undrawn_settlement_usd: float) -> str:
    """Release gallons standing undrawn on a member's pre-buy booking and apply the money they come
    to against that booking.

    One call writes a single drawdown line onto the refined fuels or propane account: the gallons
    named come off the gallons still owed to the member out of the booking, the line carries the
    price they were released at, and the money worked out on them is applied against the booking.
    The member sees the gallons still owed fall by the gallons released and the money applied shown
    on the next statement for the account.

    Args:
        energy_account_id: Id class — the internal reference number identifying the refined fuels
            or propane account whose booking is being released, as returned by the energy account
            lookup.
        gallons: Fixed-format class — the gallons released out of the booking, in US gallons to 1
            decimal place, passed as a decimal number and stored as given with no further rounding.
        settlement_price_per_gallon: Fixed-format class — the price the released gallons are
            settled at, in USD per gallon to 4 decimal places, passed as a decimal number and stored
            as given.
        undrawn_settlement_usd: Fixed-format class — the money applied against the booking, in USD
            to 2 decimal places, passed as a positive decimal number and rounded half to even to 2
            decimal places on the way in.

    Returns:
        A confirmation sentence, as a plain string, naming the reference of the drawdown line
        written, the gallons released, the price they were settled at in USD per gallon to 4 decimal
        places and the money applied against the booking in USD to 2 decimal places. Receiving that
        sentence is what indicates the gallons are released and the money stands applied.
    """
    _rows = ctx.find("energy_accounts", energy_account_id=energy_account_id)
    acct = _rows[0] if _rows else {}
    rid = ctx.make_id("edl_", energy_account_id, gallons, settlement_price_per_gallon,
                      undrawn_settlement_usd)
    ctx.create("energy_deliveries", rid, delivery_id=rid, energy_account_id=energy_account_id,
               customer_id=acct.get("customer_id", ""),
               event_type="energy_contract_gallons_drawn", product=acct.get("product", ""),
               gallons=round(float(gallons), 1),
               price_per_gallon=round(float(settlement_price_per_gallon), 4),
               amount=round(float(undrawn_settlement_usd), 2),
               delivery_date=ctx.now()[:10], posted_date=ctx.now()[:10])
    return (f"Undrawn gallons settled on line {rid}: {round(float(gallons), 1)} gallons released at "
            f"{round(float(settlement_price_per_gallon), 4)} USD per gallon, "
            f"{round(float(undrawn_settlement_usd), 2)} USD applied against the booking.")


@tool(owner="user", rw="write")
def close_energy_account_7515982f(ctx: ToolContext, energy_account_id: str, account_number: str,
                                  closing_balance_usd: float) -> str:
    """Close your own refined fuels or propane account and have the balance it closes at written
    onto it.

    One call puts that account out of service for good: its standing moves to closed, the day you
    close it is recorded against it, the balance it closes at is written onto it as what is owed,
    and the gallons still owed to you out of a pre-buy are set to none. No further fuel is delivered
    on the account and no further charge is raised on it.

    Args:
        energy_account_id: Id class — the internal reference number identifying your refined fuels
            or propane account being closed, as the desk reads it back to you from the energy
            account lookup.
        account_number: Fixed-format class — the account number printed on your delivery tickets
            and statements, written as EA- followed by six digits, e.g. EA-512044, as it appears on
            your statement; no other form is accepted and it is never left empty.
        closing_balance_usd: Fixed-format class — the balance the account closes at, in USD to 2
            decimal places, passed as a decimal number, rounded half to even to 2 decimal places on
            the way in, and written onto the account as what is owed on it.

    Returns:
        A confirmation sentence, as a plain string, naming the account number closed, the date it
        closed as YYYY-MM-DD and the balance it closed at in USD to 2 decimal places. Receiving that
        sentence is what indicates the account now stands closed.
    """
    ctx.update("energy_accounts", energy_account_id, status="closed", closed_date=ctx.now()[:10],
               account_balance=round(float(closing_balance_usd), 2), current_gallons_owed=0)
    return (f"Energy account {account_number} closed on {ctx.now()[:10]} with a balance of "
            f"{round(float(closing_balance_usd), 2)} USD.")

"""Hidden task tools of the service_billing_and_collections difficulty
(env_0042_investor_owned_electric_utility, Lakeshore Power & Light Company).

Each tool performs exactly one atomic business write on an Electric Service Agreement with the
values the agent (or, for a customer-owned tool, the customer) supplies. No tool checks a policy
prerequisite, eligibility, status or amount: those judgements belong to whoever calls it.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_late_payment_charge_a575fa01(ctx: ToolContext, service_account_id: str, bill_id: str,
                                      amount: float) -> str:
    """Post a late payment charge for one bill on an electric service agreement.

    The charge is booked on the agreement as a new late payment charge dated today, tied to the
    bill it was assessed on, and the agreement's balance owed rises by the charged amount. The
    customer sees the charge on the account right away and on the next bill. Calling it once books
    exactly one charge for that bill.

    Args:
        service_account_id: Id class — the service account number of the electric service
            agreement being charged, as returned by the service agreement lookup.
        bill_id: Id class — the reference number of the bill the late payment charge is assessed
            on, as returned by the bill lookup for that agreement.
        amount: Fixed-format class — the late payment charge in USD, a positive number with 2
            decimal places (cents); a value with more decimals is rounded half-up to the cent when
            it is booked.

    Returns:
        A confirmation sentence (string) that states the new charge reference number (an opaque
        id beginning "lpc_"), the bill reference number it was assessed on, the booked amount in
        USD with 2 decimal places, the posting date (YYYY-MM-DD) and the agreement's new balance
        owed in USD with 2 decimal places. Receiving this sentence means the charge is posted.
    """
    amt = round(float(amount) + 1e-9, 2)
    rid = ctx.make_id("lpc_", service_account_id, bill_id, amt)
    acct = ctx.find("service_accounts", service_account_id=service_account_id)[0]
    ctx.create("service_charges", rid, service_charge_id=rid, service_account_id=service_account_id,
               customer_id=acct["customer_id"], event_type="service_late_payment_charge",
               posting_date=ctx.now()[:10], amount=amt, bill_id=bill_id, reversed_payment_id=None,
               reconnect_method="not_applicable", reconnect_timing="not_applicable",
               backbill_reason="not_applicable", charge_code="not_applicable", source_reference_id=None,
               refund_method="not_applicable")
    new_balance = round(float(acct["account_balance"]) + amt + 1e-9, 2)
    ctx.update("service_accounts", service_account_id, account_balance=new_balance)
    return (f"Late payment charge {rid} of {amt:.2f} USD posted {ctx.now()[:10]} on bill {bill_id}; "
            f"agreement balance now {new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def grant_sustained_outage_credit_20084a33(ctx: ToolContext, service_account_id: str, outage_event_id: str,
                                          amount: float) -> str:
    """Post a sustained-outage credit for one outage record on an electric service agreement.

    The credit is booked on the agreement as a new sustained-outage credit dated today, tied to the
    outage record it compensates, and the agreement's balance owed falls by the credited amount.
    The customer sees the credit on the account right away and on the next bill. Calling it once
    books exactly one sustained-outage credit for that outage record.

    Args:
        service_account_id: Id class — the service account number of the electric service
            agreement whose service address had the outage, as returned by the service agreement
            lookup.
        outage_event_id: Id class — the reference number of the outage record being compensated,
            as returned by the outage record lookup for that agreement.
        amount: Fixed-format class — the credit in USD, a positive number with 2 decimal places
            (cents); a value with more decimals is rounded half-up to the cent when it is booked.

    Returns:
        A confirmation sentence (string) that states the new credit reference number (an opaque id
        beginning "soc_"), the outage reference number, the credited amount in USD with 2 decimal
        places, the posting date (YYYY-MM-DD) and the agreement's new balance owed in USD with 2
        decimal places. Receiving this sentence means the credit is posted.
    """
    amt = round(float(amount) + 1e-9, 2)
    rid = ctx.make_id("soc_", service_account_id, outage_event_id, amt)
    acct = ctx.find("service_accounts", service_account_id=service_account_id)[0]
    ctx.create("service_credits", rid, service_credit_id=rid, service_account_id=service_account_id,
               customer_id=acct["customer_id"], event_type="service_outage_credit",
               posting_date=ctx.now()[:10], amount=amt, payment_channel="not_applicable",
               confirmation_number="", credit_code="sustained_outage", source_reference_id=None,
               outage_event_id=outage_event_id)
    new_balance = round(float(acct["account_balance"]) - amt + 1e-9, 2)
    ctx.update("service_accounts", service_account_id, account_balance=new_balance)
    return (f"Sustained-outage credit {rid} of {amt:.2f} USD posted {ctx.now()[:10]} for outage "
            f"{outage_event_id}; agreement balance now {new_balance:.2f} USD.")


@tool(owner="user", rw="write")
def take_card_payment_dce85fc7(ctx: ToolContext, service_account_id: str, amount: float) -> str:
    """Pay toward an electric service agreement by debit or credit card, made by the customer.

    The customer authorizes a one-time card payment of the stated amount on the agreement. The card
    processor issues a confirmation number at authorization, the payment is posted to the agreement
    today under that number through the card channel, and the agreement's balance owed falls by the
    amount paid. The customer can read the confirmation number back at once; the payment shows on
    the account immediately.

    Args:
        service_account_id: Id class — the service account number of the electric service
            agreement the customer is paying, as the agent reads it out from the service agreement
            lookup.
        amount: Fixed-format class — the payment amount in USD, a positive number with 2 decimal
            places (cents); a value with more decimals is rounded half-up to the cent when it is
            posted.

    Returns:
        A confirmation sentence (string) that states the card payment confirmation number (an
        opaque reference beginning "CRD-"), the amount paid in USD with 2 decimal places, the
        posting date (YYYY-MM-DD) and the agreement's new balance owed in USD with 2 decimal
        places. Receiving this sentence means the payment is posted.
    """
    amt = round(float(amount) + 1e-9, 2)
    rid = ctx.make_id("pay_", service_account_id, amt)
    confirmation = "CRD-" + ctx.make_id("", service_account_id, amt, ctx.now(), length=10).upper()
    acct = ctx.find("service_accounts", service_account_id=service_account_id)[0]
    ctx.create("service_credits", rid, service_credit_id=rid, service_account_id=service_account_id,
               customer_id=acct["customer_id"], event_type="service_payment",
               posting_date=ctx.now()[:10], amount=amt, payment_channel="card",
               confirmation_number=confirmation, credit_code="not_applicable", source_reference_id=None,
               outage_event_id=None)
    new_balance = round(float(acct["account_balance"]) - amt + 1e-9, 2)
    ctx.update("service_accounts", service_account_id, account_balance=new_balance)
    return (f"Card payment {confirmation} of {amt:.2f} USD posted {ctx.now()[:10]}; "
            f"agreement balance now {new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def issue_reconnection_order_52263bc7(ctx: ToolContext, service_account_id: str, reconnection_charge: float,
                                     reconnect_method: str, reconnect_timing: str) -> str:
    """Issue a reconnection order that restores a disconnected electric service agreement.

    The order moves the agreement back to active status with today as its latest status date and,
    when the reconnection charge is above zero, books one reconnection charge dated today that
    records how service is restored and when the order is worked; the agreement's balance owed rises
    by that charge. The customer sees the agreement as active and the charge on the account at once.

    Args:
        service_account_id: Id class — the service account number of the disconnected electric
            service agreement to restore, as returned by the service agreement lookup.
        reconnection_charge: Fixed-format class — the reconnection charge in USD, a number of 0 or
            more with 2 decimal places (cents); 0.00 books no charge; a value with more decimals is
            rounded half-up to the cent.
        reconnect_method: Enum class — how service is restored, exactly one of: remote — service is
            switched back on through the remote switch of the meter in service; field — a crew
            restores service at the premise; not_applicable — never used on a reconnection order,
            the value exists only for charges of other kinds.
        reconnect_timing: Enum class — when the order is worked, exactly one of: standard_hours —
            the order is placed and worked within the standard reconnection hours; after_hours —
            the order is placed outside the standard reconnection hours for same-day restoration;
            not_applicable — never used on a reconnection order, the value exists only for charges
            of other kinds.

    Returns:
        A confirmation sentence (string) that states the agreement's new status (active), the
        status date (YYYY-MM-DD), the reconnection charge reference number (an opaque id beginning
        "rcc_", or "none" when the charge is 0.00), the charge in USD with 2 decimal places, the
        restoration method and timing, and the agreement's new balance owed in USD with 2 decimal
        places. Receiving this sentence means the order is issued.
    """
    amt = round(float(reconnection_charge) + 1e-9, 2)
    today = ctx.now()[:10]
    acct = ctx.find("service_accounts", service_account_id=service_account_id)[0]
    ctx.update("service_accounts", service_account_id, status="active", last_status_date=today)
    rid = "none"
    new_balance = round(float(acct["account_balance"]) + 1e-9, 2)
    if amt > 0:
        rid = ctx.make_id("rcc_", service_account_id, amt, reconnect_method, reconnect_timing)
        ctx.create("service_charges", rid, service_charge_id=rid, service_account_id=service_account_id,
                   customer_id=acct["customer_id"], event_type="service_reconnection_charge",
                   posting_date=today, amount=amt, bill_id=None, reversed_payment_id=None,
                   reconnect_method=reconnect_method, reconnect_timing=reconnect_timing,
                   backbill_reason="not_applicable", charge_code="not_applicable", source_reference_id=None,
                   refund_method="not_applicable")
        new_balance = round(float(acct["account_balance"]) + amt + 1e-9, 2)
        ctx.update("service_accounts", service_account_id, account_balance=new_balance)
    return (f"Agreement {service_account_id} is active as of {today}; reconnection charge {rid} of "
            f"{amt:.2f} USD ({reconnect_method}, {reconnect_timing}); agreement balance now "
            f"{new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def grant_chronic_outage_credit_becf7e74(ctx: ToolContext, service_account_id: str, outage_event_id: str,
                                        amount: float) -> str:
    """Post a chronic-outage credit on an electric service agreement for repeated interruptions.

    The credit is booked on the agreement as a new chronic-outage credit dated today, attached to the
    outage record named, and the agreement's balance owed falls by the credited amount. The customer
    sees the credit on the account right away and on the next bill. Calling it once books exactly one
    chronic-outage credit.

    Args:
        service_account_id: Id class — the service account number of the electric service
            agreement whose service address had the repeated outages, as returned by the service
            agreement lookup.
        outage_event_id: Id class — the reference number of the outage record the credit is attached
            to, as returned by the outage record lookup for that agreement.
        amount: Fixed-format class — the credit in USD, a positive number with 2 decimal places
            (cents); a value with more decimals is rounded half-up to the cent when it is booked.

    Returns:
        A confirmation sentence (string) that states the new credit reference number (an opaque id
        beginning "coc_"), the outage reference number it is attached to, the credited amount in USD
        with 2 decimal places, the posting date (YYYY-MM-DD) and the agreement's new balance owed in
        USD with 2 decimal places. Receiving this sentence means the credit is posted.
    """
    amt = round(float(amount) + 1e-9, 2)
    rid = ctx.make_id("coc_", service_account_id, outage_event_id, amt)
    acct = ctx.find("service_accounts", service_account_id=service_account_id)[0]
    ctx.create("service_credits", rid, service_credit_id=rid, service_account_id=service_account_id,
               customer_id=acct["customer_id"], event_type="service_outage_credit",
               posting_date=ctx.now()[:10], amount=amt, payment_channel="not_applicable",
               confirmation_number="", credit_code="chronic_outage", source_reference_id=None,
               outage_event_id=outage_event_id)
    new_balance = round(float(acct["account_balance"]) - amt + 1e-9, 2)
    ctx.update("service_accounts", service_account_id, account_balance=new_balance)
    return (f"Chronic-outage credit {rid} of {amt:.2f} USD posted {ctx.now()[:10]} on outage "
            f"{outage_event_id}; agreement balance now {new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def transfer_prior_balance_e8000638(ctx: ToolContext, service_account_id: str, source_reference_id: str,
                                   amount: float) -> str:
    """Transfer the unpaid balance of a closed electric service agreement onto an open agreement.

    Books two entries dated today: a balance-transfer debit on the receiving (open) agreement for the
    transfer amount given, which raises its balance owed, and a balance-transfer credit on the closed
    agreement equal to the closed agreement's recorded balance, which brings that balance to zero.
    Each entry names the other agreement as its source. The customer sees the old balance gone from
    the closed agreement and the transfer on the open agreement at once.

    Args:
        service_account_id: Id class — the service account number of the open agreement that
            receives the balance, as returned by the service agreement lookup.
        source_reference_id: Id class — the service account number of the closed agreement whose
            balance is transferred, as returned by the service agreement lookup.
        amount: Fixed-format class — the transfer amount debited to the receiving agreement in USD,
            a positive number with 2 decimal places (cents); a value with more decimals is rounded
            half-up to the cent when it is booked.

    Returns:
        A confirmation sentence (string) that states the transfer debit reference number (an opaque
        id beginning "pbd_") and amount in USD with 2 decimal places, the transfer credit reference
        number (an opaque id beginning "pbc_") and the amount cleared from the closed agreement in
        USD with 2 decimal places, the posting date (YYYY-MM-DD), and both agreements' new balances in
        USD with 2 decimal places. Receiving this sentence means both entries are posted.
    """
    amt = round(float(amount) + 1e-9, 2)
    today = ctx.now()[:10]
    recv = ctx.find("service_accounts", service_account_id=service_account_id)[0]
    closed = ctx.find("service_accounts", service_account_id=source_reference_id)[0]
    cleared = round(float(closed["account_balance"]) + 1e-9, 2)
    did = ctx.make_id("pbd_", service_account_id, source_reference_id, amt)
    cid = ctx.make_id("pbc_", source_reference_id, service_account_id, amt)
    ctx.create("service_charges", did, service_charge_id=did, service_account_id=service_account_id,
               customer_id=recv["customer_id"], event_type="service_program_debit", posting_date=today,
               amount=amt, bill_id=None, reversed_payment_id=None, reconnect_method="not_applicable",
               reconnect_timing="not_applicable", backbill_reason="not_applicable",
               charge_code="prior_balance_transfer", source_reference_id=source_reference_id,
               refund_method="not_applicable")
    ctx.create("service_credits", cid, service_credit_id=cid, service_account_id=source_reference_id,
               customer_id=closed["customer_id"], event_type="service_program_credit", posting_date=today,
               amount=cleared, payment_channel="not_applicable", confirmation_number="",
               credit_code="prior_balance_transfer", source_reference_id=service_account_id, outage_event_id=None)
    recv_balance = round(float(recv["account_balance"]) + amt + 1e-9, 2)
    ctx.update("service_accounts", service_account_id, account_balance=recv_balance)
    ctx.update("service_accounts", source_reference_id, account_balance=0.0)
    return (f"Transfer debit {did} of {amt:.2f} USD posted {today} on {service_account_id} (balance now "
            f"{recv_balance:.2f} USD); transfer credit {cid} of {cleared:.2f} USD cleared {source_reference_id} "
            f"(balance now 0.00 USD).")


@tool(owner="user", rw="write")
def authorize_bank_draft_payment_056776f4(ctx: ToolContext, service_account_id: str, amount: float) -> str:
    """Pay toward an electric service agreement by a one-time bank draft, authorized by the customer.

    The customer authorizes a single electronic draft of the stated amount from their own checking
    account to the agreement. The payment channel issues a confirmation number at authorization, the
    payment is posted to the agreement today under that number through the online bank transfer
    channel, and the agreement's balance owed falls by the amount. The customer can read the
    confirmation number back at once; the payment shows on the account immediately.

    Args:
        service_account_id: Id class — the service account number of the electric service agreement
            the customer is paying, as the agent reads it out from the service agreement lookup.
        amount: Fixed-format class — the draft amount in USD, a positive number with 2 decimal places
            (cents); a value with more decimals is rounded half-up to the cent when it is posted.

    Returns:
        A confirmation sentence (string) that states the bank draft confirmation number (an opaque
        reference beginning "EFT-"), the amount drafted in USD with 2 decimal places, the posting date
        (YYYY-MM-DD) and the agreement's new balance owed in USD with 2 decimal places. Receiving this
        sentence means the payment is posted.
    """
    amt = round(float(amount) + 1e-9, 2)
    rid = ctx.make_id("eft_", service_account_id, amt)
    confirmation = "EFT-" + ctx.make_id("", service_account_id, amt, ctx.now(), length=10).upper()
    acct = ctx.find("service_accounts", service_account_id=service_account_id)[0]
    ctx.create("service_credits", rid, service_credit_id=rid, service_account_id=service_account_id,
               customer_id=acct["customer_id"], event_type="service_payment",
               posting_date=ctx.now()[:10], amount=amt, payment_channel="online_bank_transfer",
               confirmation_number=confirmation, credit_code="not_applicable", source_reference_id=None,
               outage_event_id=None)
    new_balance = round(float(acct["account_balance"]) - amt + 1e-9, 2)
    ctx.update("service_accounts", service_account_id, account_balance=new_balance)
    return (f"Bank draft {confirmation} of {amt:.2f} USD posted {ctx.now()[:10]}; "
            f"agreement balance now {new_balance:.2f} USD.")

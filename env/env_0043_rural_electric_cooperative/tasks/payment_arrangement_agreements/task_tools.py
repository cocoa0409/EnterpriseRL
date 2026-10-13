"""Hidden task tools for the payment_arrangement_agreements difficulty (category arrange).

Each tool performs one atomic write on the Payment Arrangements records and is reached only
through unlock_* -> call_*. No tool checks a business precondition: every judgement is made by
the agent from the knowledge base and the records before the call.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def book_missed_installment_8c48d67e(ctx: ToolContext, arrangement_id: str, billing_period: str,
                                     installment_number: int, amount: float) -> str:
    """Record on a member's payment arrangement that one billed installment was missed: the
    installment, or the current charges billed with it, was still unpaid when its grace period ended.
    One call adds one missed-installment entry to the arrangement's ledger, dated on the day it is
    recorded, carrying the billing period and number of the installment and the unpaid amount. The
    entry moves nothing on the arrangement's unbilled balance and changes no status; it is counted
    toward the agreement's missed installments from then on and shows in the arrangement ledger.

    Args:
        arrangement_id: Id class — reference number of the payment arrangement the missed installment
            belongs to, as returned by the arrangement lookup for the member.
        billing_period: Fixed-format class — billing period of the bill that carried the missed
            installment, written YYYY-MM (four-digit year, hyphen, two-digit month), exactly as the
            arrangement ledger shows it on that installment's billed entry.
        installment_number: Fixed-format class — number of the missed installment within the agreement,
            a whole number (integer, no decimals) counted from 1 for the first installment billed.
        amount: Fixed-format class — unpaid amount of the missed installment and the current charges
            tested with it, in US dollars as a positive number with 2 decimal places, rounded half up
            to the cent before it is passed.

    Returns:
        A confirmation sentence (string) of the form "Missed installment recorded: entry <entry_id> on
        arrangement <arrangement_id>, installment <n> of period <YYYY-MM>, unpaid amount <amount> USD."
        where <entry_id> is the reference number of the new ledger entry (text), <n> the installment
        number (integer), <YYYY-MM> the billing period and <amount> the recorded amount with 2
        decimals. Receiving this sentence means the entry was recorded.
    """
    rid = ctx.make_id("arm_", arrangement_id, billing_period, installment_number, amount)
    amt = round(float(amount), 2)
    ctx.create("arrange_ledger", rid, arrange_entry_id=rid, arrangement_id=arrangement_id,
               customer_id=(ctx.find("arrangements", arrangement_id=arrangement_id) or [{}])[0].get("customer_id", ""), event_type="arrange_installment_missed",
               entry_date=ctx.now()[:10], billing_period=billing_period,
               installment_number=int(installment_number), amount=amt, rebill_reason="")
    return (f"Missed installment recorded: entry {rid} on arrangement {arrangement_id}, installment "
            f"{int(installment_number)} of period {billing_period}, unpaid amount {amt:.2f} USD.")


@tool(owner="user", rw="write")
def pay_off_payment_agreement_d76d2954(ctx: ToolContext, arrangement_id: str, payoff_amount: float) -> str:
    """The member pays off their own running payment arrangement early. One call bills the balance
    being paid off back onto the member's service bill as an early-payoff entry on the arrangement's
    ledger, dated today, and completes the agreement on the same day: its status becomes completed,
    its end date is set to today and its unbilled balance is closed to zero. Afterwards the member
    sees the agreement as completed and the early-payoff amount on the arrangement ledger.

    Args:
        arrangement_id: Id class — reference number of the member's payment arrangement being paid off,
            as returned by the arrangement lookup and read to the member by the representative.
        payoff_amount: Fixed-format class — balance billed back on the early payoff, in US dollars as a
            positive number with 2 decimal places, rounded half up to the cent before it is passed.

    Returns:
        A confirmation sentence (string) of the form "Agreement <arrangement_id> paid off: <amount> USD
        billed back as early payoff (entry <entry_id>); status completed on <YYYY-MM-DD>." where
        <amount> is the billed-back amount with 2 decimals, <entry_id> the reference number of the new
        ledger entry (text) and <YYYY-MM-DD> today's date. Receiving this sentence means the payoff was
        recorded and the agreement completed.
    """
    rid = ctx.make_id("arp_", arrangement_id, payoff_amount)
    amt = round(float(payoff_amount), 2)
    today = ctx.now()[:10]
    ctx.create("arrange_ledger", rid, arrange_entry_id=rid, arrangement_id=arrangement_id,
               customer_id=(ctx.find("arrangements", arrangement_id=arrangement_id) or [{}])[0].get("customer_id", ""), event_type="arrange_balance_rebill",
               entry_date=today, billing_period="", installment_number=None, amount=amt,
               rebill_reason="early_payoff")
    ctx.update("arrangements", arrangement_id, status="completed", ended_date=today, arranged_balance=0.0)
    return (f"Agreement {arrangement_id} paid off: {amt:.2f} USD billed back as early payoff "
            f"(entry {rid}); status completed on {today}.")


@tool(owner="user", rw="write")
def accept_payment_agreement_6d07adca(ctx: ToolContext, arrangement_id: str, service_account_id: str,
                                      acceptance_method: str, arranged_amount: float) -> str:
    """The member accepts an offered payment arrangement on their own service account. One call
    records the member's acceptance: the agreement's status changes from offered to active, today's
    date becomes its accepted date, the way the member accepted is recorded, and the amount the member
    commits to spread over the installments is recorded as the agreement's arranged amount. Afterwards
    the member sees the agreement as active with that arranged amount.

    Args:
        arrangement_id: Id class — reference number of the offered payment arrangement, as returned by
            the arrangement lookup and read to the member by the representative.
        service_account_id: Id class — reference number of the electric service account the offered
            arrangement covers, as returned by the service account lookup and shown on the arrangement.
        acceptance_method: Enum class — how the member gives the acceptance; exactly one of:
            "recorded_phone_consent" when the member consents aloud on the recorded line during this call;
            "e_signature" when the member signs the agreement electronically through the link or app;
            "signed_paper" when the member signs and returns the printed agreement at an office.
        arranged_amount: Fixed-format class — amount the member commits to spread over the installments,
            in US dollars as a positive number with 2 decimal places, rounded half up to the cent before
            it is passed.

    Returns:
        A confirmation sentence (string) of the form "Agreement <arrangement_id> on service account
        <service_account_id> accepted on <YYYY-MM-DD> by <acceptance_method>; arranged amount <amount> USD;
        status active." where <YYYY-MM-DD> is
        today's date, <acceptance_method> the method recorded and <amount> the arranged amount with 2
        decimals. Receiving this sentence means the acceptance was recorded.
    """
    amt = round(float(arranged_amount), 2)
    today = ctx.now()[:10]
    ctx.update("arrangements", arrangement_id, service_account_id=service_account_id, status="active", accepted_date=today,
               acceptance_method=acceptance_method, arranged_amount=amt)
    return (f"Agreement {arrangement_id} on service account {service_account_id} accepted on {today} by "
            f"{acceptance_method}; arranged amount "
            f"{amt:.2f} USD; status active.")


@tool(owner="agent", rw="write")
def move_balance_into_agreement_3b3ea9ff(ctx: ToolContext, arrangement_id: str, amount: float) -> str:
    """Move the past-due balance of a member's accepted payment arrangement off the service
    account and into the agreement. One call adds a balance-transfer entry to the arrangement's
    ledger, dated today, and raises the agreement's unbilled balance by the amount moved. Afterwards
    the arrangement ledger shows the transfer and the agreement carries that unbilled balance for its
    installments.

    Args:
        arrangement_id: Id class — reference number of the accepted payment arrangement, as returned by
            the arrangement lookup for the member.
        amount: Fixed-format class — amount moved into the agreement, in US dollars as a positive number
            with 2 decimal places, rounded half up to the cent before it is passed.

    Returns:
        A confirmation sentence (string) of the form "Balance moved into agreement <arrangement_id>:
        <amount> USD (entry <entry_id>); unbilled balance now <balance> USD." where <amount> is the
        amount moved and <balance> the agreement's unbilled balance afterwards, both with 2 decimals,
        and <entry_id> the reference number of the new ledger entry (text). Receiving this sentence
        means the transfer was recorded.
    """
    rid = ctx.make_id("art_", arrangement_id, amount)
    amt = round(float(amount), 2)
    bal = round(float((ctx.find("arrangements", arrangement_id=arrangement_id) or [{}])[0].get("arranged_balance") or 0) + amt, 2)
    ctx.create("arrange_ledger", rid, arrange_entry_id=rid, arrangement_id=arrangement_id,
               customer_id=(ctx.find("arrangements", arrangement_id=arrangement_id) or [{}])[0].get("customer_id", ""), event_type="arrange_balance_transfer",
               entry_date=ctx.now()[:10], billing_period="", installment_number=None, amount=amt,
               rebill_reason="")
    ctx.update("arrangements", arrangement_id, arranged_balance=bal)
    return (f"Balance moved into agreement {arrangement_id}: {amt:.2f} USD (entry {rid}); unbilled "
            f"balance now {bal:.2f} USD.")


@tool(owner="agent", rw="write")
def bill_agreement_installment_2bd16d35(ctx: ToolContext, arrangement_id: str, billing_period: str,
                                        installment_number: int, amount: float) -> str:
    """Bill one installment of a member's running payment arrangement on the service account's
    monthly bill. One call adds an installment-billed entry to the arrangement's ledger, dated today
    (the bill date), carrying the billing period and the installment number, and lowers the
    agreement's unbilled balance by the amount billed. Afterwards the arrangement ledger shows the
    installment billed and the reduced unbilled balance.

    Args:
        arrangement_id: Id class — reference number of the running payment arrangement, as returned by
            the arrangement lookup for the member.
        billing_period: Fixed-format class — billing period of the bill that carries the installment,
            written YYYY-MM (four-digit year, hyphen, two-digit month), the period of the service bill
            dated today as the service charges lookup shows it.
        installment_number: Fixed-format class — number of this installment within the agreement, a
            whole number (integer, no decimals): one more than the highest installment number already
            billed on the agreement.
        amount: Fixed-format class — amount of the installment billed, in US dollars as a positive number
            with 2 decimal places, rounded half up to the cent before it is passed.

    Returns:
        A confirmation sentence (string) of the form "Installment <n> billed on agreement
        <arrangement_id> for period <YYYY-MM>: <amount> USD (entry <entry_id>); unbilled balance now
        <balance> USD." where <n> is the installment number (integer), <amount> and <balance> carry 2
        decimals and <entry_id> is the reference number of the new ledger entry (text). Receiving this
        sentence means the installment was billed.
    """
    rid = ctx.make_id("ari_", arrangement_id, billing_period, installment_number, amount)
    amt = round(float(amount), 2)
    bal = round(float((ctx.find("arrangements", arrangement_id=arrangement_id) or [{}])[0].get("arranged_balance") or 0) - amt, 2)
    ctx.create("arrange_ledger", rid, arrange_entry_id=rid, arrangement_id=arrangement_id,
               customer_id=(ctx.find("arrangements", arrangement_id=arrangement_id) or [{}])[0].get("customer_id", ""), event_type="arrange_installment_bill",
               entry_date=ctx.now()[:10], billing_period=billing_period,
               installment_number=int(installment_number), amount=amt, rebill_reason="")
    ctx.update("arrangements", arrangement_id, arranged_balance=bal)
    return (f"Installment {int(installment_number)} billed on agreement {arrangement_id} for period "
            f"{billing_period}: {amt:.2f} USD (entry {rid}); unbilled balance now {bal:.2f} USD.")


@tool(owner="agent", rw="write")
def record_agreement_default_c78cb15c(ctx: ToolContext, arrangement_id: str, rebill_amount: float) -> str:
    """Put a member's running payment arrangement into default. One call records the default: the
    agreement's status changes from active to defaulted with today as its end date, the balance being
    billed back is added to the arrangement's ledger as a default entry dated today, and the
    agreement's unbilled balance is closed to zero. Afterwards the agreement shows as defaulted and
    the default entry shows on its ledger.

    Args:
        arrangement_id: Id class — reference number of the running payment arrangement that defaults, as
            returned by the arrangement lookup for the member.
        rebill_amount: Fixed-format class — balance billed back at the default, in US dollars as a
            positive number with 2 decimal places, rounded half up to the cent before it is passed.

    Returns:
        A confirmation sentence (string) of the form "Agreement <arrangement_id> defaulted on
        <YYYY-MM-DD>: <amount> USD billed back (entry <entry_id>); status defaulted." where <YYYY-MM-DD>
        is today's date, <amount> the billed-back amount with 2 decimals and <entry_id> the reference
        number of the new ledger entry (text). Receiving this sentence means the default was recorded.
    """
    rid = ctx.make_id("ard_", arrangement_id, rebill_amount)
    amt = round(float(rebill_amount), 2)
    today = ctx.now()[:10]
    ctx.create("arrange_ledger", rid, arrange_entry_id=rid, arrangement_id=arrangement_id,
               customer_id=(ctx.find("arrangements", arrangement_id=arrangement_id) or [{}])[0].get("customer_id", ""), event_type="arrange_balance_rebill",
               entry_date=today, billing_period="", installment_number=None, amount=amt,
               rebill_reason="default")
    ctx.update("arrangements", arrangement_id, status="defaulted", ended_date=today, arranged_balance=0.0)
    return (f"Agreement {arrangement_id} defaulted on {today}: {amt:.2f} USD billed back (entry {rid}); "
            f"status defaulted.")

"""Hidden task tools for deficiency_balance_resolution (env_0072_subprime_auto_lender).

Each tool performs one atomic change on a Deficiency Balance Account and returns a receipt.
The tools never check eligibility, prerequisites or amounts; the representative and the
borrower decide those from the published policy and the records.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def pay_restart_down_payment_04892a83(ctx: ToolContext, deficiency_account_id: str, amount_usd: float) -> str:
    """The borrower authorises, from their own checking account through the self-service bank
    payment channel, a one-time down payment on their Deficiency Balance Account that is not tied
    to any payment plan or settlement. The payment is posted on the account's ledger on today's
    date as a self-service bank payment carrying no arrangement, the account balance is reduced by
    the amount paid, and the account's latest payment date becomes today. The borrower sees the
    posted payment and the new balance in the receipt.

    Args:
        deficiency_account_id: Id class — the reference number of the borrower's Deficiency Balance
            Account the payment is posted to, as returned by the deficiency account lookup for this
            borrower.
        amount_usd: Fixed-format class — the down payment amount the borrower authorises, in USD,
            2 decimal places, 0.00 or more; the value is rounded half up to 2 decimal places when
            posted.

    Returns:
        A dictionary rendered as text with: status ("posted" when the payment is on the ledger);
        deficiency_txn_id (reference number of the posted payment); deficiency_account_id (the
        account paid); amount_usd (amount posted, USD, 2 decimal places); payment_channel (always
        ach_self_service); txn_date (posting date, YYYY-MM-DD); deficiency_balance_usd (account
        balance after the payment, USD, 2 decimal places).
    """
    amount = round(float(amount_usd), 2)
    acct = ctx.find("deficiency_accounts", deficiency_account_id=deficiency_account_id)
    customer_id = acct[0].get("customer_id") if acct else ""
    balance = round(float(acct[0].get("deficiency_balance_usd") or 0) - amount, 2) if acct else 0.0
    today = ctx.now()[:10]
    rid = ctx.make_id("dtx_", deficiency_account_id, amount)
    ctx.create("deficiency_transactions", rid, deficiency_txn_id=rid, deficiency_account_id=deficiency_account_id,
               customer_id=customer_id, event_type="deficiency_payment_posted", txn_date=today,
               amount_usd=amount, payment_channel="ach_self_service", arrangement_offer_id=None,
               related_txn_id="", return_reason="not_applicable", credit_source="not_applicable",
               source_record_id="", form_1099c_required=False)
    ctx.update("deficiency_accounts", deficiency_account_id, deficiency_balance_usd=balance, last_payment_date=today)
    return str({"status": "posted", "deficiency_txn_id": rid, "deficiency_account_id": deficiency_account_id,
                "amount_usd": amount, "payment_channel": "ach_self_service", "txn_date": today,
                "deficiency_balance_usd": balance})


@tool(owner="agent", rw="write")
def record_payment_plan_offer_3f4fb3a9(ctx: ToolContext, deficiency_account_id: str,
                                       installment_amount_usd: float) -> str:
    """Record a payment-plan offer on a borrower's Deficiency Balance Account so the borrower can
    accept it within the offer period. The offer is dated today with status offered and covers the
    account's whole current balance; it states the monthly installment given here, the number of
    monthly installments that installment needs to pay the whole balance (the balance divided by
    the installment, rounded up to a whole installment), no further down payment, no hardship
    document, and no due date yet, since the due date is set when the borrower accepts. The account
    itself, its balance and its status do not change. The receipt shows the new offer and its terms.

    Args:
        deficiency_account_id: Id class — the reference number of the Deficiency Balance Account the
            offer covers, as returned by the deficiency account lookup for this borrower.
        installment_amount_usd: Fixed-format class — the monthly plan installment stated in the
            offer, in USD, 2 decimal places; the value is rounded half up to 2 decimal places when
            recorded.

    Returns:
        A dictionary rendered as text with: status ("offered" when the offer is recorded);
        arrangement_offer_id (reference number of the new offer); deficiency_account_id;
        offer_type (always payment_plan); offer_date (YYYY-MM-DD); offer_amount_usd (the balance the
        plan covers, USD, 2 decimal places); installment_amount_usd (USD, 2 decimal places);
        installment_count (integer number of monthly installments).
    """
    installment = round(float(installment_amount_usd), 2)
    acct = ctx.find("deficiency_accounts", deficiency_account_id=deficiency_account_id)
    customer_id = acct[0].get("customer_id") if acct else ""
    balance = round(float(acct[0].get("deficiency_balance_usd") or 0), 2) if acct else 0.0
    count = int(-((-round(balance * 100)) // round(installment * 100))) if installment > 0 else 0
    today = ctx.now()[:10]
    rid = ctx.make_id("dao_", deficiency_account_id, installment)
    ctx.create("deficiency_arrangement_offers", rid, arrangement_offer_id=rid, customer_id=customer_id,
               deficiency_account_id=deficiency_account_id, offer_type="payment_plan", offer_date=today,
               offer_amount_usd=balance, installment_count=count, installment_amount_usd=installment,
               first_due_date="", down_payment_usd=0.0, hardship_document="none", offer_status="offered",
               accepted_at="", broken_date="", created_at=ctx.now())
    return str({"status": "offered", "arrangement_offer_id": rid, "deficiency_account_id": deficiency_account_id,
                "offer_type": "payment_plan", "offer_date": today, "offer_amount_usd": balance,
                "installment_amount_usd": installment, "installment_count": count})


class _SettlementCalendar:
    """Calendar arithmetic for settlement due dates (pure Python, no clock access)."""

    @staticmethod
    def first_due(day_text: str) -> str:
        year, month, day = int(day_text[0:4]), int(day_text[5:7]), int(day_text[8:10])
        month += 1
        if month > 12:
            month, year = 1, year + 1
        return f"{year:04d}-{month:02d}-{min(day, 28):02d}"


@tool(owner="agent", rw="write")
def record_lump_sum_settlement_offer_7c3d7537(ctx: ToolContext, deficiency_account_id: str, offer_amount_usd: float,
                                              hardship_document: str) -> str:
    """Record a lump-sum settlement offer on a borrower's Deficiency Balance Account so the borrower
    can accept it within the offer period. The offer is dated today with status offered and states the
    single lump-sum amount given here as both the amount the borrower pays and its one installment,
    no down payment, the hardship document recorded with it, and no due date yet, since the due date
    is set when the borrower accepts. The account itself, its balance and its status do not change.
    The receipt shows the new offer and its terms.

    Args:
        deficiency_account_id: Id class — the reference number of the Deficiency Balance Account the
            offer covers, as returned by the deficiency account lookup for this borrower.
        offer_amount_usd: Fixed-format class — the lump-sum settlement amount stated in the offer, in
            USD, 2 decimal places; the value is rounded half up to 2 decimal places when recorded.
        hardship_document: Enum class — the hardship document recorded on the offer, exactly one of:
            ssa_award_letter (a Social Security award letter is recorded for the borrower with this
            offer); unemployment_determination (a state unemployment benefit determination is recorded
            with this offer); medical_disability_statement (a physician's disability statement is
            recorded with this offer); none (no hardship document is recorded with this offer).

    Returns:
        A dictionary rendered as text with: status ("offered" when the offer is recorded);
        arrangement_offer_id (reference number of the new offer); deficiency_account_id;
        offer_type (always lump_sum_settlement); offer_date (YYYY-MM-DD); offer_amount_usd (USD,
        2 decimal places); installment_count (integer, always 1); hardship_document (as recorded).
    """
    amount = round(float(offer_amount_usd), 2)
    acct = ctx.find("deficiency_accounts", deficiency_account_id=deficiency_account_id)
    customer_id = acct[0].get("customer_id") if acct else ""
    today = ctx.now()[:10]
    rid = ctx.make_id("dao_", deficiency_account_id, "lump_sum_settlement", amount, today)
    ctx.create("deficiency_arrangement_offers", rid, arrangement_offer_id=rid, customer_id=customer_id,
               deficiency_account_id=deficiency_account_id, offer_type="lump_sum_settlement", offer_date=today,
               offer_amount_usd=amount, installment_count=1, installment_amount_usd=amount, first_due_date="",
               down_payment_usd=0.0, hardship_document=hardship_document, offer_status="offered",
               accepted_at="", broken_date="", created_at=ctx.now())
    return str({"status": "offered", "arrangement_offer_id": rid, "deficiency_account_id": deficiency_account_id,
                "offer_type": "lump_sum_settlement", "offer_date": today, "offer_amount_usd": amount,
                "installment_count": 1, "hardship_document": hardship_document})


@tool(owner="user", rw="write")
def accept_installment_settlement_d1722676(ctx: ToolContext, deficiency_account_id: str,
                                           settlement_amount_usd: float) -> str:
    """The borrower accepts, in their own name, an installment settlement of their Deficiency Balance
    Account for the settlement amount given here. The acceptance is recorded as an installment
    settlement offer dated today with status accepted and the acceptance time of now, carrying the
    settlement amount as the total the borrower will pay, no down payment and no hardship document;
    the number of installments, the installment amount and the first due date stay unset (zero
    installments, 0.00 and an empty date) until the settlement is started. The account's balance and
    status do not change. The borrower sees the accepted settlement and its reference number in the
    receipt.

    Args:
        deficiency_account_id: Id class — the reference number of the borrower's Deficiency Balance
            Account the settlement covers, as returned by the deficiency account lookup for this
            borrower.
        settlement_amount_usd: Fixed-format class — the total settlement amount the borrower accepts,
            in USD, 2 decimal places; the value is rounded half up to 2 decimal places when recorded.

    Returns:
        A dictionary rendered as text with: status ("accepted" when the acceptance is recorded);
        arrangement_offer_id (reference number of the accepted settlement); deficiency_account_id;
        offer_type (always installment_settlement); offer_date (YYYY-MM-DD); offer_amount_usd (the
        accepted settlement amount, USD, 2 decimal places); accepted_at (acceptance time, the clock's
        timestamp text).
    """
    amount = round(float(settlement_amount_usd), 2)
    acct = ctx.find("deficiency_accounts", deficiency_account_id=deficiency_account_id)
    customer_id = acct[0].get("customer_id") if acct else ""
    today = ctx.now()[:10]
    rid = ctx.make_id("dao_", deficiency_account_id, "installment_settlement", amount, today)
    ctx.create("deficiency_arrangement_offers", rid, arrangement_offer_id=rid, customer_id=customer_id,
               deficiency_account_id=deficiency_account_id, offer_type="installment_settlement", offer_date=today,
               offer_amount_usd=amount, installment_count=0, installment_amount_usd=0.0, first_due_date="",
               down_payment_usd=0.0, hardship_document="none", offer_status="accepted",
               accepted_at=ctx.now(), broken_date="", created_at=ctx.now())
    return str({"status": "accepted", "arrangement_offer_id": rid, "deficiency_account_id": deficiency_account_id,
                "offer_type": "installment_settlement", "offer_date": today, "offer_amount_usd": amount,
                "accepted_at": ctx.now()})


@tool(owner="agent", rw="write")
def start_installment_settlement_185f50ba(ctx: ToolContext, deficiency_account_id: str, arrangement_offer_id: str,
                                          installment_amount_usd: float) -> str:
    """Start an accepted installment settlement on a borrower's Deficiency Balance Account. The account
    moves to status on_settlement_plan with the given accepted settlement as its arrangement in force;
    the settlement records the monthly installment given here, the number of installments that
    installment needs to pay the settlement amount (the settlement amount divided by the installment,
    rounded up to a whole installment), and a first due date one month after the acceptance on the
    acceptance's day of the month (the 28th when that day is the 29th, 30th or 31st). The balance does
    not change. The
    receipt shows the account status and the settlement schedule.

    Args:
        deficiency_account_id: Id class — the reference number of the Deficiency Balance Account the
            settlement is started on, as returned by the deficiency account lookup for this borrower.
        arrangement_offer_id: Id class — the reference number of the accepted installment settlement,
            as returned when the borrower accepted it or by the arrangement offer lookup.
        installment_amount_usd: Fixed-format class — the monthly settlement installment, in USD,
            2 decimal places; the value is rounded half up to 2 decimal places when recorded.

    Returns:
        A dictionary rendered as text with: status ("started" when the settlement is in force);
        deficiency_account_id; account_status (always on_settlement_plan); arrangement_offer_id;
        offer_amount_usd (the settlement amount, USD, 2 decimal places); installment_amount_usd (USD,
        2 decimal places); installment_count (integer number of monthly installments);
        first_due_date (YYYY-MM-DD).
    """
    installment = round(float(installment_amount_usd), 2)
    offer = ctx.find("deficiency_arrangement_offers", arrangement_offer_id=arrangement_offer_id)
    amount = round(float(offer[0].get("offer_amount_usd") or 0), 2) if offer else 0.0
    count = int(-((-round(amount * 100)) // round(installment * 100))) if installment > 0 else 0
    accepted = str(offer[0].get("accepted_at") or "") if offer else ""
    first_due = _SettlementCalendar.first_due(accepted[:10] if accepted else ctx.now()[:10])
    ctx.update("deficiency_accounts", deficiency_account_id, status="on_settlement_plan",
               arrangement_offer_id=arrangement_offer_id)
    if offer:
        ctx.update("deficiency_arrangement_offers", arrangement_offer_id, installment_amount_usd=installment,
                   installment_count=count, first_due_date=first_due)
    return str({"status": "started", "deficiency_account_id": deficiency_account_id,
                "account_status": "on_settlement_plan", "arrangement_offer_id": arrangement_offer_id,
                "offer_amount_usd": amount, "installment_amount_usd": installment, "installment_count": count,
                "first_due_date": first_due})

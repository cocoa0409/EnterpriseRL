"""Hidden task tools for the debit_card_disputes_and_card_servicing difficulty (Pocketwire Visa Debit Card).

Each tool performs one atomic write on the card's own records and takes every computed value as an
argument; none of them checks eligibility, status, ownership or any policy prerequisite.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def file_unauthorized_card_dispute_b9450be9(ctx: ToolContext, card_id: str, card_txn_id: str,
                                             dispute_amount: float, customer_liability: float) -> str:
    """The cardholder files, in their own name, an unauthorized-transaction dispute on one settled
    purchase or ATM withdrawal of one of their Pocketwire Visa debit cards, asserting that they did not
    make or authorize it. One call opens exactly one dispute record on that transaction with the reason
    unauthorized, today's filing date, the disputed amount and the customer liability given, the outcome
    pending and no provisional credit posted. The cardholder then sees the dispute as open (pending) on
    that transaction in the app; no money moves on this call.

    Args:
        card_id: Id class — the reference number of the debit card the disputed transaction was made on,
            as shown by the debit card lookup for this cardholder.
        card_txn_id: Id class — the reference number of the settled purchase or ATM withdrawal being
            disputed, as shown by the card activity lookup for that card.
        dispute_amount: Fixed-format class — the amount disputed, in USD, a non-negative number with 2
            decimal places (to the cent), never more than the transaction amount.
        customer_liability: Fixed-format class — the part of the disputed amount the cardholder bears on
            this dispute, in USD, a non-negative number with 2 decimal places (to the cent).

    Returns:
        A dictionary receipt: dispute_record_id (string, the reference number of the new dispute record),
        card_id (string, the card), card_txn_id (string, the disputed transaction), dispute_reason (string,
        always unauthorized), reported_date (string, YYYY-MM-DD, the filing date), dispute_amount (number,
        USD with 2 decimal places), customer_liability (number, USD with 2 decimal places) and resolution
        (string, always pending). A receipt carrying resolution pending means the dispute is open.
    """
    amount = round(float(dispute_amount), 2)
    liability = round(float(customer_liability), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("cdsp_", card_id, card_txn_id, "unauthorized", amount, liability)
    card = ctx.find("card_accounts", card_id=card_id)
    customer_id = card[0].get("customer_id") if card else ""
    ctx.create("card_disputes", rid, card_dispute_id=rid, card_id=card_id, customer_id=customer_id,
               event_type="card_dispute_filed", card_txn_id=card_txn_id, dispute_reason="unauthorized",
               reported_date=today, dispute_amount=amount, customer_liability=liability,
               resolution="pending", resolution_date="", provisional_credit_posted=False)
    return str({"dispute_record_id": rid, "card_id": card_id, "card_txn_id": card_txn_id,
                "dispute_reason": "unauthorized", "reported_date": today, "dispute_amount": amount,
                "customer_liability": liability, "resolution": "pending"})


@tool(owner="agent", rw="write")
def post_takeover_dispute_credit_edfadedb(ctx: ToolContext, card_id: str, card_txn_id: str,
                                          credit_amount: float) -> str:
    """Records the outcome approved on an open unauthorized dispute of a transaction on a Pocketwire
    Visa debit card and books its final dispute credit on that card. One call writes the dispute
    outcome approved with today's date and no provisional credit posted, carrying the reason, disputed
    amount and liability of the open dispute record on that transaction, and credits the given amount to
    the card's settlement balance as a final dispute credit linked to the disputed transaction. The
    cardholder sees the dispute closed as approved and the credit on the card's activity.

    Args:
        card_id: Id class — the reference number of the debit card the disputed transaction was made on,
            as shown by the debit card lookup for this cardholder.
        card_txn_id: Id class — the reference number of the disputed purchase or ATM withdrawal, as shown
            by the card activity lookup or the dispute lookup for that card.
        credit_amount: Fixed-format class — the final credit booked to the card, in USD, a non-negative
            number with 2 decimal places (to the cent).

    Returns:
        A dictionary receipt: outcome_record_id (string, the reference number of the approved outcome
        record), credit_entry_id (string, the reference number of the credit on the card's activity),
        card_txn_id (string, the disputed transaction), resolution (string, always approved),
        resolution_date (string, YYYY-MM-DD) and credit_amount (number, USD with 2 decimal places).
        A receipt with resolution approved and a credit_entry_id means the credit is on the card.
    """
    amount = round(float(credit_amount), 2)
    today = ctx.now()[:10]
    filed = ctx.find("card_disputes", card_txn_id=card_txn_id, event_type="card_dispute_filed")
    src = filed[0] if filed else {}
    card = ctx.find("card_accounts", card_id=card_id)
    customer_id = card[0].get("customer_id") if card else ""
    oid = ctx.make_id("cdsp_", card_id, card_txn_id, "approved", amount)
    ctx.create("card_disputes", oid, card_dispute_id=oid, card_id=card_id, customer_id=customer_id,
               event_type="card_dispute_resolved", card_txn_id=card_txn_id,
               dispute_reason=src.get("dispute_reason", "unauthorized"), reported_date=src.get("reported_date", ""),
               dispute_amount=src.get("dispute_amount", 0.0), customer_liability=src.get("customer_liability", 0.0),
               resolution="approved", resolution_date=today, provisional_credit_posted=False)
    cid = ctx.make_id("ctxn_", card_id, card_txn_id, "card_dispute_credit", amount)
    ctx.create("card_transactions", cid, card_txn_id=cid, card_id=card_id, customer_id=customer_id,
               event_type="card_dispute_credit", txn_reference="", txn_date=today, amount=amount,
               merchant_name="", merchant_category="not_applicable", entry_mode="not_applicable",
               is_foreign=False, atm_network="not_applicable", atm_operator_surcharge=0.0,
               hold_type="not_applicable", card_fee_type="not_applicable", source_txn_id=card_txn_id)
    return str({"outcome_record_id": oid, "credit_entry_id": cid, "card_txn_id": card_txn_id,
                "resolution": "approved", "resolution_date": today, "credit_amount": amount})


@tool(owner="user", rw="write")
def file_incorrect_amount_card_dispute_a0bf950b(ctx: ToolContext, card_id: str, card_txn_id: str,
                                                dispute_amount: float) -> str:
    """The cardholder files, in their own name, a merchant dispute of the reason incorrect_amount on one
    settled purchase of one of their Pocketwire Visa debit cards, asserting that the merchant settled
    more than was agreed. One call opens exactly one dispute record on that purchase with today's filing
    date, the disputed amount given, no customer liability, the outcome pending and no provisional credit
    posted. The cardholder then sees the dispute as open (pending) on that purchase in the app; no money
    moves on this call.

    Args:
        card_id: Id class — the reference number of the debit card the purchase was made on, as shown by
            the debit card lookup for this cardholder.
        card_txn_id: Id class — the reference number of the settled purchase being disputed, as shown by
            the card activity lookup for that card.
        dispute_amount: Fixed-format class — the amount disputed, in USD, a non-negative number with 2
            decimal places (to the cent), never more than the purchase amount.

    Returns:
        A dictionary receipt: dispute_record_id (string, the reference number of the new dispute record),
        card_id (string, the card), card_txn_id (string, the disputed purchase), dispute_reason (string,
        always incorrect_amount), reported_date (string, YYYY-MM-DD, the filing date), dispute_amount
        (number, USD with 2 decimal places) and resolution (string, always pending). A receipt carrying
        resolution pending means the dispute is open.
    """
    amount = round(float(dispute_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("cdsp_", card_id, card_txn_id, "incorrect_amount", amount)
    card = ctx.find("card_accounts", card_id=card_id)
    customer_id = card[0].get("customer_id") if card else ""
    ctx.create("card_disputes", rid, card_dispute_id=rid, card_id=card_id, customer_id=customer_id,
               event_type="card_dispute_filed", card_txn_id=card_txn_id, dispute_reason="incorrect_amount",
               reported_date=today, dispute_amount=amount, customer_liability=0.0,
               resolution="pending", resolution_date="", provisional_credit_posted=False)
    return str({"dispute_record_id": rid, "card_id": card_id, "card_txn_id": card_txn_id,
                "dispute_reason": "incorrect_amount", "reported_date": today, "dispute_amount": amount,
                "resolution": "pending"})


@tool(owner="agent", rw="write")
def post_on_filing_dispute_credit_86bd6080(ctx: ToolContext, card_id: str, card_txn_id: str,
                                           credit_amount: float) -> str:
    """Books the credit given on filing for an open merchant dispute of a purchase on a Pocketwire Visa
    debit card. One call credits the given amount to the card's settlement balance as a dispute credit
    linked to the disputed purchase; the dispute itself stays open for the part not credited. The
    cardholder sees the credit on the card's activity next to the disputed purchase.

    Args:
        card_id: Id class — the reference number of the debit card the disputed purchase was made on, as
            shown by the debit card lookup for this cardholder.
        card_txn_id: Id class — the reference number of the disputed purchase, as shown by the card
            activity lookup or the dispute lookup for that card.
        credit_amount: Fixed-format class — the amount credited to the card, in USD, a non-negative number
            with 2 decimal places (to the cent).

    Returns:
        A dictionary receipt: credit_entry_id (string, the reference number of the credit on the card's
        activity), card_txn_id (string, the disputed purchase), txn_date (string, YYYY-MM-DD, the booking
        date) and credit_amount (number, USD with 2 decimal places). A receipt with a credit_entry_id
        means the credit is on the card.
    """
    amount = round(float(credit_amount), 2)
    today = ctx.now()[:10]
    card = ctx.find("card_accounts", card_id=card_id)
    customer_id = card[0].get("customer_id") if card else ""
    cid = ctx.make_id("ctxn_", card_id, card_txn_id, "card_dispute_credit", amount)
    ctx.create("card_transactions", cid, card_txn_id=cid, card_id=card_id, customer_id=customer_id,
               event_type="card_dispute_credit", txn_reference="", txn_date=today, amount=amount,
               merchant_name="", merchant_category="not_applicable", entry_mode="not_applicable",
               is_foreign=False, atm_network="not_applicable", atm_operator_surcharge=0.0,
               hold_type="not_applicable", card_fee_type="not_applicable", source_txn_id=card_txn_id)
    return str({"credit_entry_id": cid, "card_txn_id": card_txn_id, "txn_date": today,
                "credit_amount": amount})

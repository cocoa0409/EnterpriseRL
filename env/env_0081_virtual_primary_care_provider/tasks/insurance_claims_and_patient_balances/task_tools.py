"""Hidden task tools of the insurance_claims_and_patient_balances difficulty (claim category)."""
from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _Money:
    @staticmethod
    def cents(value):
        """Exact half-up rounding of a USD figure to the cent."""
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def claim_row(ctx, claim_id):
        """The insurance claim record named by the reference number, or None."""
        rows = ctx.find("insurance_claims", claim_id=claim_id)
        return rows[0] if rows else None


@tool(owner="agent", rw="write")
def post_small_balance_writeoff_bfef4ea9(ctx: ToolContext, claim_id: str, writeoff_amount: float) -> str:
    """Write off the remaining patient balance of one insurance claim as a small balance. One call books a single
    write-off entry on that claim's patient balance, under the coverage and visit the claim belongs to, dated today;
    the entry reduces what the patient owes on the claim by the amount written off, so the patient will not be billed
    or sent a statement for that amount. The patient can see the write-off on the claim's balance history.

    Args:
        claim_id: Id class — the reference number of the insurance claim whose balance is written off, as shown by the claim or statement lookup for this patient.
        writeoff_amount: Fixed-format class — the balance being written off, in USD as a positive number with exactly 2 decimal places (cents), rounded half up to the cent; the entry is booked as the negative of this amount.

    Returns:
        A text receipt of a dict with: balance_entry_id (string, the new write-off entry's reference number),
        claim_id (string, the claim written off), amount (number, USD, the signed entry amount, negative),
        entry_date (string, YYYY-MM-DD, today's date), status (string, the literal "written_off" on success).
        A text starting with "Error:" means the claim reference was not found and nothing was booked.
    """
    claim = _Money.claim_row(ctx, claim_id)
    if claim is None:
        return f"Error: no insurance claim {claim_id}."
    amt = _Money.cents(writeoff_amount)
    rid = ctx.make_id("pbe_", "wo", claim_id, amt)
    ctx.create("patient_balance_entries", rid, balance_entry_id=rid, coverage_id=claim["coverage_id"],
               customer_id=claim["customer_id"], event_type="claim_small_balance_written_off", claim_id=claim_id,
               visit_id=claim["visit_id"], amount=-amt, entry_date=ctx.now()[:10], source_entry_id="")
    return str({"balance_entry_id": rid, "claim_id": claim_id, "amount": -amt, "entry_date": ctx.now()[:10],
                "status": "written_off"})


@tool(owner="agent", rw="write")
def transfer_claim_credit_12a8a2c0(ctx: ToolContext, claim_id: str, to_claim_id: str, transfer_amount: float) -> str:
    """Move credit the patient holds on one insurance claim onto the open balance of another of the patient's claims.
    One call books a matching pair of entries dated today: a transfer entry on the claim that holds the credit, which
    uses up that much of its credit, and a received entry on the claim being paid, which lowers what the patient owes
    there by the same amount and names the transfer entry it came from. The patient sees the credit leave one claim
    and reduce the balance of the other.

    Args:
        claim_id: Id class — the reference number of the insurance claim that holds the credit, as shown by the claim or balance lookup for this patient.
        to_claim_id: Id class — the reference number of the insurance claim whose open balance receives the credit, as shown by the claim or statement lookup for this patient.
        transfer_amount: Fixed-format class — the credit moved, in USD as a positive number with exactly 2 decimal places (cents), rounded half up to the cent.

    Returns:
        A text receipt of a dict with: transfer_entry_id (string, the entry on the crediting claim), received_entry_id
        (string, the entry on the claim paid), claim_id and to_claim_id (strings, as passed), amount (number, USD,
        the positive amount moved), entry_date (string, YYYY-MM-DD, today), status (string, the literal "transferred").
        A text starting with "Error:" means a claim reference was not found and nothing was booked.
    """
    src = _Money.claim_row(ctx, claim_id)
    dst = _Money.claim_row(ctx, to_claim_id)
    if src is None or dst is None:
        return f"Error: claim reference not found ({claim_id}, {to_claim_id})."
    amt = _Money.cents(transfer_amount)
    day = ctx.now()[:10]
    tid = ctx.make_id("pbe_", "xfer", claim_id, to_claim_id, amt)
    ctx.create("patient_balance_entries", tid, balance_entry_id=tid, coverage_id=src["coverage_id"],
               customer_id=src["customer_id"], event_type="claim_credit_transferred", claim_id=claim_id,
               visit_id=src["visit_id"], amount=amt, entry_date=day, source_entry_id="")
    rid = ctx.make_id("pbe_", "rcv", claim_id, to_claim_id, amt)
    ctx.create("patient_balance_entries", rid, balance_entry_id=rid, coverage_id=dst["coverage_id"],
               customer_id=dst["customer_id"], event_type="claim_credit_received", claim_id=to_claim_id,
               visit_id=dst["visit_id"], amount=-amt, entry_date=day, source_entry_id=tid)
    return str({"transfer_entry_id": tid, "received_entry_id": rid, "claim_id": claim_id,
                "to_claim_id": to_claim_id, "amount": amt, "entry_date": day, "status": "transferred"})


@tool(owner="user", rw="write")
def post_rebill_balance_payment_9bd5f69d(ctx: ToolContext, claim_id: str, payment_amount: float, discount_amount: float) -> str:
    """The patient pays, with a card they read out themselves, the self-pay balance of one of their insurance claims
    in full. One call books the patient's payment entry on that claim's balance dated today and, when a prompt-pay
    discount accompanies the payment, a discount entry on the same claim; together they clear the balance paid. The
    patient sees the payment and any discount on the claim and a confirmation reference.

    Args:
        claim_id: Id class — the reference number of the insurance claim being paid, as quoted to the patient by the agent from the claim or statement lookup.
        payment_amount: Fixed-format class — the amount the patient pays, in USD as a positive number with exactly 2 decimal places (cents), rounded half up to the cent.
        discount_amount: Fixed-format class — the prompt-pay discount posted with the payment, in USD as a positive number with exactly 2 decimal places (cents), rounded half up to the cent; 0.00 when no discount accompanies the payment.

    Returns:
        A text receipt of a dict with: payment_entry_id (string, the payment entry), discount_entry_id (string, the
        discount entry, empty when the discount is 0.00), claim_id (string), payment (number, USD, positive amount
        paid), discount (number, USD, positive discount), entry_date (string, YYYY-MM-DD, today), confirmation
        (string, the payment confirmation reference, equal to payment_entry_id), status (string, the literal "paid").
        A text starting with "Error:" means the claim reference was not found and nothing was booked.
    """
    claim = _Money.claim_row(ctx, claim_id)
    if claim is None:
        return f"Error: no insurance claim {claim_id}."
    pay = _Money.cents(payment_amount)
    disc = _Money.cents(discount_amount)
    day = ctx.now()[:10]
    pid = ctx.make_id("pbe_", "pay", claim_id, pay, disc)
    ctx.create("patient_balance_entries", pid, balance_entry_id=pid, coverage_id=claim["coverage_id"],
               customer_id=claim["customer_id"], event_type="claim_patient_payment_posted", claim_id=claim_id,
               visit_id=claim["visit_id"], amount=-pay, entry_date=day, source_entry_id="")
    did = ""
    if disc > 0:
        did = ctx.make_id("pbe_", "ppd", claim_id, pay, disc)
        ctx.create("patient_balance_entries", did, balance_entry_id=did, coverage_id=claim["coverage_id"],
                   customer_id=claim["customer_id"], event_type="claim_prompt_pay_discount_applied", claim_id=claim_id,
                   visit_id=claim["visit_id"], amount=-disc, entry_date=day, source_entry_id="")
    return str({"payment_entry_id": pid, "discount_entry_id": did, "claim_id": claim_id, "payment": pay,
                "discount": disc, "entry_date": day, "confirmation": pid, "status": "paid"})


@tool(owner="agent", rw="write")
def apply_booking_collection_b81aee5f(ctx: ToolContext, claim_id: str, collection_amount: float) -> str:
    """Apply what the patient paid at booking for a visit against the patient balance of that visit's insurance
    claim. One call books a single time-of-service entry on the claim dated today, which lowers what the patient owes
    on the claim by the amount applied; the patient sees the booking payment credited on the claim.

    Args:
        claim_id: Id class — the reference number of the insurance claim the booking payment is applied to, as shown by the claim lookup for this patient.
        collection_amount: Fixed-format class — the booking payment applied, in USD as a positive number with exactly 2 decimal places (cents), rounded half up to the cent; the entry is booked as the negative of this amount.

    Returns:
        A text receipt of a dict with: balance_entry_id (string, the new entry), claim_id (string), amount (number,
        USD, the signed entry amount, negative), entry_date (string, YYYY-MM-DD, today), status (string, the literal
        "applied"). A text starting with "Error:" means the claim reference was not found and nothing was booked.
    """
    claim = _Money.claim_row(ctx, claim_id)
    if claim is None:
        return f"Error: no insurance claim {claim_id}."
    amt = _Money.cents(collection_amount)
    rid = ctx.make_id("pbe_", "tos", claim_id, amt)
    ctx.create("patient_balance_entries", rid, balance_entry_id=rid, coverage_id=claim["coverage_id"],
               customer_id=claim["customer_id"], event_type="claim_time_of_service_applied", claim_id=claim_id,
               visit_id=claim["visit_id"], amount=-amt, entry_date=ctx.now()[:10], source_entry_id="")
    return str({"balance_entry_id": rid, "claim_id": claim_id, "amount": -amt, "entry_date": ctx.now()[:10],
                "status": "applied"})


@tool(owner="user", rw="write")
def post_cost_share_payment_1adf649d(ctx: ToolContext, claim_id: str, payment_amount: float) -> str:
    """The patient pays, with a card they read out themselves, their insured cost-share balance on one of their
    insurance claims. One call books the patient's payment entry on that claim's balance dated today, lowering what
    the patient owes on the claim by the amount paid; the patient sees the payment on the claim and a confirmation
    reference.

    Args:
        claim_id: Id class — the reference number of the insurance claim being paid, as quoted to the patient by the agent from the claim or statement lookup.
        payment_amount: Fixed-format class — the amount the patient pays, in USD as a positive number with exactly 2 decimal places (cents), rounded half up to the cent.

    Returns:
        A text receipt of a dict with: payment_entry_id (string, the payment entry), claim_id (string), payment
        (number, USD, positive amount paid), entry_date (string, YYYY-MM-DD, today), confirmation (string, the payment
        confirmation reference, equal to payment_entry_id), status (string, the literal "paid"). A text starting with
        "Error:" means the claim reference was not found and nothing was booked.
    """
    claim = _Money.claim_row(ctx, claim_id)
    if claim is None:
        return f"Error: no insurance claim {claim_id}."
    pay = _Money.cents(payment_amount)
    day = ctx.now()[:10]
    pid = ctx.make_id("pbe_", "pay", claim_id, pay)
    ctx.create("patient_balance_entries", pid, balance_entry_id=pid, coverage_id=claim["coverage_id"],
               customer_id=claim["customer_id"], event_type="claim_patient_payment_posted", claim_id=claim_id,
               visit_id=claim["visit_id"], amount=-pay, entry_date=day, source_entry_id="")
    return str({"payment_entry_id": pid, "claim_id": claim_id, "payment": pay, "entry_date": day,
                "confirmation": pid, "status": "paid"})

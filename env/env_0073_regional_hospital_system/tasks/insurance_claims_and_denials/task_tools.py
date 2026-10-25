"""Hidden task tools — insurance_claims_and_denials (Riverbend Regional Health, Insurance Claim category).

Every tool performs one atomic posting on one insurance claim and returns a receipt. No tool checks a policy
condition, an eligibility, a prerequisite or a computed figure: the figure passed in is posted as given.
"""

from erlbench import ToolContext, tool


class _Claims:
    @staticmethod
    def get(ctx: ToolContext, claim_id: str) -> dict:
        rows = ctx.find("insurance_claims", claim_id=claim_id)
        return rows[0] if rows else {}

    @staticmethod
    def oldest_payment(ctx: ToolContext, claim_id: str) -> dict:
        rows = ctx.find("claim_transactions", claim_id=claim_id, event_type="claim_payment_posted")
        rows = sorted(rows, key=lambda r: (str(r.get("posting_date", "")), str(r.get("remit_trace_number", ""))))
        return rows[0] if rows else {}


@tool(owner="agent", rw="write")
def refund_surgery_claim_payment_239964f7(ctx: ToolContext, claim_id: str, amount_usd: float) -> str:
    """Record, on one insurance claim, the payer's recovery of a payment it made on the claim, refunded to the payer
    by Riverbend. One call books one payer recovery entry on the claim with the reason code WO-72, recorded against
    the payer remittance that carried the claim's payer payment with the smallest posting date (equal dates: the
    smallest remittance trace number); that remittance's trace number and date are copied onto the entry. The entry
    is dated today and raises the amount still expected from the payer on that claim by the same figure. What the patient owes does not change. The claim's status does not change. Success is the receipt below
    naming the new entry.

    Args:
        claim_id: Id class — the reference number of the insurance claim whose payment the payer is recovering, as
            shown by the claim lookup for the patient.
        amount_usd: Fixed-format class — the amount refunded to the payer, in USD, 2 decimal places, positive
            magnitude, already rounded to the cent by the caller; the tool posts it exactly as given.

    Returns:
        A text receipt: "Recovery <entry_id> posted on claim <claim_id>: <amount_usd> USD, reason code WO-72, against
        remittance <remit_trace_number>; amount still expected from the payer <payer_balance> USD." entry_id is the
        reference of the new claim activity entry; remit_trace_number is the trace number of the remittance that
        carried the claim's payer payment with the smallest posting date (empty when the claim has no payment); payer_balance is the new amount still expected
        from the payer, USD with 2 decimal places. The receipt appearing is the success signal.
    """
    claim = _Claims.get(ctx, claim_id)
    pay0 = _Claims.oldest_payment(ctx, claim_id)
    trace = pay0.get("remit_trace_number", "")
    rdate = pay0.get("remit_date", "")
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("ctb_", claim_id, "WO-72", amount_usd)
    ctx.create("claim_transactions", rid, claim_txn_id=rid, claim_id=claim_id, customer_id=claim.get("customer_id", ""),
               event_type="claim_takeback", posting_date=ctx.now()[:10], amount=amount, remit_trace_number=trace,
               remit_date=rdate, carc_code="WO-72", correction_seq=0, correction_reason="", writeoff_reason="",
               appeal_level=0, appeal_type="")
    balance = round(float(claim.get("payer_balance") or 0) + amount, 2)
    ctx.update("insurance_claims", claim_id, payer_balance=balance)
    return (f"Recovery {rid} posted on claim {claim_id}: {amount:.2f} USD, reason code WO-72, against remittance "
            f"{trace}; amount still expected from the payer {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def write_off_surgery_small_items_d7ad9b50(ctx: ToolContext, claim_id: str, amount_usd: float) -> str:
    """Write off, on one denied insurance claim, the value of small items on Riverbend's outpatient-surgery small-item list that are too small to carry into
    any further appeal. One call books one write-off entry on the claim
    with the write-off reason BELOW_APPEAL_THRESHOLD and the claim's current denial reason code, dated today, and lowers the
    amount still expected from the payer on that claim by the same figure. The patient is never billed for it. The
    claim's status does not change. Success is the receipt below naming the new entry.

    Args:
        claim_id: Id class — the reference number of the insurance claim whose small items are written off, as shown by
            the claim lookup for the patient.
        amount_usd: Fixed-format class — the value being written off, in USD, 2 decimal places, positive magnitude,
            already rounded to the cent by the caller; the tool posts it exactly as given.

    Returns:
        A text receipt: "Write-off <entry_id> posted on claim <claim_id>: <amount_usd> USD, reason
        BELOW_APPEAL_THRESHOLD, denial code <carc_code>; amount still expected from the payer <payer_balance> USD."
        entry_id is the reference of the new claim activity entry; carc_code is the claim's denial reason code copied
        onto the entry; payer_balance is the new amount still expected from the payer, USD with 2
        decimal places. The receipt appearing is the success signal.
    """
    claim = _Claims.get(ctx, claim_id)
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("cwo_", claim_id, "BELOW_APPEAL_THRESHOLD", amount_usd)
    ctx.create("claim_transactions", rid, claim_txn_id=rid, claim_id=claim_id, customer_id=claim.get("customer_id", ""),
               event_type="claim_denial_written_off", posting_date=ctx.now()[:10], amount=amount,
               remit_trace_number="", remit_date="", carc_code=claim.get("denial_carc", ""), correction_seq=0,
               correction_reason="", writeoff_reason="BELOW_APPEAL_THRESHOLD", appeal_level=0, appeal_type="")
    balance = round(float(claim.get("payer_balance") or 0) - amount, 2)
    ctx.update("insurance_claims", claim_id, payer_balance=balance)
    return (f"Write-off {rid} posted on claim {claim_id}: {amount:.2f} USD, reason BELOW_APPEAL_THRESHOLD, "
            f"denial code {claim.get('denial_carc', '')}; amount still expected from the payer {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def write_off_noncovered_convenience_item_58e216c4(ctx: ToolContext, claim_id: str, amount_usd: float) -> str:
    """Write off, on one denied insurance claim, the value of take-home convenience items that no payer covers and
    for which no advance financial-responsibility waiver is on file. One call books one write-off entry on the claim
    with the write-off reason NONCOVERED_NO_WAIVER and the claim's current denial reason code, dated today, and
    lowers the amount still expected from the payer on that claim by the same figure. The patient is never billed
    for it. The claim's status does not change. Success is the receipt below naming the new entry.

    Args:
        claim_id: Id class — the reference number of the insurance claim whose convenience items are written off, as
            shown by the claim lookup for the patient.
        amount_usd: Fixed-format class — the convenience-item value being written off, in USD, 2 decimal places,
            positive magnitude, already rounded to the cent by the caller; the tool posts it exactly as given.

    Returns:
        A text receipt: "Write-off <entry_id> posted on claim <claim_id>: <amount_usd> USD, reason
        NONCOVERED_NO_WAIVER, denial code <carc_code>; amount still expected from the payer <payer_balance> USD."
        entry_id is the reference of the new claim activity entry; carc_code is the claim's denial reason code copied
        onto the entry; payer_balance is the new amount still expected from the payer, USD with 2
        decimal places. The receipt appearing is the success signal.
    """
    claim = _Claims.get(ctx, claim_id)
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("cwo_", claim_id, "NONCOVERED_NO_WAIVER", amount_usd)
    ctx.create("claim_transactions", rid, claim_txn_id=rid, claim_id=claim_id, customer_id=claim.get("customer_id", ""),
               event_type="claim_denial_written_off", posting_date=ctx.now()[:10], amount=amount,
               remit_trace_number="", remit_date="", carc_code=claim.get("denial_carc", ""), correction_seq=0,
               correction_reason="", writeoff_reason="NONCOVERED_NO_WAIVER", appeal_level=0, appeal_type="")
    balance = round(float(claim.get("payer_balance") or 0) - amount, 2)
    ctx.update("insurance_claims", claim_id, payer_balance=balance)
    return (f"Write-off {rid} posted on claim {claim_id}: {amount:.2f} USD, reason NONCOVERED_NO_WAIVER, "
            f"denial code {claim.get('denial_carc', '')}; amount still expected from the payer {balance:.2f} USD.")


@tool(owner="user", rw="write")
def close_denial_on_member_decision_7cc13d5d(ctx: ToolContext, claim_id: str, amount_usd: float) -> str:
    """Record, as the patient, your own decision not to pursue a member-level appeal of a denied insurance claim, so
    that Riverbend closes the denial without billing you. One call books one write-off entry on the claim with the
    write-off reason APPEALS_EXHAUSTED and the claim's current denial reason code, dated today, for the figure the
    representative gave you, and lowers the amount still expected from the payer on that claim by the same figure.
    You are never billed for it. The claim's status does not change. Success is the receipt below naming the new
    entry.

    Args:
        claim_id: Id class — the reference number of your insurance claim that the representative read to you from
            the claim lookup.
        amount_usd: Fixed-format class — the figure the representative told you Riverbend is closing on your
            decision, in USD, 2 decimal places, positive magnitude, already rounded to the cent; it is posted exactly
            as given.

    Returns:
        A text receipt: "Decision recorded. Write-off <entry_id> posted on claim <claim_id>: <amount_usd> USD, reason
        APPEALS_EXHAUSTED, denial code <carc_code>; amount still expected from the payer <payer_balance> USD."
        entry_id is the reference of the new claim activity entry; carc_code is the claim's denial reason code copied
        onto the entry; payer_balance is the new amount still expected from the payer, USD with 2
        decimal places. The receipt appearing is the success signal.
    """
    claim = _Claims.get(ctx, claim_id)
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("cwo_", claim_id, "APPEALS_EXHAUSTED", amount_usd)
    ctx.create("claim_transactions", rid, claim_txn_id=rid, claim_id=claim_id, customer_id=claim.get("customer_id", ""),
               event_type="claim_denial_written_off", posting_date=ctx.now()[:10], amount=amount,
               remit_trace_number="", remit_date="", carc_code=claim.get("denial_carc", ""), correction_seq=0,
               correction_reason="", writeoff_reason="APPEALS_EXHAUSTED", appeal_level=0, appeal_type="")
    balance = round(float(claim.get("payer_balance") or 0) - amount, 2)
    ctx.update("insurance_claims", claim_id, payer_balance=balance)
    return (f"Decision recorded. Write-off {rid} posted on claim {claim_id}: {amount:.2f} USD, reason "
            f"APPEALS_EXHAUSTED, denial code {claim.get('denial_carc', '')}; amount still expected from the payer "
            f"{balance:.2f} USD.")


@tool(owner="agent", rw="write")
def refund_payer_recovery_9b1903be(ctx: ToolContext, claim_id: str, amount_usd: float) -> str:
    """Record, on one insurance claim, the payer's recovery of a payment it made on the claim, refunded to the payer
    by Riverbend. One call books one payer recovery entry on the claim with the reason code WO-72, recorded against
    the payer remittance that carried the claim's payer payment with the smallest posting date (equal dates: the
    smallest remittance trace number); that remittance's trace number and date are copied onto the entry. The entry
    is dated today and raises the amount still expected from the payer on that claim by the same figure. What the patient owes does not change. The claim's status does not change. Success is the receipt below
    naming the new entry.

    Args:
        claim_id: Id class — the reference number of the insurance claim whose payment the payer is recovering, as
            shown by the claim lookup for the patient.
        amount_usd: Fixed-format class — the amount refunded to the payer, in USD, 2 decimal places, positive
            magnitude, already rounded to the cent by the caller; the tool posts it exactly as given.

    Returns:
        A text receipt: "Recovery <entry_id> posted on claim <claim_id>: <amount_usd> USD, reason code WO-72, against
        remittance <remit_trace_number>; amount still expected from the payer <payer_balance> USD." entry_id is the
        reference of the new claim activity entry; remit_trace_number is the trace number of the remittance that
        carried the claim's payer payment with the smallest posting date (empty when the claim has no payment); payer_balance is the new amount still expected
        from the payer, USD with 2 decimal places. The receipt appearing is the success signal.
    """
    claim = _Claims.get(ctx, claim_id)
    pay0 = _Claims.oldest_payment(ctx, claim_id)
    trace = pay0.get("remit_trace_number", "")
    rdate = pay0.get("remit_date", "")
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("ctb_", claim_id, "WO-72", amount_usd)
    ctx.create("claim_transactions", rid, claim_txn_id=rid, claim_id=claim_id, customer_id=claim.get("customer_id", ""),
               event_type="claim_takeback", posting_date=ctx.now()[:10], amount=amount, remit_trace_number=trace,
               remit_date=rdate, carc_code="WO-72", correction_seq=0, correction_reason="", writeoff_reason="",
               appeal_level=0, appeal_type="")
    balance = round(float(claim.get("payer_balance") or 0) + amount, 2)
    ctx.update("insurance_claims", claim_id, payer_balance=balance)
    return (f"Recovery {rid} posted on claim {claim_id}: {amount:.2f} USD, reason code WO-72, against remittance "
            f"{trace}; amount still expected from the payer {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def write_off_observation_small_items_ab2aa651(ctx: ToolContext, claim_id: str, amount_usd: float) -> str:
    """Write off, on one denied insurance claim, the value of small items on Riverbend's observation and emergency small-item list that are too small to
    carry into any further appeal. One call books one write-off entry on the claim
    with the write-off reason BELOW_APPEAL_THRESHOLD and the claim's current denial reason code, dated today, and lowers the
    amount still expected from the payer on that claim by the same figure. The patient is never billed for it. The
    claim's status does not change. Success is the receipt below naming the new entry.

    Args:
        claim_id: Id class — the reference number of the insurance claim whose small items are written off, as shown by
            the claim lookup for the patient.
        amount_usd: Fixed-format class — the value being written off, in USD, 2 decimal places, positive magnitude,
            already rounded to the cent by the caller; the tool posts it exactly as given.

    Returns:
        A text receipt: "Write-off <entry_id> posted on claim <claim_id>: <amount_usd> USD, reason
        BELOW_APPEAL_THRESHOLD, denial code <carc_code>; amount still expected from the payer <payer_balance> USD."
        entry_id is the reference of the new claim activity entry; carc_code is the claim's denial reason code copied
        onto the entry; payer_balance is the new amount still expected from the payer, USD with 2
        decimal places. The receipt appearing is the success signal.
    """
    claim = _Claims.get(ctx, claim_id)
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("cwo_", claim_id, "BELOW_APPEAL_THRESHOLD", amount_usd)
    ctx.create("claim_transactions", rid, claim_txn_id=rid, claim_id=claim_id, customer_id=claim.get("customer_id", ""),
               event_type="claim_denial_written_off", posting_date=ctx.now()[:10], amount=amount,
               remit_trace_number="", remit_date="", carc_code=claim.get("denial_carc", ""), correction_seq=0,
               correction_reason="", writeoff_reason="BELOW_APPEAL_THRESHOLD", appeal_level=0, appeal_type="")
    balance = round(float(claim.get("payer_balance") or 0) - amount, 2)
    ctx.update("insurance_claims", claim_id, payer_balance=balance)
    return (f"Write-off {rid} posted on claim {claim_id}: {amount:.2f} USD, reason BELOW_APPEAL_THRESHOLD, "
            f"denial code {claim.get('denial_carc', '')}; amount still expected from the payer {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def write_off_self_administered_drugs_664aab61(ctx: ToolContext, claim_id: str, amount_usd: float) -> str:
    """Write off, on one insurance claim, the value of self-administered drugs that no payer covers on an outpatient
    claim and for which no advance financial-responsibility waiver is on file. One call books one write-off entry on
    the claim with the write-off reason NONCOVERED_NO_WAIVER and the claim's current denial reason code, dated today,
    and lowers the amount still expected from the payer on that claim by the same figure. The patient is never billed
    for it. The claim's status does not change. Success is the receipt below naming the new entry.

    Args:
        claim_id: Id class — the reference number of the insurance claim whose self-administered drugs are written
            off, as shown by the claim lookup for the patient.
        amount_usd: Fixed-format class — the self-administered drug value being written off, in USD, 2 decimal
            places, positive magnitude, already rounded to the cent by the caller; the tool posts it exactly as given.

    Returns:
        A text receipt: "Write-off <entry_id> posted on claim <claim_id>: <amount_usd> USD, reason
        NONCOVERED_NO_WAIVER, denial code <carc_code>; amount still expected from the payer <payer_balance> USD."
        entry_id is the reference of the new claim activity entry; carc_code is the claim's denial reason code copied
        onto the entry; payer_balance is the new amount still expected from the payer, USD with 2
        decimal places. The receipt appearing is the success signal.
    """
    claim = _Claims.get(ctx, claim_id)
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("cwo_", claim_id, "NONCOVERED_NO_WAIVER", amount_usd)
    ctx.create("claim_transactions", rid, claim_txn_id=rid, claim_id=claim_id, customer_id=claim.get("customer_id", ""),
               event_type="claim_denial_written_off", posting_date=ctx.now()[:10], amount=amount,
               remit_trace_number="", remit_date="", carc_code=claim.get("denial_carc", ""), correction_seq=0,
               correction_reason="", writeoff_reason="NONCOVERED_NO_WAIVER", appeal_level=0, appeal_type="")
    balance = round(float(claim.get("payer_balance") or 0) - amount, 2)
    ctx.update("insurance_claims", claim_id, payer_balance=balance)
    return (f"Write-off {rid} posted on claim {claim_id}: {amount:.2f} USD, reason NONCOVERED_NO_WAIVER, "
            f"denial code {claim.get('denial_carc', '')}; amount still expected from the payer {balance:.2f} USD.")


@tool(owner="user", rw="write")
def close_denial_on_external_review_decision_5747d436(ctx: ToolContext, claim_id: str, amount_usd: float) -> str:
    """Record, as the patient, your own decision not to request an independent external review of a denied insurance
    claim, so that Riverbend closes the denial without billing you. One call books one write-off entry on the claim
    with the write-off reason APPEALS_EXHAUSTED and the claim's current denial reason code, dated today, for the
    figure the representative gave you, and lowers the amount still expected from the payer on that claim by the same
    figure. You are never billed for it. The claim's status does not change. Success is the receipt below naming the
    new entry.

    Args:
        claim_id: Id class — the reference number of your insurance claim that the representative read to you from
            the claim lookup.
        amount_usd: Fixed-format class — the figure the representative told you Riverbend is closing on your
            decision, in USD, 2 decimal places, positive magnitude, already rounded to the cent; it is posted exactly
            as given.

    Returns:
        A text receipt: "Decision recorded. Write-off <entry_id> posted on claim <claim_id>: <amount_usd> USD, reason
        APPEALS_EXHAUSTED, denial code <carc_code>; amount still expected from the payer <payer_balance> USD."
        entry_id is the reference of the new claim activity entry; carc_code is the claim's denial reason code copied
        onto the entry; payer_balance is the new amount still expected from the payer, USD with 2
        decimal places. The receipt appearing is the success signal.
    """
    claim = _Claims.get(ctx, claim_id)
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("cwo_", claim_id, "APPEALS_EXHAUSTED", amount_usd)
    ctx.create("claim_transactions", rid, claim_txn_id=rid, claim_id=claim_id, customer_id=claim.get("customer_id", ""),
               event_type="claim_denial_written_off", posting_date=ctx.now()[:10], amount=amount,
               remit_trace_number="", remit_date="", carc_code=claim.get("denial_carc", ""), correction_seq=0,
               correction_reason="", writeoff_reason="APPEALS_EXHAUSTED", appeal_level=0, appeal_type="")
    balance = round(float(claim.get("payer_balance") or 0) - amount, 2)
    ctx.update("insurance_claims", claim_id, payer_balance=balance)
    return (f"Decision recorded. Write-off {rid} posted on claim {claim_id}: {amount:.2f} USD, reason "
            f"APPEALS_EXHAUSTED, denial code {claim.get('denial_carc', '')}; amount still expected from the payer "
            f"{balance:.2f} USD.")

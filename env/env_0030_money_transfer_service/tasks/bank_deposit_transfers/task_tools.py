"""Hidden task tools for difficulty bank_deposit_transfers (env_0030_money_transfer_service).

Each tool is named by exactly one extended policy's target_tool in bank.extended.yaml and is reached
only through the unlock_* -> call_* meta-tools. Every tool performs one atomic business write with the
values it is given; none of them checks a policy condition, works out an amount or refuses a call.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def refund_late_delivery_fee_f06ff624(ctx: ToolContext, bank_transfer_id: str, related_entry_id: str,
                                      refund_amount_usd: float) -> str:
    """Refund part or all of the transfer fee on a Bank Deposit transfer that reached the recipient
    later than its promised date of availability, as Paloma's on-time promise refund.

    One call books one fee refund with the reason late delivery against one fee charge on the
    transfer's money movements, dated today, and lowers the fees Paloma holds on that transfer by the
    amount refunded. The money goes back to the customer's original payment method; the refund then
    shows on the transfer's money movements and the transfer's held fees drop by the same amount.

    Args:
        bank_transfer_id: Id class — the reference number of the Bank Deposit transfer whose transfer
            fee is being refunded, as returned by the Bank Deposit transfer lookup for this customer.
        related_entry_id: Id class — the reference number of the money movement that charged the
            transfer fee being refunded, as returned by the Bank Deposit money-movement lookup for that
            transfer.
        refund_amount_usd: Fixed-format class — the amount of the transfer fee refunded, in USD, given
            with 2 decimal places (cents) as a positive number; it is recorded exactly as passed after
            rounding half up to 2 decimal places.

    Returns:
        A dictionary rendered as text with: ledger_entry_id (the reference number of the new fee
        refund movement), bank_transfer_id (the transfer refunded), refunded_usd (the amount refunded,
        USD with 2 decimal places), fee_refund_reason (always late_delivery), entry_date (the refund
        date, YYYY-MM-DD), fees_held_usd (the fees Paloma still holds on the transfer afterwards, USD
        with 2 decimal places) and status (refunded when the refund was booked).
    """
    amount = round(float(refund_amount_usd), 2)
    rows = ctx.find("bank_transfers", bank_transfer_id=bank_transfer_id)
    transfer = rows[0] if rows else {}
    today = ctx.now()[:10]
    rid = ctx.make_id("bkl_", bank_transfer_id, related_entry_id, refund_amount_usd)
    ctx.create("bank_ledger", rid, ledger_entry_id=rid, bank_transfer_id=bank_transfer_id,
               customer_id=transfer.get("customer_id", ""), event_type="bank_fee_refunded",
               entry_date=today, amount_usd=amount, fee_type="none",
               fee_refund_reason="late_delivery", payout_attempt=0, receive_amount="",
               fx_rate_applied="", return_reason="none", refund_basis="none",
               credit_reason="none", related_entry_id=related_entry_id)
    held = round(float(transfer.get("fees_held_usd") or 0) - amount, 2)
    ctx.update("bank_transfers", bank_transfer_id, fees_held_usd=held)
    return str({"ledger_entry_id": rid, "bank_transfer_id": bank_transfer_id, "refunded_usd": amount,
                "fee_refund_reason": "late_delivery", "entry_date": today, "fees_held_usd": held,
                "status": "refunded"})


@tool(owner="user", rw="write")
def request_transfer_recall_f96dc6b4(ctx: ToolContext, bank_transfer_id: str, payout_attempt: int,
                                     recall_fee_usd: float) -> str:
    """Ask Paloma to recall a Bank Deposit payment that was credited to account details the customer
    gave by mistake, and accept the recall fee for it.

    One call opens a recall request on the transfer's case file, dated today and open until the
    beneficiary bank answers, and collects the recall fee as a fee charge on the transfer's money
    movements against the payout being recalled; the fees Paloma holds on the transfer rise by that
    fee. The customer sees the open recall request and the fee charged on the transfer. Paloma cannot
    compel the beneficiary bank, so the request does not guarantee the money comes back.

    Args:
        bank_transfer_id: Id class — the reference number of the Bank Deposit transfer to recall, as
            the support agent reads it out from the transfer record.
        payout_attempt: Fixed-format class — the attempt number of the payout being recalled, an
            integer count starting at 1, as the support agent reads it from the transfer's payouts.
        recall_fee_usd: Fixed-format class — the recall fee the customer accepts, in USD, given with 2
            decimal places (cents) as a positive number; it is charged exactly as passed after rounding
            half up to 2 decimal places.

    Returns:
        A dictionary rendered as text with: recall_case_id (the reference number of the new recall
        request), fee_entry_id (the reference number of the recall fee charge), bank_transfer_id (the
        transfer being recalled), recall_fee_usd (the fee charged, USD with 2 decimal places),
        payout_attempt (the payout attempt recalled, integer), case_status (open while the beneficiary
        bank has not answered), requested_on (the request date, YYYY-MM-DD) and fees_held_usd (the
        fees Paloma holds on the transfer afterwards, USD with 2 decimal places).
    """
    fee = round(float(recall_fee_usd), 2)
    attempt = int(payout_attempt)
    rows = ctx.find("bank_transfers", bank_transfer_id=bank_transfer_id)
    transfer = rows[0] if rows else {}
    customer_id = transfer.get("customer_id", "")
    today = ctx.now()[:10]
    case_id = ctx.make_id("bkc_", bank_transfer_id, payout_attempt, recall_fee_usd)
    ctx.create("bank_cases", case_id, case_id=case_id, bank_transfer_id=bank_transfer_id,
               customer_id=customer_id, event_type="bank_recall_requested", case_date=today,
               case_type="recall_request", rfi_topic="none", doc_reference="", related_case_id="",
               case_outcome="open", remedy_choice="not_applicable", resolution_due_date="")
    fee_id = ctx.make_id("bkl_", bank_transfer_id, payout_attempt, recall_fee_usd, "recall_fee")
    ctx.create("bank_ledger", fee_id, ledger_entry_id=fee_id, bank_transfer_id=bank_transfer_id,
               customer_id=customer_id, event_type="bank_fee_charged", entry_date=today,
               amount_usd=fee, fee_type="recall_fee", fee_refund_reason="none",
               payout_attempt=attempt, receive_amount="", fx_rate_applied="", return_reason="none",
               refund_basis="none", credit_reason="none", related_entry_id="")
    held = round(float(transfer.get("fees_held_usd") or 0) + fee, 2)
    ctx.update("bank_transfers", bank_transfer_id, fees_held_usd=held)
    return str({"recall_case_id": case_id, "fee_entry_id": fee_id, "bank_transfer_id": bank_transfer_id,
                "recall_fee_usd": fee, "payout_attempt": attempt, "case_status": "open",
                "requested_on": today, "fees_held_usd": held})


@tool(owner="agent", rw="write")
def book_shortfall_credit_979e59e7(ctx: ToolContext, bank_transfer_id: str, related_entry_id: str,
                                   credit_amount_usd: float) -> str:
    """Put Paloma's own money into a Bank Deposit transfer to make good an amount the recipient was
    short-paid, on a transfer where Paloma's error-resolution team found an incorrect amount.

    One call books one Paloma make-good credit for an incorrect-amount shortfall on the transfer's money
    movements, dated today and pointing back to the payout that came up short, and raises the principal
    Paloma holds on the transfer by the amount credited. Nothing is sent to the customer or the
    recipient by this credit itself; the credit then shows on the transfer's money movements and the
    transfer's held principal rises by the same amount.

    Args:
        bank_transfer_id: Id class — the reference number of the Bank Deposit transfer being made good,
            as returned by the Bank Deposit transfer lookup for this customer.
        related_entry_id: Id class — the reference number of the payout money movement that came up
            short, as returned by the Bank Deposit money-movement lookup for that transfer.
        credit_amount_usd: Fixed-format class — the amount Paloma credits, in USD, given with 2 decimal
            places (cents) as a positive number; it is recorded exactly as passed after rounding half up
            to 2 decimal places.

    Returns:
        A dictionary rendered as text with: ledger_entry_id (the reference number of the new credit
        movement), bank_transfer_id (the transfer credited), credited_usd (the amount credited, USD with
        2 decimal places), credit_reason (always incorrect_amount_shortfall), entry_date (the credit date,
        YYYY-MM-DD), principal_held_usd (the principal Paloma holds on the transfer afterwards, USD with 2
        decimal places) and status (credited when the credit was booked).
    """
    amount = round(float(credit_amount_usd), 2)
    rows = ctx.find("bank_transfers", bank_transfer_id=bank_transfer_id)
    transfer = rows[0] if rows else {}
    today = ctx.now()[:10]
    rid = ctx.make_id("bkl_", bank_transfer_id, related_entry_id, credit_amount_usd)
    ctx.create("bank_ledger", rid, ledger_entry_id=rid, bank_transfer_id=bank_transfer_id,
               customer_id=transfer.get("customer_id", ""), event_type="bank_paloma_credit",
               entry_date=today, amount_usd=amount, fee_type="none", fee_refund_reason="none",
               payout_attempt=0, receive_amount="", fx_rate_applied="", return_reason="none",
               refund_basis="none", credit_reason="incorrect_amount_shortfall",
               related_entry_id=related_entry_id)
    held = round(float(transfer.get("principal_held_usd") or 0) + amount, 2)
    ctx.update("bank_transfers", bank_transfer_id, principal_held_usd=held)
    return str({"ledger_entry_id": rid, "bank_transfer_id": bank_transfer_id, "credited_usd": amount,
                "credit_reason": "incorrect_amount_shortfall", "entry_date": today,
                "principal_held_usd": held, "status": "credited"})


@tool(owner="user", rw="write")
def choose_shortfall_delivery_49c1959f(ctx: ToolContext, bank_transfer_id: str, related_case_id: str,
                                       payout_attempt: int, payout_usd: float, delivery_rate: float,
                                       receive_amount: float, date_available: str) -> str:
    """Choose, as the customer, to have the amount a recipient was short-paid delivered to the same
    recipient bank account, on a Bank Deposit transfer where Paloma found an incorrect amount.

    One call records the customer's remedy choice (delivery of the shortfall) against the error notice,
    sends a new payout attempt of the dollars Paloma holds on the transfer to the beneficiary bank in the
    payout currency at the stated rate, puts the transfer back in transit with the newly disclosed date
    of availability, and lowers the principal Paloma holds on the transfer by the dollars paid out. The
    customer sees the remedy recorded, the transfer in transit again and the new payout with its amount
    and date.

    Args:
        bank_transfer_id: Id class — the reference number of the Bank Deposit transfer whose shortfall is
            delivered, as the support agent reads it out from the transfer record.
        related_case_id: Id class — the reference number of the error notice on which the incorrect amount
            was found, as the support agent reads it out from the transfer's case file.
        payout_attempt: Fixed-format class — the attempt number of this new payout, an integer count
            starting at 1, as the support agent reads it out.
        payout_usd: Fixed-format class — the dollars paid out on this payout, in USD, given with 2 decimal
            places (cents) as a positive number, as the support agent reads it out; recorded after rounding
            half up to 2 decimal places.
        delivery_rate: Fixed-format class — the exchange rate used for this payout, in payout-currency
            units per 1 USD, given with 4 decimal places, as the support agent reads it out; recorded after
            rounding half up to 4 decimal places.
        receive_amount: Fixed-format class — the amount the recipient's bank receives on this payout, in
            payout currency, 2 decimal places (whole units for VND), as the support agent reads it out;
            recorded after rounding half up to 2 decimal places.
        date_available: Fixed-format class — the newly disclosed date of availability of this payout, in
            YYYY-MM-DD, as the support agent reads it out; recorded exactly as passed.

    Returns:
        A dictionary rendered as text with: remedy_case_id (the reference number of the recorded remedy
        choice), payout_entry_id (the reference number of the new payout movement), bank_transfer_id (the
        transfer), remedy_choice (always resend_shortfall), payout_attempt (integer), payout_usd (USD with
        2 decimal places), receive_amount (payout currency with 2 decimal places), status (in_transit once
        the payout has been sent), date_available (YYYY-MM-DD) and principal_held_usd (the principal
        Paloma still holds on the transfer afterwards, USD with 2 decimal places).
    """
    usd = round(float(payout_usd), 2)
    rate = round(float(delivery_rate), 4)
    amount = round(float(receive_amount), 2)
    attempt = int(payout_attempt)
    rows = ctx.find("bank_transfers", bank_transfer_id=bank_transfer_id)
    transfer = rows[0] if rows else {}
    customer_id = transfer.get("customer_id", "")
    today = ctx.now()[:10]
    case_id = ctx.make_id("bkc_", bank_transfer_id, related_case_id, payout_attempt, payout_usd,
                          delivery_rate, receive_amount, date_available)
    ctx.create("bank_cases", case_id, case_id=case_id, bank_transfer_id=bank_transfer_id,
               customer_id=customer_id, event_type="bank_remedy_chosen", case_date=today,
               case_type="incorrect_amount", rfi_topic="none", doc_reference="",
               related_case_id=related_case_id, case_outcome="open", remedy_choice="resend_shortfall",
               resolution_due_date="")
    pay_id = ctx.make_id("bkl_", bank_transfer_id, payout_attempt, payout_usd, delivery_rate, receive_amount)
    ctx.create("bank_ledger", pay_id, ledger_entry_id=pay_id, bank_transfer_id=bank_transfer_id,
               customer_id=customer_id, event_type="bank_payout_sent", entry_date=today, amount_usd=usd,
               fee_type="none", fee_refund_reason="none", payout_attempt=attempt, receive_amount=amount,
               fx_rate_applied=rate, return_reason="none", refund_basis="none", credit_reason="none",
               related_entry_id="")
    held = round(float(transfer.get("principal_held_usd") or 0) - usd, 2)
    ctx.update("bank_transfers", bank_transfer_id, status="in_transit", date_available=date_available,
               principal_held_usd=held)
    return str({"remedy_case_id": case_id, "payout_entry_id": pay_id, "bank_transfer_id": bank_transfer_id,
                "remedy_choice": "resend_shortfall", "payout_attempt": attempt, "payout_usd": usd,
                "receive_amount": amount, "status": "in_transit", "date_available": date_available,
                "principal_held_usd": held})

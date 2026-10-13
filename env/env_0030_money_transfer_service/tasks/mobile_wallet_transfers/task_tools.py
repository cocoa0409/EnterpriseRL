"""Hidden task tools of the mobile_wallet_transfers difficulty (Paloma Remit, Mobile Wallet category).

Each tool performs one atomic write on one Mobile Wallet transfer and is reached only through
unlock_* -> call_*; its name is published only as an extended policy's target_tool. No tool
checks eligibility, prerequisites or amounts: the values passed in are booked as given.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def charge_resend_fee_8300b1da(ctx: ToolContext, wallet_transfer_id: str, fee_seq: int,
                               amount_usd: float) -> str:
    """Collect the charge for one customer-requested resend of a Mobile Wallet credit that bounced.

    Books one resend-charge entry (fee type retry_fee) on the given Mobile Wallet transfer, dated
    today and numbered with the resend number given, collected from the customer's original funding
    method; the fees Paloma holds for the transfer rise by the amount. The transfer's status, wallet
    destination and principal are not changed and no credit is sent by this action. The entry shows in
    the transfer's money movements and the customer sees the charge on the funding method they paid
    with. A dictionary receipt carrying the new entry's reference means the charge
    was booked.

    Args:
        wallet_transfer_id: Id class — the reference number of the Mobile Wallet transfer whose bounced
            credit is being sent again, as returned by the Mobile Wallet transfer lookup.
        fee_seq: Fixed-format class — the number of this resend on the transfer, an integer count
            starting at 1, equal to the number of credits already sent on the transfer.
        amount_usd: Fixed-format class — the resend charge collected, in USD, 2 decimal places,
            already rounded half up to the cent; 0.00 is booked as given.

    Returns:
        A dictionary rendered as text with: ledger_entry_id (reference of the new resend-charge
        entry), wallet_transfer_id (the transfer charged), fee_seq (integer resend number booked),
        amount_usd (USD charged, 2 decimals), entry_date (YYYY-MM-DD, today) and fees_held_usd (USD the
        transfer now holds in fees, 2 decimals). A receipt with a ledger_entry_id means the charge stands.
    """
    amount = round(float(amount_usd), 2)
    seq = int(fee_seq)
    found = ctx.find("wallet_transfers", wallet_transfer_id=wallet_transfer_id)
    row = found[0] if found else {}
    rid = ctx.make_id("wle_", wallet_transfer_id, "retry_fee", seq, amount)
    today = ctx.now()[:10]
    ctx.create("wallet_ledger", rid,
               ledger_entry_id=rid, wallet_transfer_id=wallet_transfer_id, customer_id=row.get("customer_id", ""),
               event_type="wallet_fee_charged", entry_date=today, amount_usd=amount,
               fee_type="retry_fee", fee_seq=seq, fee_refund_reason="none",
               credit_attempt=0, receive_amount="", fx_rate_applied="",
               failure_reason="none", refund_basis="none", credit_reason="none",
               related_entry_id="")
    fees_held = round(float(row.get("fees_held_usd") or 0) + amount, 2)
    ctx.update("wallet_transfers", wallet_transfer_id, fees_held_usd=fees_held)
    return str({"ledger_entry_id": rid, "wallet_transfer_id": wallet_transfer_id, "fee_seq": seq,
                "amount_usd": amount, "entry_date": today, "fees_held_usd": fees_held})


@tool(owner="agent", rw="write")
def resend_failed_credit_8d2e2e1a(ctx: ToolContext, wallet_transfer_id: str, credit_attempt: int,
                                  fx_rate_applied: float, receive_amount: float) -> str:
    """Send a bounced Mobile Wallet credit again to the wallet the transfer is addressed to.

    Sends the whole principal Paloma currently holds for the given Mobile Wallet transfer to its
    wallet provider as a new credit attempt, at the exchange rate and local amount given: one
    credit-sent entry is booked dated today, the principal Paloma holds for the transfer drops to
    0.00, the transfer moves to processing with its release moment set to now and its date
    available set to today, and the wallet destination stays as it is. The customer and recipient
    can follow the credit as in progress. A dictionary receipt carrying the new entry's
    reference means the credit was sent.

    Args:
        wallet_transfer_id: Id class — the reference number of the Mobile Wallet transfer whose bounced
            credit is sent again, as returned by the Mobile Wallet transfer lookup.
        credit_attempt: Fixed-format class — the number of this credit attempt on the transfer, an
            integer count starting at 1 (one more than the credits already sent on the transfer).
        fx_rate_applied: Fixed-format class — the exchange rate this credit converts at, in
            payout-currency units per 1 USD, 4 decimal places, already rounded half up.
        receive_amount: Fixed-format class — the amount this credit delivers to the wallet, in
            payout currency, 2 decimal places, already rounded half up.

    Returns:
        A dictionary rendered as text with: ledger_entry_id (reference of the new credit-sent entry),
        wallet_transfer_id (the transfer), credit_attempt (integer attempt number), amount_usd (USD
        principal sent, 2 decimals), fx_rate_applied (rate, 4 decimals), receive_amount (payout
        currency, 2 decimals), status (now processing) and released_at (moment sent,
        YYYY-MM-DDTHH:MM:SS). A receipt with a ledger_entry_id and status processing means the credit
        went out.
    """
    attempt = int(credit_attempt)
    rate = round(float(fx_rate_applied), 4)
    local = round(float(receive_amount), 2)
    found = ctx.find("wallet_transfers", wallet_transfer_id=wallet_transfer_id)
    row = found[0] if found else {}
    principal = round(float(row.get("principal_held_usd") or 0), 2)
    rid = ctx.make_id("wle_", wallet_transfer_id, "credit_sent", attempt, rate, local)
    clock = ctx.now()  # e.g. '2026-10-06 11:20:00 CDT'; stored in the schema's YYYY-MM-DDTHH:MM:SS form
    now = f"{clock[:10]}T{clock[11:19]}"
    ctx.create("wallet_ledger", rid,
               ledger_entry_id=rid, wallet_transfer_id=wallet_transfer_id, customer_id=row.get("customer_id", ""),
               event_type="wallet_credit_sent", entry_date=now[:10], amount_usd=principal,
               fee_type="none", fee_seq=0, fee_refund_reason="none",
               credit_attempt=attempt, receive_amount=local, fx_rate_applied=rate,
               failure_reason="none", refund_basis="none", credit_reason="none",
               related_entry_id="")
    ctx.update("wallet_transfers", wallet_transfer_id, status="processing", released_at=now,
               date_available=now[:10], principal_held_usd=0.0)
    return str({"ledger_entry_id": rid, "wallet_transfer_id": wallet_transfer_id, "credit_attempt": attempt,
                "amount_usd": principal, "fx_rate_applied": rate, "receive_amount": local,
                "status": "processing", "released_at": now})


@tool(owner="agent", rw="write")
def book_shortfall_makegood_2311834f(ctx: ToolContext, wallet_transfer_id: str, related_entry_id: str,
                                     amount_usd: float) -> str:
    """Book Paloma's own make-good credit for a Mobile Wallet credit that reached the wallet short.

    Books one Paloma credit entry (credit reason incorrect_amount_shortfall) on the given Mobile
    Wallet transfer, dated today and pointing at the credit that arrived short, funded with Paloma's
    own money; the principal Paloma holds for the transfer rises by the amount and is held for a
    re-credit or a refund. The transfer's status is not changed and nothing is sent to the
    wallet or the customer by this action. A dictionary receipt carrying the new entry's reference
    means the make-good stands.

    Args:
        wallet_transfer_id: Id class — the reference number of the Mobile Wallet transfer whose credit
            arrived short, as returned by the Mobile Wallet transfer lookup.
        related_entry_id: Id class — the reference number of the credit-sent money movement that
            arrived short, as returned by the Mobile Wallet money-movement lookup for that transfer.
        amount_usd: Fixed-format class — the make-good Paloma puts in, in USD, 2 decimal places,
            already rounded half up to the cent.

    Returns:
        A dictionary rendered as text with: ledger_entry_id (reference of the new Paloma credit entry),
        wallet_transfer_id (the transfer), related_entry_id (the short credit it answers), amount_usd
        (USD credited, 2 decimals), entry_date (YYYY-MM-DD, today) and principal_held_usd (USD Paloma
        now holds for the transfer, 2 decimals). A receipt with a ledger_entry_id means the credit stands.
    """
    amount = round(float(amount_usd), 2)
    found = ctx.find("wallet_transfers", wallet_transfer_id=wallet_transfer_id)
    row = found[0] if found else {}
    rid = ctx.make_id("wle_", wallet_transfer_id, "incorrect_amount_shortfall", related_entry_id, amount)
    today = ctx.now()[:10]
    ctx.create("wallet_ledger", rid,
               ledger_entry_id=rid, wallet_transfer_id=wallet_transfer_id, customer_id=row.get("customer_id", ""),
               event_type="wallet_paloma_credit", entry_date=today, amount_usd=amount,
               fee_type="none", fee_seq=0, fee_refund_reason="none",
               credit_attempt=0, receive_amount="", fx_rate_applied="",
               failure_reason="none", refund_basis="none", credit_reason="incorrect_amount_shortfall",
               related_entry_id=related_entry_id)
    held = round(float(row.get("principal_held_usd") or 0) + amount, 2)
    ctx.update("wallet_transfers", wallet_transfer_id, principal_held_usd=held)
    return str({"ledger_entry_id": rid, "wallet_transfer_id": wallet_transfer_id,
                "related_entry_id": related_entry_id, "amount_usd": amount, "entry_date": today,
                "principal_held_usd": held})


@tool(owner="user", rw="write")
def choose_shortfall_recredit_f54302ef(ctx: ToolContext, wallet_transfer_id: str, related_case_id: str,
                                       credit_attempt: int, fx_rate_applied: float,
                                       receive_amount: float) -> str:
    """Record the customer's own choice to have a short Mobile Wallet credit made good by a re-credit.

    The customer chooses, on an error notice that Paloma found in their favour, to have the missing
    amount re-credited to the same wallet: the choice is recorded against the notice (remedy
    recredit_shortfall, dated today), and the whole principal Paloma holds for the transfer is sent
    at once to the transfer's wallet as a new credit attempt at the rate and local amount given. The
    principal Paloma holds drops to 0.00 and the transfer moves to processing with its release moment
    set to now and its date available set to today. The customer can tell the recipient the
    re-credit is on its way. A dictionary receipt carrying the choice and credit references means
    both stand.

    Args:
        wallet_transfer_id: Id class — the reference number of the Mobile Wallet transfer the remedy is
            for, as the agent reads it from the Mobile Wallet transfer lookup and passes it on.
        related_case_id: Id class — the reference number of the error notice the choice answers, as the
            agent reads it from the Mobile Wallet case lookup and passes it on.
        credit_attempt: Fixed-format class — the number of the re-credit attempt on the transfer, an
            integer count starting at 1 (one more than the credits already sent on the transfer).
        fx_rate_applied: Fixed-format class — the exchange rate the re-credit converts at, in
            payout-currency units per 1 USD, 4 decimal places, as the agent quotes it.
        receive_amount: Fixed-format class — the amount the re-credit delivers to the wallet, in payout
            currency, 2 decimal places, as the agent quotes it.

    Returns:
        A dictionary rendered as text with: case_id (reference of the recorded choice), remedy_choice
        (recredit_shortfall), ledger_entry_id (reference of the re-credit entry), credit_attempt
        (integer attempt number), amount_usd (USD sent, 2 decimals), fx_rate_applied (4 decimals),
        receive_amount (payout currency, 2 decimals) and status (now processing). A receipt with both
        references and status processing means the choice is recorded and the re-credit went out.
    """
    attempt = int(credit_attempt)
    rate = round(float(fx_rate_applied), 4)
    local = round(float(receive_amount), 2)
    found = ctx.find("wallet_transfers", wallet_transfer_id=wallet_transfer_id)
    row = found[0] if found else {}
    principal = round(float(row.get("principal_held_usd") or 0), 2)
    clock = ctx.now()  # e.g. '2026-10-06 11:20:00 CDT'; stored in the schema's YYYY-MM-DDTHH:MM:SS form
    now = f"{clock[:10]}T{clock[11:19]}"
    cid = ctx.make_id("wca_", wallet_transfer_id, related_case_id, "recredit_shortfall")
    ctx.create("wallet_cases", cid, case_id=cid, wallet_transfer_id=wallet_transfer_id,
               customer_id=row.get("customer_id", ""), event_type="wallet_remedy_chosen", case_date=now[:10],
               case_type="none", rfi_topic="none", doc_reference="", new_wallet_provider="none",
               new_wallet_number="", new_wallet_holder_name="", redirect_seq=0, related_case_id=related_case_id,
               case_outcome="not_applicable", remedy_choice="recredit_shortfall", resolution_due_date="")
    rid = ctx.make_id("wle_", wallet_transfer_id, "credit_sent", attempt, rate, local)
    ctx.create("wallet_ledger", rid,
               ledger_entry_id=rid, wallet_transfer_id=wallet_transfer_id, customer_id=row.get("customer_id", ""),
               event_type="wallet_credit_sent", entry_date=now[:10], amount_usd=principal,
               fee_type="none", fee_seq=0, fee_refund_reason="none",
               credit_attempt=attempt, receive_amount=local, fx_rate_applied=rate,
               failure_reason="none", refund_basis="none", credit_reason="none",
               related_entry_id="")
    ctx.update("wallet_transfers", wallet_transfer_id, status="processing", released_at=now,
               date_available=now[:10], closed_date="", principal_held_usd=0.0)
    return str({"case_id": cid, "remedy_choice": "recredit_shortfall", "ledger_entry_id": rid,
                "credit_attempt": attempt, "amount_usd": principal, "fx_rate_applied": rate,
                "receive_amount": local, "status": "processing"})


@tool(owner="agent", rw="write")
def fund_wallet_recredit_aebfda78(ctx: ToolContext, wallet_transfer_id: str, related_entry_id: str,
                                  amount_usd: float) -> str:
    """Book Paloma's own funding for re-crediting a Mobile Wallet transfer that was credited to the wrong wallet.

    Books one Paloma credit entry (credit reason error_recredit) on the given Mobile Wallet transfer,
    dated today and pointing at the credit that went to a wallet other than the transfer's own,
    funded with Paloma's own money; the principal Paloma holds for the transfer rises by the amount
    and is held for the re-credit to the transfer's own wallet. The transfer's status is not changed
    and nothing is sent to any wallet or to the customer by this action. A dictionary receipt
    carrying the new entry's reference means the funding stands.

    Args:
        wallet_transfer_id: Id class — the reference number of the Mobile Wallet transfer that was
            credited to the wrong wallet, as returned by the Mobile Wallet transfer lookup.
        related_entry_id: Id class — the reference number of the credit-sent money movement that
            reached the wrong wallet, as returned by the Mobile Wallet money-movement lookup.
        amount_usd: Fixed-format class — the funding Paloma puts in, in USD, 2 decimal places, already
            rounded half up to the cent.

    Returns:
        A dictionary rendered as text with: ledger_entry_id (reference of the new Paloma credit entry),
        wallet_transfer_id (the transfer), related_entry_id (the misdirected credit it answers),
        amount_usd (USD credited, 2 decimals), entry_date (YYYY-MM-DD, today) and principal_held_usd
        (USD Paloma now holds for the transfer, 2 decimals). A receipt with a ledger_entry_id means
        the funding stands.
    """
    amount = round(float(amount_usd), 2)
    found = ctx.find("wallet_transfers", wallet_transfer_id=wallet_transfer_id)
    row = found[0] if found else {}
    rid = ctx.make_id("wle_", wallet_transfer_id, "error_recredit", related_entry_id, amount)
    today = ctx.now()[:10]
    ctx.create("wallet_ledger", rid,
               ledger_entry_id=rid, wallet_transfer_id=wallet_transfer_id, customer_id=row.get("customer_id", ""),
               event_type="wallet_paloma_credit", entry_date=today, amount_usd=amount,
               fee_type="none", fee_seq=0, fee_refund_reason="none",
               credit_attempt=0, receive_amount="", fx_rate_applied="",
               failure_reason="none", refund_basis="none", credit_reason="error_recredit",
               related_entry_id=related_entry_id)
    held = round(float(row.get("principal_held_usd") or 0) + amount, 2)
    ctx.update("wallet_transfers", wallet_transfer_id, principal_held_usd=held)
    return str({"ledger_entry_id": rid, "wallet_transfer_id": wallet_transfer_id,
                "related_entry_id": related_entry_id, "amount_usd": amount, "entry_date": today,
                "principal_held_usd": held})


@tool(owner="user", rw="write")
def choose_wallet_recredit_d4ef146e(ctx: ToolContext, wallet_transfer_id: str, related_case_id: str,
                                    credit_attempt: int, fx_rate_applied: float, receive_amount: float) -> str:
    """Record the customer's own choice to have a wrongly credited Mobile Wallet transfer re-credited.

    The customer chooses, on a wrong-wallet error notice that Paloma found in their favour, to have the
    money credited again to the wallet the transfer is addressed to: the choice is recorded against the
    notice (remedy recredit, dated today), and the whole principal Paloma holds for the transfer is
    sent at once to the transfer's own wallet as a new credit attempt at the rate and local amount
    given. The principal Paloma holds drops to 0.00 and the transfer moves to processing with its
    release moment set to now and its date available set to today. The customer can tell the
    recipient the money is on its way. A dictionary receipt carrying the choice and credit references
    means both stand.

    Args:
        wallet_transfer_id: Id class — the reference number of the Mobile Wallet transfer the remedy is
            for, as the agent reads it from the Mobile Wallet transfer lookup and passes it on.
        related_case_id: Id class — the reference number of the wrong-wallet error notice the choice
            answers, as the agent reads it from the Mobile Wallet case lookup and passes it on.
        credit_attempt: Fixed-format class — the number of the re-credit attempt on the transfer, an
            integer count starting at 1 (one more than the credits already sent on the transfer).
        fx_rate_applied: Fixed-format class — the exchange rate the re-credit converts at, in
            payout-currency units per 1 USD, 4 decimal places, as the agent quotes it.
        receive_amount: Fixed-format class — the amount the re-credit delivers to the wallet, in payout
            currency, 2 decimal places, as the agent quotes it.

    Returns:
        A dictionary rendered as text with: case_id (reference of the recorded choice), remedy_choice
        (recredit), ledger_entry_id (reference of the re-credit entry), credit_attempt (integer attempt
        number), amount_usd (USD sent, 2 decimals), fx_rate_applied (4 decimals), receive_amount (payout
        currency, 2 decimals) and status (now processing). A receipt with both references and status
        processing means the choice is recorded and the re-credit went out.
    """
    attempt = int(credit_attempt)
    rate = round(float(fx_rate_applied), 4)
    local = round(float(receive_amount), 2)
    found = ctx.find("wallet_transfers", wallet_transfer_id=wallet_transfer_id)
    row = found[0] if found else {}
    principal = round(float(row.get("principal_held_usd") or 0), 2)
    clock = ctx.now()  # e.g. '2026-10-06 11:20:00 CDT'; stored in the schema's YYYY-MM-DDTHH:MM:SS form
    now = f"{clock[:10]}T{clock[11:19]}"
    cid = ctx.make_id("wca_", wallet_transfer_id, related_case_id, "recredit")
    ctx.create("wallet_cases", cid, case_id=cid, wallet_transfer_id=wallet_transfer_id,
               customer_id=row.get("customer_id", ""), event_type="wallet_remedy_chosen", case_date=now[:10],
               case_type="none", rfi_topic="none", doc_reference="", new_wallet_provider="none",
               new_wallet_number="", new_wallet_holder_name="", redirect_seq=0, related_case_id=related_case_id,
               case_outcome="not_applicable", remedy_choice="recredit", resolution_due_date="")
    rid = ctx.make_id("wle_", wallet_transfer_id, "credit_sent", attempt, rate, local)
    ctx.create("wallet_ledger", rid,
               ledger_entry_id=rid, wallet_transfer_id=wallet_transfer_id, customer_id=row.get("customer_id", ""),
               event_type="wallet_credit_sent", entry_date=now[:10], amount_usd=principal,
               fee_type="none", fee_seq=0, fee_refund_reason="none",
               credit_attempt=attempt, receive_amount=local, fx_rate_applied=rate,
               failure_reason="none", refund_basis="none", credit_reason="none",
               related_entry_id="")
    ctx.update("wallet_transfers", wallet_transfer_id, status="processing", released_at=now,
               date_available=now[:10], closed_date="", principal_held_usd=0.0)
    return str({"case_id": cid, "remedy_choice": "recredit", "ledger_entry_id": rid,
                "credit_attempt": attempt, "amount_usd": principal, "fx_rate_applied": rate,
                "receive_amount": local, "status": "processing"})

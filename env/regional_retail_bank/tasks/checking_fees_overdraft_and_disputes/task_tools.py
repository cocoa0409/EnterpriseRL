"""Hidden task tools for the difficulty checking_fees_overdraft_and_disputes.

Each function performs one atomic write on a Personal Checking record of Piedmont
Crescent Bank. None of them looks up history, applies a fee schedule or judges whether
a business condition is met: the agent reads the knowledge base and the records, works
the figure out, and passes it in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_fee_schedule_correction_961f83a2(ctx: ToolContext, checking_account_id: str, customer_id: str,
                                          source_item_id: str, correction_amount: float,
                                          statement_cycle: str) -> str:
    """Post a corrective entry on a personal checking account for the part of an overdraft charge that the bank took beyond its published fee schedule.

    One call books a single correction entry credited to the named checking account and
    marks it as a bank error tied to the overdraft charge it corrects; the account's
    posted ledger balance rises by the corrected amount at once. The owner sees the
    credit on the account with the overdraft charge it relates to, and the entry carries
    the bank-error ground rather than any goodwill ground. Nothing else on the account
    changes, and the original overdraft charge stays on the record.

    Args:
        checking_account_id: Id class — the reference number of the personal checking account the correction is credited to; take it from the checking account lookup for this owner before calling.
        customer_id: Id class — the reference number of the customer profile that owns the account, as returned by the customer profile lookup; it is stamped on the correction entry so the owner's refund record stays complete.
        source_item_id: Id class — the reference number of the single overdraft charge entry on the account that is being corrected; read it from the account's posted activity before calling.
        correction_amount: Fixed-format class — the money credited back, expressed in USD, 2 decimal places, always positive, in United States dollars and rounded half-up to the cent at the moment of the call; there is no empty value and zero is not accepted.
        statement_cycle: Fixed-format class — the statement cycle the correction entry belongs to, written as YYYY-MM, the month in which that cycle closes, with no day part and no time zone.

    Returns:
        A confirmation sentence containing the reference number minted for the new
        correction entry, the corrected amount formatted to the cent, and the account's
        posted ledger balance after the credit. The sentence naming a correction entry
        reference number is what indicates the call completed; afterwards the credit is
        visible in the account's posted activity.
    """
    amount = round(float(correction_amount), 2)
    rid = ctx.make_id("chktxn_", checking_account_id, customer_id, source_item_id, amount, statement_cycle)
    ctx.create("checking_transactions", rid, checking_txn_id=rid, checking_account_id=checking_account_id,
               customer_id=customer_id, event_type="checking_fee_refund", amount=amount,
               posted_date=ctx.now()[:10], channel="none", description="", trace_number="",
               check_number="", atm_operator_surcharge=0.00, fee_code="overdraft_item",
               source_item_id=source_item_id, statement_cycle=statement_cycle,
               adjustment_reason="bank_error", checking_dispute_id="")
    rows = ctx.find("checking_accounts", checking_account_id=checking_account_id)
    new_balance = round(float(rows[0].get("ledger_balance") or 0) + amount, 2) if rows else amount
    ctx.update("checking_accounts", checking_account_id, ledger_balance=new_balance)
    return (f"Correction entry {rid} credited {amount:.2f} to checking account {checking_account_id}; "
            f"posted ledger balance is now {new_balance:.2f}.")


@tool(owner="agent", rw="write")
def post_dispute_credit_reversal_956f6db8(ctx: ToolContext, checking_account_id: str, customer_id: str,
                                          checking_dispute_id: str, source_item_id: str,
                                          reversal_amount: float, statement_cycle: str) -> str:
    """Take back part or all of a temporary credit that was posted to a personal checking account while an electronic-transaction claim was being looked into.

    One call books a single take-back entry debited from the named checking account and
    ties it to the claim and to the temporary credit entry it reverses; the account's
    posted ledger balance falls by that amount at once. The owner sees the debit on the
    account alongside the temporary credit it relates to. The claim record itself is left
    as the Dispute Resolution team maintains it, and the disputed item is not touched.

    Args:
        checking_account_id: Id class — the reference number of the personal checking account the take-back is debited from; take it from the checking account lookup for this owner before calling.
        customer_id: Id class — the reference number of the customer profile that owns the account, as returned by the customer profile lookup; it is stamped on the take-back entry.
        checking_dispute_id: Id class — the reference number of the electronic-transaction claim the temporary credit belongs to, read from the dispute lookup before calling.
        source_item_id: Id class — the reference number of the temporary credit entry on the account that is being taken back, read from the account's posted activity before calling.
        reversal_amount: Fixed-format class — the money taken back, expressed in USD, 2 decimal places, always positive, in United States dollars and rounded half-up to the cent at the moment of the call; there is no empty value and zero is not accepted.
        statement_cycle: Fixed-format class — the statement cycle the take-back entry belongs to, written as YYYY-MM, the month in which that cycle closes, with no day part and no time zone.

    Returns:
        A confirmation sentence containing the reference number minted for the new
        take-back entry, the amount taken back formatted to the cent, and the account's
        posted ledger balance after the debit. The sentence naming a take-back entry
        reference number is what indicates the call completed; afterwards the debit is
        visible in the account's posted activity.
    """
    amount = round(float(reversal_amount), 2)
    rid = ctx.make_id("chktxn_", checking_account_id, customer_id, checking_dispute_id, source_item_id,
                      amount, statement_cycle)
    ctx.create("checking_transactions", rid, checking_txn_id=rid, checking_account_id=checking_account_id,
               customer_id=customer_id, event_type="checking_provisional_reversal", amount=amount,
               posted_date=ctx.now()[:10], channel="none", description="", trace_number="",
               check_number="", atm_operator_surcharge=0.00, fee_code="none",
               source_item_id=source_item_id, statement_cycle=statement_cycle,
               adjustment_reason="dispute_reversal", checking_dispute_id=checking_dispute_id)
    rows = ctx.find("checking_accounts", checking_account_id=checking_account_id)
    new_balance = round(float(rows[0].get("ledger_balance") or 0) - amount, 2) if rows else -amount
    ctx.update("checking_accounts", checking_account_id, ledger_balance=new_balance)
    return (f"Take-back entry {rid} debited {amount:.2f} from checking account {checking_account_id} "
            f"against claim {checking_dispute_id}; posted ledger balance is now {new_balance:.2f}.")


@tool(owner="user", rw="write")
def confirm_closure_payout_0546356c(ctx: ToolContext, checking_account_id: str, customer_id: str,
                                    disbursement_method: str, destination_account_id: str,
                                    payout_amount: float) -> str:
    """Let the owner of a personal checking account confirm that the account is to be closed and that the money left in it is to be paid out, and carry both out in one step.

    One call records the owner's confirmed closing instruction naming how the money is to
    reach them, books the paying-out entry as a debit on the account, and closes the
    account: its state becomes closed, the closing date is stamped, the posted ledger
    balance is brought to zero and any savings account named as an overdraft protection
    source is released. The owner sees the paying-out entry in the account's activity and
    the account shown as closed.

    Args:
        checking_account_id: Id class — the reference number of the personal checking account being closed, taken from the checking account lookup for this owner before the call.
        customer_id: Id class — the reference number of the customer profile of the owner giving the instruction, as returned by the customer profile lookup.
        disbursement_method: Enum class — how the money left in the account reaches the owner. Use transfer_to_pcb_account when the owner wants it moved to another Piedmont Crescent Bank account of theirs, which is then named as the destination. Use official_check_mailed when the owner wants a bank-issued check posted to the address held on their profile instead of a transfer.
        destination_account_id: Id class — the reference number of the Piedmont Crescent Bank savings or checking account that receives the money when the owner chose a transfer; read it from that product's account lookup, and pass an empty string when a check is being mailed instead.
        payout_amount: Fixed-format class — the money paid out of the account, expressed in USD, 2 decimal places, always positive, in United States dollars and rounded half-up to the cent at the moment of the call; there is no empty value.

    Returns:
        A confirmation sentence containing the reference number minted for the owner's
        confirmed closing instruction, the reference number minted for the paying-out
        entry, the amount paid out formatted to the cent, and the date the account
        closed. The sentence naming both reference numbers is what indicates the call
        completed; afterwards the account reads as closed with a zero balance.
    """
    amount = round(float(payout_amount), 2)
    today = ctx.now()[:10]
    req = ctx.make_id("chkclr_", checking_account_id, customer_id, disbursement_method,
                      destination_account_id, amount)
    ctx.create("checking_closure_requests", req, closure_request_id=req, customer_id=customer_id,
               checking_account_id=checking_account_id, disbursement_method=disbursement_method,
               destination_account_id=destination_account_id, request_status="completed",
               created_at=ctx.now())
    txn = ctx.make_id("chktxn_", req, amount)
    ctx.create("checking_transactions", txn, checking_txn_id=txn, checking_account_id=checking_account_id,
               customer_id=customer_id, event_type="checking_debit", amount=amount, posted_date=today,
               channel="internal_transfer", description="Closing balance paid out", trace_number="",
               check_number="", atm_operator_surcharge=0.00, fee_code="none", source_item_id="",
               statement_cycle=today[:7], adjustment_reason="none", checking_dispute_id="",
               counterparty_account_id=destination_account_id)
    ctx.update("checking_accounts", checking_account_id, status="closed", closed_date=today,
               ledger_balance=0.00, overdraft_link_savings_account_id="")
    return (f"Closing instruction {req} confirmed and paying-out entry {txn} booked for {amount:.2f}; "
            f"checking account {checking_account_id} closed on {today}.")


@tool(owner="agent", rw="write")
def convert_account_tier_569988a7(ctx: ToolContext, checking_account_id: str, customer_id: str,
                                  target_variant_name: str) -> str:
    """Move a personal checking account onto a different Personal Checking tier while it keeps its account number, its balance and all of its past activity.

    One call rewrites the tier held on the named account, so that from then on the fee
    schedule, waivers, allowances and limits of the new tier are the ones that govern it.
    Nothing is charged for the move, no entry is booked on the account and the owner sees
    the account listed under its new tier straight away.

    Args:
        checking_account_id: Id class — the reference number of the personal checking account whose tier is being rewritten; take it from the checking account lookup for this owner before calling.
        customer_id: Id class — the reference number of the customer profile that owns the account, as returned by the customer profile lookup; the move is recorded against that owner.
        target_variant_name: Enum class — the official name of the tier the account is moved onto. Access Checking is the entry tier for an adult who keeps no qualifying balance and wants the simplest account. Student Checking is for a young owner still inside the student age range. Everyday Checking is the general transactional tier for an owner with an ordinary balance or direct deposit. Interest Checking is for an owner who keeps a mid-sized balance and wants the account itself to earn. Premier Checking is for an owner whose deposits across the bank reach the premier relationship level. Private Client Checking is for an owner whose relationship reaches the private client level.

    Returns:
        A confirmation sentence naming the checking account reference number, the tier the
        account now sits on and the owner it was recorded against. The sentence naming the
        new tier is what indicates the call completed; afterwards the account lookup shows
        that tier.
    """
    ctx.update("checking_accounts", checking_account_id, variant_name=target_variant_name)
    return (f"Checking account {checking_account_id} now sits on {target_variant_name} for owner "
            f"{customer_id}; account number, balance and activity are unchanged.")


@tool(owner="agent", rw="write")
def post_dispute_provisional_credit_b16208c2(ctx: ToolContext, checking_account_id: str, customer_id: str,
                                             checking_dispute_id: str, source_item_id: str,
                                             credit_amount: float, statement_cycle: str) -> str:
    """Put a temporary credit onto a personal checking account for an electronic-transaction claim that is still being looked into.

    One call books a single temporary credit entry credited to the named checking account,
    tied to the claim and to the disputed debit, and moves that claim's state to
    temporarily credited. The account's posted ledger balance rises by the credited amount
    at once and the owner can use the money while the claim is worked. The disputed debit
    itself stays on the record unchanged.

    Args:
        checking_account_id: Id class — the reference number of the personal checking account the temporary credit is posted to; take it from the checking account lookup for this owner before calling.
        customer_id: Id class — the reference number of the customer profile that owns the account and filed the claim, as returned by the customer profile lookup.
        checking_dispute_id: Id class — the reference number of the electronic-transaction claim the temporary credit belongs to, read from the dispute lookup before calling.
        source_item_id: Id class — the reference number of the disputed debit entry on the account that the claim was raised about, read from the account's posted activity before calling.
        credit_amount: Fixed-format class — the money credited for the time being, expressed in USD, 2 decimal places, always positive, in United States dollars and rounded half-up to the cent at the moment of the call; there is no empty value and zero is not accepted.
        statement_cycle: Fixed-format class — the statement cycle the temporary credit entry belongs to, written as YYYY-MM, the month in which that cycle closes, with no day part and no time zone.

    Returns:
        A confirmation sentence containing the reference number minted for the new
        temporary credit entry, the credited amount formatted to the cent, the account's
        posted ledger balance after the credit and the claim's state afterwards. The
        sentence naming a temporary credit entry reference number is what indicates the
        call completed; afterwards the credit is visible in the account's posted activity.
    """
    amount = round(float(credit_amount), 2)
    rid = ctx.make_id("chktxn_", checking_account_id, customer_id, checking_dispute_id, source_item_id,
                      amount, statement_cycle)
    ctx.create("checking_transactions", rid, checking_txn_id=rid, checking_account_id=checking_account_id,
               customer_id=customer_id, event_type="checking_provisional_credit", amount=amount,
               posted_date=ctx.now()[:10], channel="none", description="", trace_number="",
               check_number="", atm_operator_surcharge=0.00, fee_code="none",
               source_item_id=source_item_id, statement_cycle=statement_cycle,
               adjustment_reason="dispute_provisional", checking_dispute_id=checking_dispute_id)
    ctx.update("checking_disputes", checking_dispute_id, dispute_status="provisional_credited")
    rows = ctx.find("checking_accounts", checking_account_id=checking_account_id)
    new_balance = round(float(rows[0].get("ledger_balance") or 0) + amount, 2) if rows else amount
    ctx.update("checking_accounts", checking_account_id, ledger_balance=new_balance)
    return (f"Temporary credit entry {rid} credited {amount:.2f} to checking account {checking_account_id}; "
            f"posted ledger balance is now {new_balance:.2f} and claim {checking_dispute_id} now reads "
            "temporarily credited.")


@tool(owner="user", rw="write")
def authorize_overdraft_protection_source_1d4e232c(ctx: ToolContext, checking_account_id: str,
                                                   overdraft_link_savings_account_id: str) -> str:
    """Let the owner name one of their own savings accounts as the account Piedmont Crescent Bank may draw on to cover items that would otherwise overdraw their personal checking account.

    One call writes that savings account onto the checking account as its overdraft
    protection source, replacing whatever source was named there before. From then on the
    named savings account is the one the bank reaches into for a covering transfer. No
    money moves during this call, nothing is charged, and the owner sees the savings
    account shown as the protection source on the checking account.

    Args:
        checking_account_id: Id class — the reference number of the personal checking account that is to be protected; take it from the checking account lookup for this owner before the call.
        overdraft_link_savings_account_id: Id class — the reference number of the owner's savings or money market account that is to be drawn on, read from the savings account lookup; pass an empty string to leave the checking account with no protection source at all.

    Returns:
        A confirmation sentence naming the checking account reference number and the
        savings account reference number now recorded as its protection source. The
        sentence naming that savings account is what indicates the call completed;
        afterwards the checking account lookup shows it as the protection source.
    """
    ctx.update("checking_accounts", checking_account_id,
               overdraft_link_savings_account_id=overdraft_link_savings_account_id)
    return (f"Checking account {checking_account_id} now draws on savings account "
            f"{overdraft_link_savings_account_id} when an item would overdraw it.")


@tool(owner="agent", rw="write")
def post_overdraft_courtesy_relief_64b96dbf(ctx: ToolContext, checking_account_id: str, customer_id: str,
                                            source_item_id: str, relief_amount: float,
                                            statement_cycle: str) -> str:
    """Give back money as a goodwill gesture on the overdraft charges that a personal checking account has correctly been billed.

    One call books a single goodwill entry credited to the named checking account, marks
    it as a goodwill gesture rather than a bank error, and ties it to the overdraft charge
    it is granted against; the account's posted ledger balance rises by that amount at
    once. The owner sees the credit in the account's activity, and the overdraft charges
    themselves stay on the record.

    Args:
        checking_account_id: Id class — the reference number of the personal checking account the goodwill credit is posted to; take it from the checking account lookup for this owner before calling.
        customer_id: Id class — the reference number of the customer profile that owns the account, as returned by the customer profile lookup; it is stamped on the entry so the owner's goodwill record stays complete.
        source_item_id: Id class — the reference number of the single overdraft charge entry on the account that the goodwill entry is recorded against, read from the account's posted activity before calling.
        relief_amount: Fixed-format class — the money given back as goodwill, expressed in USD, 2 decimal places, always positive, in United States dollars and rounded half-up to the cent at the moment of the call; there is no empty value and zero is not accepted.
        statement_cycle: Fixed-format class — the statement cycle the goodwill entry belongs to, written as YYYY-MM, the month in which that cycle closes, with no day part and no time zone.

    Returns:
        A confirmation sentence containing the reference number minted for the new
        goodwill entry, the amount given back formatted to the cent, and the account's
        posted ledger balance after the credit. The sentence naming a goodwill entry
        reference number is what indicates the call completed; afterwards the credit is
        visible in the account's posted activity.
    """
    amount = round(float(relief_amount), 2)
    rid = ctx.make_id("chktxn_", checking_account_id, customer_id, source_item_id, amount,
                      statement_cycle, "courtesy")
    ctx.create("checking_transactions", rid, checking_txn_id=rid, checking_account_id=checking_account_id,
               customer_id=customer_id, event_type="checking_fee_refund", amount=amount,
               posted_date=ctx.now()[:10], channel="none", description="", trace_number="",
               check_number="", atm_operator_surcharge=0.00, fee_code="overdraft_item",
               source_item_id=source_item_id, statement_cycle=statement_cycle,
               adjustment_reason="courtesy_waiver", checking_dispute_id="")
    rows = ctx.find("checking_accounts", checking_account_id=checking_account_id)
    new_balance = round(float(rows[0].get("ledger_balance") or 0) + amount, 2) if rows else amount
    ctx.update("checking_accounts", checking_account_id, ledger_balance=new_balance)
    return (f"Goodwill entry {rid} credited {amount:.2f} to checking account {checking_account_id}; "
            f"posted ledger balance is now {new_balance:.2f}.")

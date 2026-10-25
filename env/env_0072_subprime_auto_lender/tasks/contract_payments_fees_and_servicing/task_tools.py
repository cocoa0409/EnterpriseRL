"""Hidden task tools for contract_payments_fees_and_servicing (env_0072_subprime_auto_lender).

Each tool performs one atomic servicing write on a Harborline retail installment contract with the
values the representative (or the borrower) has already worked out; no tool judges eligibility,
aggregates history or computes an amount.
"""

from erlbench import ToolContext, tool


class _Calendar:
    """Pure-Python calendar arithmetic on YYYY-MM-DD strings (no clock, no library)."""

    @staticmethod
    def add_months(day: str, months: int) -> str:
        y, m, d = (int(p) for p in str(day)[:10].split("-"))
        m0 = m - 1 + int(months)
        return f"{y + m0 // 12:04d}-{m0 % 12 + 1:02d}-{d:02d}"


_LEDGER_BLANK = dict(payment_channel="not_applicable", payment_type="not_applicable",
                     interest_applied_usd=0.0, principal_applied_usd=0.0, fees_applied_usd=0.0,
                     return_reason="not_applicable", waiver_reason="not_applicable",
                     ancillary_source="not_applicable", source_record_id="",
                     fee_settlement_method="not_applicable")


@tool(owner="agent", rw="write")
def assess_late_charge_1a8e6313(ctx: ToolContext, contract_id: str, installment_due_date: str,
                                amount_usd: float) -> str:
    """Book a late charge on one installment of a borrower's retail installment contract. One call
    adds a single late-charge entry, dated today, to the contract's money history for the installment
    named, and raises the contract's fees due by the amount charged; the borrower sees the late
    charge on the contract and in the fees owed. A receipt carrying the new ledger reference means
    the charge is booked.

    Args:
        contract_id: Id class — the contract reference number of the retail installment contract being charged, as returned by the contract lookup for the verified borrower.
        installment_due_date: Fixed-format class — the due date of the installment the late charge is for, written YYYY-MM-DD, a calendar date with no time or time zone; never empty for this charge.
        amount_usd: Fixed-format class — the late charge amount in USD, 2 decimal places, 0.00 or more; the value is stored rounded half-up to the cent exactly as passed.

    Returns:
        A dictionary rendered as text with: contract_txn_id (the ledger reference of the new late-charge entry, text), contract_id (the contract charged, text), installment_due_date (YYYY-MM-DD of the installment charged), amount_usd (the late charge booked, USD number with 2 decimal places), fees_due_usd (the contract's fees due including this charge, USD number with 2 decimal places) and status (the text booked, meaning the charge is now owed on the contract).
    """
    contract = (ctx.find("contracts", contract_id=contract_id) or [{}])[0]
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("lc_", contract_id, installment_due_date, amount_usd)
    ctx.create("contract_transactions", rid, contract_txn_id=rid, contract_id=contract_id,
               customer_id=contract.get("customer_id", ""), event_type="contract_fee_assessed",
               txn_date=ctx.now()[:10], amount_usd=amount, fee_type="late_charge",
               installment_due_date=installment_due_date, related_txn_id="", **_LEDGER_BLANK)
    fees_due = round(float(contract.get("fees_due_usd") or 0.0) + amount, 2)
    ctx.update("contracts", contract_id, fees_due_usd=fees_due)
    return str({"contract_txn_id": rid, "contract_id": contract_id,
                "installment_due_date": installment_due_date, "amount_usd": amount,
                "fees_due_usd": fees_due, "status": "booked"})


@tool(owner="user", rw="write")
def sign_extension_agreement_772d986b(ctx: ToolContext, contract_id: str, service_request_id: str,
                                      requested_extension_months: int) -> str:
    """The borrower signs their open hardship extension agreement for a retail installment contract,
    committing to the number of installments it defers. One call records the borrower's signature
    on that agreement, sets the installments it defers, and moves the agreement from awaiting
    signature to signed; the borrower can see the signed agreement and its signature time. A
    receipt showing the agreement as signed means the signature is on file.

    Args:
        contract_id: Id class — the contract reference number of the retail installment contract the agreement is for, as returned by the contract lookup.
        service_request_id: Id class — the reference number of the borrower's open extension agreement awaiting signature on that contract, as returned by the servicing-request lookup.
        requested_extension_months: Fixed-format class — the installments the agreement defers, an integer count of installments, 0 when not applicable; a whole number with no decimals.

    Returns:
        A dictionary rendered as text with: service_request_id (the agreement signed, text), contract_id (the contract it covers, text), requested_extension_months (installments the signed agreement defers, integer), request_status (the text signed, meaning the borrower's signature is recorded) and signed_at (the signature time in the same date-time format the system clock reports, text).
    """
    months = int(requested_extension_months)
    signed_at = ctx.now()
    ctx.update("contract_service_requests", service_request_id, contract_id=contract_id,
               requested_extension_months=months, request_status="signed", signed_at=signed_at)
    return str({"service_request_id": service_request_id, "contract_id": contract_id,
                "requested_extension_months": months, "request_status": "signed",
                "signed_at": signed_at})


@tool(owner="agent", rw="write")
def grant_hardship_extension_883d335d(ctx: ToolContext, contract_id: str, service_request_id: str,
                                      extension_fee_usd: float) -> str:
    """Apply a borrower's signed hardship extension agreement to their retail installment contract.
    One call records the extension effective today for the installments the signed agreement
    defers, moves the contract's next due date and final installment date later by that many
    months on the same due day, books the extension fee passed (added to fees due) or records the
    fee as waived when the amount passed is zero, and marks the agreement applied. The borrower
    sees the new due dates and any extension fee owed. A receipt carrying the extension reference
    and the new dates means the extension is in effect.

    Args:
        contract_id: Id class — the contract reference number of the retail installment contract being extended, as returned by the contract lookup.
        service_request_id: Id class — the reference number of the borrower's signed extension agreement on that contract, as returned by the servicing-request lookup or by the signing receipt.
        extension_fee_usd: Fixed-format class — the extension fee charged for this extension in USD, 2 decimal places, 0.00 or more; stored rounded half-up to the cent exactly as passed, and 0.00 records the fee as waived.

    Returns:
        A dictionary rendered as text with: servicing_event_id (the reference of the extension record, text), contract_id (text), extension_months (installments deferred, integer), new_next_due_date and new_maturity_date (the YYYY-MM-DD next due date and final installment date the extension sets), fee_treatment (fee_assessed when a fee was booked, fee_waived when none), extension_fee_usd (the fee booked, USD number with 2 decimal places), fee_txn_id (ledger reference of the fee entry, empty text when no fee was booked) and status (the text applied, meaning the extension is in effect).
    """
    contract = (ctx.find("contracts", contract_id=contract_id) or [{}])[0]
    agreement = (ctx.find("contract_service_requests", service_request_id=service_request_id) or [{}])[0]
    months = int(agreement.get("requested_extension_months") or 0)
    fee = round(float(extension_fee_usd), 2)
    today = ctx.now()[:10]
    old_next = contract.get("next_due_date", "")
    new_next = _Calendar.add_months(old_next, months) if old_next else ""
    new_maturity = _Calendar.add_months(contract["maturity_date"], months) if contract.get("maturity_date") else ""
    treatment = "fee_assessed" if fee > 0 else "fee_waived"
    eid = ctx.make_id("ext_", contract_id, service_request_id, extension_fee_usd)
    ctx.create("contract_servicing_events", eid, servicing_event_id=eid, contract_id=contract_id,
               customer_id=contract.get("customer_id", ""), event_type="contract_extension_granted",
               effective_date=today, service_request_id=service_request_id, old_due_day=0, new_due_day=0,
               old_next_due_date=old_next, new_next_due_date=new_next, extension_months=months,
               new_maturity_date=new_maturity, fee_treatment=treatment, scra_action="not_applicable",
               new_apr_pct=0.0, new_scheduled_payment_usd=0.0, quoted_payoff_usd=0.0,
               quote_good_through_date="", funds_final_date="", release_method="not_applicable")
    fee_txn = ""
    if fee > 0:
        fee_txn = ctx.make_id("xfee_", eid, fee)
        ctx.create("contract_transactions", fee_txn, contract_txn_id=fee_txn, contract_id=contract_id,
                   customer_id=contract.get("customer_id", ""), event_type="contract_fee_assessed",
                   txn_date=today, amount_usd=fee, fee_type="extension_fee", installment_due_date="",
                   related_txn_id=eid, **_LEDGER_BLANK)
    fees_due = round(float(contract.get("fees_due_usd") or 0.0) + fee, 2)
    ctx.update("contracts", contract_id, next_due_date=new_next, maturity_date=new_maturity,
               fees_due_usd=fees_due)
    ctx.update("contract_service_requests", service_request_id, request_status="applied")
    return str({"servicing_event_id": eid, "contract_id": contract_id, "extension_months": months,
                "new_next_due_date": new_next, "new_maturity_date": new_maturity,
                "fee_treatment": treatment, "extension_fee_usd": fee, "fee_txn_id": fee_txn,
                "status": "applied"})


@tool(owner="agent", rw="write")
def assess_returned_payment_fee_c98c0726(ctx: ToolContext, contract_id: str, related_txn_id: str,
                                        amount_usd: float) -> str:
    """Book a returned-payment fee on a borrower's retail installment contract for one payment the
    bank returned unpaid. One call adds a single returned-payment fee entry linked to that return,
    dated on the date the return was received, and raises the contract's fees due by the amount
    charged; the borrower sees the fee on the contract and in the fees owed. A receipt carrying the
    new ledger reference means the fee is booked.

    Args:
        contract_id: Id class — the contract reference number of the retail installment contract being charged, as returned by the contract lookup for the verified borrower.
        related_txn_id: Id class — the ledger reference number of the return entry (the returned-payment record) the fee is charged for, as returned by the contract money-history lookup.
        amount_usd: Fixed-format class — the returned-payment fee amount in USD, 2 decimal places, 0.00 or more; stored rounded half-up to the cent exactly as passed.

    Returns:
        A dictionary rendered as text with: contract_txn_id (ledger reference of the new fee entry, text), contract_id (text), related_txn_id (the return the fee is linked to, text), txn_date (YYYY-MM-DD date the fee is dated, the date the return was received), amount_usd (the fee booked, USD number with 2 decimal places), fees_due_usd (the contract's fees due including this fee, USD number with 2 decimal places) and status (the text booked, meaning the fee is now owed).
    """
    contract = (ctx.find("contracts", contract_id=contract_id) or [{}])[0]
    returned = (ctx.find("contract_transactions", contract_txn_id=related_txn_id) or [{}])[0]
    amount = round(float(amount_usd), 2)
    dated = returned.get("txn_date") or ctx.now()[:10]
    rid = ctx.make_id("rpf_", contract_id, related_txn_id, amount_usd)
    ctx.create("contract_transactions", rid, contract_txn_id=rid, contract_id=contract_id,
               customer_id=contract.get("customer_id", ""), event_type="contract_fee_assessed",
               txn_date=dated, amount_usd=amount, fee_type="returned_payment_fee", installment_due_date="",
               related_txn_id=related_txn_id, **_LEDGER_BLANK)
    fees_due = round(float(contract.get("fees_due_usd") or 0.0) + amount, 2)
    ctx.update("contracts", contract_id, fees_due_usd=fees_due)
    return str({"contract_txn_id": rid, "contract_id": contract_id, "related_txn_id": related_txn_id,
                "txn_date": dated, "amount_usd": amount, "fees_due_usd": fees_due, "status": "booked"})


@tool(owner="agent", rw="write")
def issue_payoff_quote_f4f38627(ctx: ToolContext, contract_id: str, quote_good_through_date: str,
                                quoted_payoff_usd: float) -> str:
    """Issue a payoff statement on a borrower's retail installment contract. One call records a
    payoff quote dated today stating the payoff figure and the last date that figure is good
    through; no balance, fee or due date on the contract changes. The borrower can be given the
    figure and the good-through date shown on the receipt, which means the statement is on file.

    Args:
        contract_id: Id class — the contract reference number of the retail installment contract the statement is for, as returned by the contract lookup.
        quote_good_through_date: Fixed-format class — the last date the quoted figure pays the contract in full, written YYYY-MM-DD, a calendar date with no time or time zone; never empty for a statement.
        quoted_payoff_usd: Fixed-format class — the payoff figure stated, in USD, 2 decimal places, 0.00 when not applicable; stored rounded half-up to the cent exactly as passed.

    Returns:
        A dictionary rendered as text with: servicing_event_id (reference of the payoff statement record, text), contract_id (text), effective_date (YYYY-MM-DD quote date), quote_good_through_date (YYYY-MM-DD), quoted_payoff_usd (the figure stated, USD number with 2 decimal places) and status (the text issued, meaning the statement is on file).
    """
    contract = (ctx.find("contracts", contract_id=contract_id) or [{}])[0]
    figure = round(float(quoted_payoff_usd), 2)
    today = ctx.now()[:10]
    eid = ctx.make_id("poq_", contract_id, quote_good_through_date, quoted_payoff_usd)
    ctx.create("contract_servicing_events", eid, servicing_event_id=eid, contract_id=contract_id,
               customer_id=contract.get("customer_id", ""), event_type="contract_payoff_quoted",
               effective_date=today, service_request_id=None, old_due_day=0, new_due_day=0,
               old_next_due_date="", new_next_due_date="", extension_months=0, new_maturity_date="",
               fee_treatment="not_applicable", scra_action="not_applicable", new_apr_pct=0.0,
               new_scheduled_payment_usd=0.0, quoted_payoff_usd=figure,
               quote_good_through_date=quote_good_through_date, funds_final_date="",
               release_method="not_applicable")
    return str({"servicing_event_id": eid, "contract_id": contract_id, "effective_date": today,
                "quote_good_through_date": quote_good_through_date, "quoted_payoff_usd": figure,
                "status": "issued"})


@tool(owner="user", rw="write")
def authorize_payoff_payment_7f0b790b(ctx: ToolContext, contract_id: str, payment_channel: str,
                                      amount_usd: float) -> str:
    """The borrower authorizes a payment from their own funds that pays their retail installment
    contract off in full today. One call posts a payoff payment dated today for the amount given:
    its principal portion clears the principal balance, its fee portion settles all fees due and
    the rest is its interest portion; the contract's balances go to zero, the contract is closed as
    paid off by the borrower, and the fee settlement is recorded. The borrower sees the payment and
    the closed contract; a receipt carrying the payment reference and the paid_off status means the
    payoff has posted.

    Args:
        contract_id: Id class — the contract reference number of the retail installment contract being paid off, as returned by the contract lookup or quoted on the payoff statement.
        payment_channel: Enum class — how the borrower pays: ach_autopay when the money is drawn by the borrower's recurring automatic draft; ach_self_service when the borrower schedules a one-time bank draft through the phone line, website or app; ach_agent when the borrower gives a live representative their bank account for a one-time draft; debit_card_self_service when the borrower pays by debit card through the phone line, website or app; debit_card_agent when the borrower gives a live representative a debit card; moneygram when the borrower sends a MoneyGram payment; check_mail when the borrower mails a personal check; wire_transfer when the borrower's bank sends a wire; certified_funds when the borrower sends a cashier's check or money order; third_party_remittance when an insurer, auction or other third party remits the funds; not_applicable when no payment channel applies, never for a payoff.
        amount_usd: Fixed-format class — the payoff amount paid in USD, 2 decimal places, 0.00 or more; stored rounded half-up to the cent exactly as passed.

    Returns:
        A dictionary rendered as text with: contract_txn_id (reference of the payoff payment, text), contract_id (text), txn_date (YYYY-MM-DD posting date), amount_usd (amount paid, USD number with 2 decimal places), principal_applied_usd, fees_applied_usd and interest_applied_usd (its portions, USD numbers with 2 decimal places), status (the text paid_off, meaning the contract is closed as paid in full) and closed_date (YYYY-MM-DD).
    """
    contract = (ctx.find("contracts", contract_id=contract_id) or [{}])[0]
    amount = round(float(amount_usd), 2)
    principal = round(float(contract.get("principal_balance_usd") or 0.0), 2)
    fees = round(float(contract.get("fees_due_usd") or 0.0), 2)
    interest = round(amount - principal - fees, 2)
    today = ctx.now()[:10]
    pid = ctx.make_id("pay_", contract_id, payment_channel, amount_usd)
    ctx.create("contract_transactions", pid, contract_txn_id=pid, contract_id=contract_id,
               customer_id=contract.get("customer_id", ""), event_type="contract_payment_posted",
               txn_date=today, amount_usd=amount, payment_channel=payment_channel, payment_type="payoff",
               interest_applied_usd=interest, principal_applied_usd=principal, fees_applied_usd=fees,
               fee_type="not_applicable", installment_due_date="", related_txn_id="",
               return_reason="not_applicable", waiver_reason="not_applicable",
               ancillary_source="not_applicable", source_record_id="", fee_settlement_method="not_applicable")
    if fees > 0:
        fid = ctx.make_id("pfs_", pid, fees)
        ctx.create("contract_transactions", fid, contract_txn_id=fid, contract_id=contract_id,
                   customer_id=contract.get("customer_id", ""), event_type="contract_fee_paid",
                   txn_date=today, amount_usd=fees, payment_channel="not_applicable", payment_type="not_applicable",
                   interest_applied_usd=0.0, principal_applied_usd=0.0, fees_applied_usd=0.0,
                   fee_type="not_applicable", installment_due_date="", related_txn_id=pid,
                   return_reason="not_applicable", waiver_reason="not_applicable",
                   ancillary_source="not_applicable", source_record_id="", fee_settlement_method="payment")
    ctx.update("contracts", contract_id, principal_balance_usd=0.0, fees_due_usd=0.0, unpaid_interest_usd=0.0,
               partial_installment_credit_usd=0.0, status="paid_off", closed_date=today,
               payoff_reason="borrower_payoff")
    return str({"contract_txn_id": pid, "contract_id": contract_id, "txn_date": today, "amount_usd": amount,
                "principal_applied_usd": principal, "fees_applied_usd": fees, "interest_applied_usd": interest,
                "status": "paid_off", "closed_date": today})

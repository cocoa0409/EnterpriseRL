"""Hidden task tools for the disclosures_conditions_and_application_fees difficulty of
env_0059_residential_mortgage_lender (Larkspur Home Lending, category loan).

Each tool performs exactly one atomic write on a mortgage loan file's records with the values the
caller passes in; none of them checks eligibility, ordering or amounts. Names are registered only
in loan.extended.yaml (extended_policies.target_tool) and are reached through unlock_* -> call_*.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def authorize_credit_report_repull_408eaf54(ctx: ToolContext, loan_file_id: str, customer_id: str, borrower_count: int,
                                            amount: float, payment_method: str) -> str:
    """The borrower personally authorizes Larkspur to pull a new tri-merge credit report on their own mortgage loan file and pays the credit report charge for that pull. One call books one credit report fee charge on the loan file's up-front fee history for the amount given, charged today to the card or bank account the borrower chooses, and raises the file's balance of borrower-paid up-front fees by that amount. Afterwards the borrower and the agent can see the new charge, with its amount, date and payment method, in the file's fee history. A receipt naming the new fee entry confirms the pull was authorized and paid.

    Args:
        loan_file_id: Id class — the reference number of the borrower's mortgage loan file the new credit pull is for, as returned by the loan file lookup.
        customer_id: Id class — the customer reference number of the borrower who authorizes and pays for the pull, as returned by the customer lookup.
        borrower_count: Fixed-format class — the number of borrowers on the loan file whose credit is pulled by this authorization; format integer, persons (a whole number of 1 or more, no decimals).
        amount: Fixed-format class — the credit report charge the borrower pays for this pull; US dollars as a number of 0.00 or more with exactly 2 decimal places (cents), already rounded to the cent, no currency symbol (0.00 records a pull whose cost the borrower does not bear).
        payment_method: Enum class — how the borrower pays the charge, one of: "debit_card" — the borrower pays with a debit card; "credit_card" — the borrower pays with a credit card; "ach_debit" — the borrower pays by a direct debit from a bank checking or savings account; "closing_disclosure_credit" — a credit line on the Closing Disclosure, which moves no money from the borrower and applies only when an earlier fee is credited back at closing, never when a charge is paid.

    Returns:
        A one-line confirmation string of the form "Credit report pull authorized: fee entry <entry_id> on loan file <loan_file_id>, <borrower_count> borrower(s), <amount> USD charged by <payment_method> on <YYYY-MM-DD>." where entry_id is the new fee entry's reference number (text), borrower_count is the integer passed in, amount is the dollar amount with 2 decimals, payment_method is the value passed in and the date is today's date. Receiving this line means the charge is booked on the file.
    """
    rows = ctx.find("loan_files", loan_file_id=loan_file_id)
    amt = round(float(amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("lfe_", loan_file_id, customer_id, borrower_count, amt, payment_method, today)
    ctx.create("loan_fee_ledger", rid, loan_fee_entry_id=rid, loan_file_id=loan_file_id, customer_id=customer_id,
               event_type="loan_credit_report_fee_charged", fee_code="credit_report_fee", amount=amt,
               borrower_count=int(borrower_count), entry_date=today, payment_method=payment_method,
               original_fee_entry_id="", entry_reason="new_charge")
    if rows:
        balance = round(float(rows[0].get("prepaid_fee_balance") or 0) + amt, 2)
        ctx.update("loan_files", loan_file_id, prepaid_fee_balance=balance)
    return (f"Credit report pull authorized: fee entry {rid} on loan file {loan_file_id}, {int(borrower_count)} borrower(s), "
            f"{amt:.2f} USD charged by {payment_method} on {today}.")


@tool(owner="agent", rw="write")
def issue_corrected_closing_disclosure_de3eb1f4(ctx: ToolContext, loan_file_id: str, disclosure_sequence: int,
                                                coc_reason: str, coc_documented_date: str,
                                                nonrecurring_closing_costs: float) -> str:
    """Issue a corrected Closing Disclosure on a mortgage loan file before the loan is signed, restating the borrower-paid nonrecurring closing costs. One call adds one corrected Closing Disclosure to the file's disclosure history, dated today and sent to the borrower through the e-sign portal, carrying the sequence number, the changed-circumstance reason and its documented date, and the nonrecurring closing costs given; its receipt date stays empty until the borrower acknowledges it in the portal. The borrower can then open the corrected Closing Disclosure in the portal. A receipt naming the new disclosure confirms it was issued.

    Args:
        loan_file_id: Id class — the reference number of the mortgage loan file the corrected Closing Disclosure is issued on, as returned by the loan file lookup.
        disclosure_sequence: Fixed-format class — the ordinal of this Closing Disclosure among the Closing Disclosures on the file (1 for the first, 2 for the first correction, and so on); format integer, ordinal — the value is an integer, no decimals.
        coc_reason: Enum class — the changed circumstance the correction relies on, one of: "none" — no changed circumstance is relied on; "borrower_requested_change" — a change to the loan or the transaction that the borrower asked for; "rate_lock" — the rate was locked after a floating disclosure; "rate_lock_extension" — a lock extension the borrower requested; "relock" — a relock the borrower requested; "appraised_value_change" — the appraised value differs from the value on the application; "loan_amount_change" — the loan amount changed; "program_change" — the file moved to another loan program; "third_party_charge_increase_from_new_information" — a third-party charge rose because of new information about the borrower or the property; "delayed_settlement_over_60_days" — settlement on a new-construction purchase is delayed more than 60 days past the disclosed date.
        coc_documented_date: Fixed-format class — the date Larkspur received the information establishing the changed circumstance, as YYYY-MM-DD (calendar date, no time, no time zone); an empty string "" when coc_reason is "none".
        nonrecurring_closing_costs: Fixed-format class — the borrower-paid one-time closing costs disclosed on the corrected Closing Disclosure (Loan Costs sections A, B and C plus taxes and government fees, excluding discount points); US dollars as a positive number with exactly 2 decimal places (cents), already rounded to the cent, no currency symbol.

    Returns:
        A one-line confirmation string of the form "Corrected Closing Disclosure <disclosure_id> issued on loan file <loan_file_id>: sequence <disclosure_sequence>, changed circumstance <coc_reason> documented <coc_documented_date>, nonrecurring closing costs <amount> USD, issued <YYYY-MM-DD> via esign_portal." where disclosure_id is the new disclosure's reference number (text), the sequence is the integer passed in, the reason and date are the values passed in, the amount has 2 decimals and the issue date is today's date. Receiving this line means the corrected Closing Disclosure is on the file.
    """
    rows = ctx.find("loan_files", loan_file_id=loan_file_id)
    customer_id = rows[0].get("customer_id", "") if rows else ""
    amt = round(float(nonrecurring_closing_costs), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("ldc_", loan_file_id, disclosure_sequence, coc_reason, coc_documented_date, amt)
    ctx.create("loan_disclosures", rid, disclosure_id=rid, loan_file_id=loan_file_id, customer_id=customer_id,
               event_type="loan_cd_corrected", disclosure_form="closing_disclosure",
               disclosure_sequence=int(disclosure_sequence), issued_date=today, delivery_method="esign_portal",
               received_date="", coc_reason=coc_reason, coc_documented_date=coc_documented_date,
               nonrecurring_closing_costs=amt)
    return (f"Corrected Closing Disclosure {rid} issued on loan file {loan_file_id}: sequence {int(disclosure_sequence)}, "
            f"changed circumstance {coc_reason} documented {coc_documented_date}, nonrecurring closing costs {amt:.2f} USD, "
            f"issued {today} via esign_portal.")


@tool(owner="user", rw="write")
def pay_application_fee_6c3f9eab(ctx: ToolContext, loan_file_id: str, customer_id: str, amount: float,
                                 payment_method: str) -> str:
    """The borrower personally pays the application fee on their own mortgage loan file. One call books one application fee collection on the loan file's up-front fee history for the amount given, charged today to the card or bank account the borrower chooses, and raises the file's balance of borrower-paid up-front fees by that amount. Afterwards the borrower and the agent can see the collection, with its amount, date and payment method, in the file's fee history. A receipt naming the new fee entry confirms the fee was paid.

    Args:
        loan_file_id: Id class — the reference number of the borrower's mortgage loan file the application fee is paid on, as returned by the loan file lookup.
        customer_id: Id class — the customer reference number of the borrower who pays, as returned by the customer lookup.
        amount: Fixed-format class — the application fee the borrower pays; US dollars as a number of 0.00 or more with exactly 2 decimal places (cents), already rounded to the cent, no currency symbol (0.00 records a fee settled in full by discounts).
        payment_method: Enum class — how the borrower pays, one of: "debit_card" — the borrower pays with a debit card; "credit_card" — the borrower pays with a credit card; "ach_debit" — the borrower pays by a direct debit from a bank checking or savings account; "closing_disclosure_credit" — a credit line on the Closing Disclosure, which moves no money from the borrower and applies only when an earlier fee is credited back at closing, never when a fee is paid.

    Returns:
        A one-line confirmation string of the form "Application fee paid: fee entry <entry_id> on loan file <loan_file_id>, <amount> USD charged by <payment_method> on <YYYY-MM-DD>." where entry_id is the new fee entry's reference number (text), amount is the dollar amount with 2 decimals, payment_method is the value passed in and the date is today's date. Receiving this line means the application fee is booked on the file.
    """
    rows = ctx.find("loan_files", loan_file_id=loan_file_id)
    amt = round(float(amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("lfe_", loan_file_id, customer_id, "application_fee", amt, payment_method, today)
    ctx.create("loan_fee_ledger", rid, loan_fee_entry_id=rid, loan_file_id=loan_file_id, customer_id=customer_id,
               event_type="loan_application_fee_collected", fee_code="application_fee", amount=amt, borrower_count=0,
               entry_date=today, payment_method=payment_method, original_fee_entry_id="", entry_reason="new_charge")
    if rows:
        balance = round(float(rows[0].get("prepaid_fee_balance") or 0) + amt, 2)
        ctx.update("loan_files", loan_file_id, prepaid_fee_balance=balance)
    return (f"Application fee paid: fee entry {rid} on loan file {loan_file_id}, {amt:.2f} USD charged by "
            f"{payment_method} on {today}.")


@tool(owner="agent", rw="write")
def issue_revised_loan_estimate_22df4f86(ctx: ToolContext, loan_file_id: str, disclosure_sequence: int, coc_reason: str,
                                         coc_documented_date: str, zero_tolerance_total: float) -> str:
    """Issue a revised Loan Estimate on a mortgage loan file for a changed circumstance, restating the total of the charges that may not increase at all (the zero-tolerance charges). One call adds one revised Loan Estimate to the file's disclosure history, dated today and sent to the borrower through the e-sign portal, carrying the sequence number, the changed-circumstance reason and its documented date, and the zero-tolerance total given; its receipt date stays empty until the borrower acknowledges it in the portal. The borrower can then open the revised Loan Estimate in the portal. A receipt naming the new disclosure confirms it was issued.

    Args:
        loan_file_id: Id class — the reference number of the mortgage loan file the revised Loan Estimate is issued on, as returned by the loan file lookup.
        disclosure_sequence: Fixed-format class — the ordinal of this Loan Estimate among the Loan Estimates on the file (1 for the initial one, 2 for the first revision, and so on); format integer, ordinal — the value is an integer, no decimals.
        coc_reason: Enum class — the changed circumstance the revision relies on, one of: "none" — no changed circumstance is relied on; "borrower_requested_change" — a change the borrower asked for other than a lock action; "rate_lock" — the rate was locked after a floating disclosure; "rate_lock_extension" — a lock extension the borrower requested; "relock" — a relock the borrower requested; "appraised_value_change" — the appraised value differs from the value on the application; "loan_amount_change" — the loan amount changed; "program_change" — the file moved to another loan program; "third_party_charge_increase_from_new_information" — a third-party charge rose because of new information about the borrower or the property; "delayed_settlement_over_60_days" — settlement on a new-construction purchase is delayed more than 60 days past the disclosed date.
        coc_documented_date: Fixed-format class — the date Larkspur received the information establishing the changed circumstance, as YYYY-MM-DD (calendar date, no time, no time zone); an empty string "" when coc_reason is "none".
        zero_tolerance_total: Fixed-format class — the sum of the zero-tolerance charges disclosed on the revised Loan Estimate (Larkspur's own charges and the services the borrower could not shop for); US dollars as a positive number with exactly 2 decimal places (cents), already rounded to the cent, no currency symbol.

    Returns:
        A one-line confirmation string of the form "Revised Loan Estimate <disclosure_id> issued on loan file <loan_file_id>: sequence <disclosure_sequence>, changed circumstance <coc_reason> documented <coc_documented_date>, zero-tolerance total <amount> USD, issued <YYYY-MM-DD> via esign_portal." where disclosure_id is the new disclosure's reference number (text), the sequence is the integer passed in, the reason and date are the values passed in, the amount has 2 decimals and the issue date is today's date. Receiving this line means the revised Loan Estimate is on the file.
    """
    rows = ctx.find("loan_files", loan_file_id=loan_file_id)
    customer_id = rows[0].get("customer_id", "") if rows else ""
    amt = round(float(zero_tolerance_total), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("lle_", loan_file_id, disclosure_sequence, coc_reason, coc_documented_date, amt)
    ctx.create("loan_disclosures", rid, disclosure_id=rid, loan_file_id=loan_file_id, customer_id=customer_id,
               event_type="loan_le_revised", disclosure_form="loan_estimate", disclosure_sequence=int(disclosure_sequence),
               issued_date=today, delivery_method="esign_portal", received_date="", coc_reason=coc_reason,
               coc_documented_date=coc_documented_date, zero_tolerance_total=amt)
    return (f"Revised Loan Estimate {rid} issued on loan file {loan_file_id}: sequence {int(disclosure_sequence)}, "
            f"changed circumstance {coc_reason} documented {coc_documented_date}, zero-tolerance total {amt:.2f} USD, "
            f"issued {today} via esign_portal.")


@tool(owner="agent", rw="write")
def assess_tolerance_cure_d5e015cb(ctx: ToolContext, loan_file_id: str, tolerance_bucket: str, baseline_disclosure_id: str,
                                   final_disclosure_id: str, cure_amount: float, cure_method: str) -> str:
    """Book a TRID tolerance cure that Larkspur owes the borrower on a mortgage loan file. One call adds one assessed cure to the file's tolerance cure history, dated today, for the tolerance bucket, the baseline and measured disclosures, the amount and the delivery method given, and raises the file's balance of cures owed to the borrower by that amount. The borrower and the agent can then see the cure owed in the file's tolerance cure history. A receipt naming the new cure entry confirms it was booked.

    Args:
        loan_file_id: Id class — the reference number of the mortgage loan file the cure is owed on, as returned by the loan file lookup.
        tolerance_bucket: Enum class — the tolerance bucket the cure belongs to, one of: "zero_tolerance" — charges that may not increase at all (Larkspur's charges, transfer taxes, services the borrower could not shop for); "ten_percent_aggregate" — charges that together may increase by no more than ten percent (recording fees and shoppable services chosen from Larkspur's written provider list).
        baseline_disclosure_id: Id class — the reference number of the Loan Estimate whose amounts are the good-faith baseline, as listed in the file's disclosure history.
        final_disclosure_id: Id class — the reference number of the disclosure whose amounts are measured against the baseline, as listed in the file's disclosure history or returned when that disclosure was issued.
        cure_amount: Fixed-format class — the cure owed to the borrower; US dollars as a positive number with exactly 2 decimal places (cents), already rounded to the cent, no currency symbol.
        cure_method: Enum class — how the cure reaches the borrower, one of: "credit_at_closing" — given as a lender credit on the Closing Disclosure at closing; "post_closing_refund" — refunded to the borrower after the loan has closed, with a corrected Closing Disclosure.

    Returns:
        A one-line confirmation string of the form "Tolerance cure <cure_entry_id> assessed on loan file <loan_file_id>: <tolerance_bucket>, baseline <baseline_disclosure_id>, measured <final_disclosure_id>, <amount> USD by <cure_method> on <YYYY-MM-DD>." where cure_entry_id is the new cure entry's reference number (text), the bucket, ids and method are the values passed in, the amount has 2 decimals and the date is today's date. Receiving this line means the cure is booked as owed.
    """
    rows = ctx.find("loan_files", loan_file_id=loan_file_id)
    customer_id = rows[0].get("customer_id", "") if rows else ""
    amt = round(float(cure_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("ltc_", loan_file_id, tolerance_bucket, baseline_disclosure_id, final_disclosure_id, amt, cure_method)
    ctx.create("loan_tolerance_cures", rid, cure_entry_id=rid, loan_file_id=loan_file_id, customer_id=customer_id,
               event_type="loan_tolerance_cure_assessed", tolerance_bucket=tolerance_bucket,
               baseline_disclosure_id=baseline_disclosure_id, final_disclosure_id=final_disclosure_id, cure_amount=amt,
               cure_method=cure_method, cure_date=today, source_cure_entry_id="")
    if rows:
        balance = round(float(rows[0].get("tolerance_cure_balance") or 0) + amt, 2)
        ctx.update("loan_files", loan_file_id, tolerance_cure_balance=balance)
    return (f"Tolerance cure {rid} assessed on loan file {loan_file_id}: {tolerance_bucket}, baseline {baseline_disclosure_id}, "
            f"measured {final_disclosure_id}, {amt:.2f} USD by {cure_method} on {today}.")


@tool(owner="agent", rw="write")
def issue_closing_disclosure_6debf4ff(ctx: ToolContext, loan_file_id: str, issued_date: str, lender_credit_amount: float) -> str:
    """Issue the initial Closing Disclosure on a mortgage loan file with its total lender credits. One call adds the first Closing Disclosure (sequence 1, no changed circumstance) to the file's disclosure history, dated and released to the borrower's e-sign portal on the date given (today, or a later delivery date the disclosure is queued for), carrying the lender credit amount given; its receipt date stays empty until the borrower acknowledges it in the portal. The borrower can then open the Closing Disclosure in the portal. A receipt naming the new disclosure confirms it was issued.

    Args:
        loan_file_id: Id class — the reference number of the mortgage loan file the Closing Disclosure is issued on, as returned by the loan file lookup.
        issued_date: Fixed-format class — the date the Closing Disclosure is dated and delivered to the e-sign portal, as YYYY-MM-DD (calendar date, no time, no time zone); today's date or a later delivery date, never empty.
        lender_credit_amount: Fixed-format class — the total lender credits disclosed on the Closing Disclosure, shown as an amount of 0.00 or more; US dollars with exactly 2 decimal places (cents), already rounded to the cent, no currency symbol.

    Returns:
        A one-line confirmation string of the form "Closing Disclosure <disclosure_id> issued on loan file <loan_file_id>: sequence 1, lender credits <amount> USD, issued <YYYY-MM-DD> via esign_portal." where disclosure_id is the new disclosure's reference number (text), the amount has 2 decimals and the date is the issued_date passed in. Receiving this line means the Closing Disclosure is on the file with that date.
    """
    rows = ctx.find("loan_files", loan_file_id=loan_file_id)
    customer_id = rows[0].get("customer_id", "") if rows else ""
    amt = round(float(lender_credit_amount), 2)
    rid = ctx.make_id("lcd_", loan_file_id, issued_date, amt)
    ctx.create("loan_disclosures", rid, disclosure_id=rid, loan_file_id=loan_file_id, customer_id=customer_id,
               event_type="loan_cd_issued", disclosure_form="closing_disclosure", disclosure_sequence=1, issued_date=issued_date,
               delivery_method="esign_portal", received_date="", coc_reason="none", coc_documented_date="",
               lender_credit_amount=amt)
    return (f"Closing Disclosure {rid} issued on loan file {loan_file_id}: sequence 1, lender credits {amt:.2f} USD, "
            f"issued {issued_date} via esign_portal.")

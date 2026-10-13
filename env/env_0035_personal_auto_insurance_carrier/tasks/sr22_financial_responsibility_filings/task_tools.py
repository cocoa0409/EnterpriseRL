"""Hidden task tools for env_0035_personal_auto_insurance_carrier / sr22_financial_responsibility_filings.
Output of the erl-task-instantiate skill.
Path: env/env_0035_personal_auto_insurance_carrier/tasks/sr22_financial_responsibility_filings/task_tools.py

Each tool performs one atomic financial-responsibility filing action and books the filing charge the
agent has already worked out. No tool judges eligibility, timing or order; no tool computes a charge.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def restore_certificate_8ba85022(ctx: ToolContext, filing_id: str, reinstatement_charge: float) -> str:
    """Restore an SR-22 or FR-44 certificate whose SR-26 cancellation notice is still pending, by
    sending the state a reinstatement filing and booking its reinstatement filing charge.

    One call puts the filing back to the accepted status, clears the pending SR-26 effective date, records
    one reinstatement transmission to the ordering state under a new transmission confirmation number, and
    records one filing charge with the reason reinstatement filing on that transmission, in the amount
    given. The customer sees the certificate shown as accepted again and the charge on the filing history.

    Args:
        filing_id: Id class — the filing reference number of the certificate being restored, as returned
            by the filing lookup for the household.
        reinstatement_charge: Fixed-format class — the reinstatement filing charge to book, in USD, a
            non-negative amount with 2 decimal places (rounded to the cent on entry).

    Returns:
        A confirmation sentence (string) naming the filing reference number, the status accepted, the new
        transmission confirmation number of the reinstatement filing (text beginning with SRT-), and the
        charge booked in USD with 2 decimal places; receiving it means the restoration and its charge were
        recorded.
    """
    today = ctx.now()[:10]
    found = ctx.find("sr22_filings", filing_id=filing_id)
    filing = found[0] if found else {}
    trn = ctx.make_id("SRT-", filing_id, "reinstatement", today, reinstatement_charge)
    ctx.update("sr22_filings", filing_id, status="accepted", sr26_effective_date="")
    tid = ctx.make_id("sxl_", filing_id, "transmission", trn)
    ctx.create("sr22_ledger", tid, sr22_entry_id=tid, filing_id=filing_id,
               customer_id=filing.get("customer_id", ""), event_type="sr22_transmission",
               transmission_number=trn, transmission_type="reinstatement",
               transmitted_date=today, entry_date=today)
    fid = ctx.make_id("sxl_", filing_id, "fee", trn, reinstatement_charge)
    ctx.create("sr22_ledger", fid, sr22_entry_id=fid, filing_id=filing_id,
               customer_id=filing.get("customer_id", ""), event_type="sr22_fee_assessed",
               fee_reason="reinstatement_filing", transmission_number=trn,
               fee_amount=round(float(reinstatement_charge), 2), entry_date=today)
    return (f"Filing {filing_id} restored to accepted; reinstatement filing transmitted under {trn}; "
            f"charge {round(float(reinstatement_charge), 2):.2f} USD booked.")


@tool(owner="agent", rw="write")
def amend_certificate_vehicles_869f2144(ctx: ToolContext, filing_id: str, endorsement_id: str,
                                        vehicle_amendment_charge: float) -> str:
    """Send the ordering state an amended certificate that updates the vehicle schedule printed on an
    owner certificate to match a policy vehicle endorsement, and book its vehicle amendment charge.

    One call records one amendment entry with the reason vehicle change tied to the policy endorsement
    given, one amendment transmission to the state under a new transmission confirmation number, and one
    filing charge with the reason amended filing on that transmission, in the amount given. The filing's
    status does not change. The customer sees the amendment and its charge on the filing history.

    Args:
        filing_id: Id class — the filing reference number of the certificate being amended, as returned by
            the filing lookup for the household.
        endorsement_id: Id class — the transaction reference number of the policy vehicle endorsement (an
            added, replaced or removed vehicle) that the amendment reports, as returned by the policy
            transaction history.
        vehicle_amendment_charge: Fixed-format class — the vehicle amendment charge to book, in USD, a
            non-negative amount with 2 decimal places (rounded to the cent on entry).

    Returns:
        A confirmation sentence (string) naming the filing reference number, the endorsement reported, the
        new transmission confirmation number of the amendment (text beginning with SRT-) and the charge
        booked in USD with 2 decimal places; receiving it means the amendment and its charge were recorded.
    """
    today = ctx.now()[:10]
    found = ctx.find("sr22_filings", filing_id=filing_id)
    filing = found[0] if found else {}
    cust = filing.get("customer_id", "")
    trn = ctx.make_id("SRT-", filing_id, "vehicle_change", endorsement_id, today, vehicle_amendment_charge)
    aid = ctx.make_id("sxl_", filing_id, "amendment", trn, endorsement_id)
    ctx.create("sr22_ledger", aid, sr22_entry_id=aid, filing_id=filing_id, customer_id=cust,
               event_type="sr22_amended_filing", amendment_reason="vehicle_change",
               transmission_number=trn, source_transaction_id=endorsement_id, entry_date=today)
    tid = ctx.make_id("sxl_", filing_id, "transmission", trn)
    ctx.create("sr22_ledger", tid, sr22_entry_id=tid, filing_id=filing_id, customer_id=cust,
               event_type="sr22_transmission", transmission_number=trn, transmission_type="amendment",
               transmitted_date=today, entry_date=today)
    fid = ctx.make_id("sxl_", filing_id, "fee", trn, vehicle_amendment_charge)
    ctx.create("sr22_ledger", fid, sr22_entry_id=fid, filing_id=filing_id, customer_id=cust,
               event_type="sr22_fee_assessed", fee_reason="amended_filing", transmission_number=trn,
               fee_amount=round(float(vehicle_amendment_charge), 2), entry_date=today)
    return (f"Vehicle amendment for filing {filing_id} (endorsement {endorsement_id}) transmitted under {trn}; "
            f"charge {round(float(vehicle_amendment_charge), 2):.2f} USD booked.")


@tool(owner="agent", rw="write")
def amend_certificate_address_1c393d15(ctx: ToolContext, filing_id: str, address_amendment_charge: float) -> str:
    """Send the ordering state an amended certificate that updates the mailing address printed on a
    certificate to match the household's new mailing address, and book its address amendment charge.

    One call records one amendment entry with the reason address change, one amendment transmission to the
    state under a new transmission confirmation number, and one filing charge with the reason amended
    filing on that transmission, in the amount given. The filing's status does not change. The customer
    sees the amendment and its charge on the filing history.

    Args:
        filing_id: Id class — the filing reference number of the certificate being amended, as returned by
            the filing lookup for the household.
        address_amendment_charge: Fixed-format class — the address amendment charge to book, in USD, a
            non-negative amount with 2 decimal places (rounded to the cent on entry).

    Returns:
        A confirmation sentence (string) naming the filing reference number, the new transmission
        confirmation number of the amendment (text beginning with SRT-) and the charge booked in USD with 2
        decimal places; receiving it means the amendment and its charge were recorded.
    """
    today = ctx.now()[:10]
    found = ctx.find("sr22_filings", filing_id=filing_id)
    filing = found[0] if found else {}
    cust = filing.get("customer_id", "")
    trn = ctx.make_id("SRT-", filing_id, "address_change", today, address_amendment_charge)
    aid = ctx.make_id("sxl_", filing_id, "amendment", trn)
    ctx.create("sr22_ledger", aid, sr22_entry_id=aid, filing_id=filing_id, customer_id=cust,
               event_type="sr22_amended_filing", amendment_reason="address_change",
               transmission_number=trn, entry_date=today)
    tid = ctx.make_id("sxl_", filing_id, "transmission", trn)
    ctx.create("sr22_ledger", tid, sr22_entry_id=tid, filing_id=filing_id, customer_id=cust,
               event_type="sr22_transmission", transmission_number=trn, transmission_type="amendment",
               transmitted_date=today, entry_date=today)
    fid = ctx.make_id("sxl_", filing_id, "fee", trn, address_amendment_charge)
    ctx.create("sr22_ledger", fid, sr22_entry_id=fid, filing_id=filing_id, customer_id=cust,
               event_type="sr22_fee_assessed", fee_reason="amended_filing", transmission_number=trn,
               fee_amount=round(float(address_amendment_charge), 2), entry_date=today)
    return (f"Address amendment for filing {filing_id} transmitted under {trn}; "
            f"charge {round(float(address_amendment_charge), 2):.2f} USD booked.")


@tool(owner="user", rw="write")
def request_filing_release_10a5eab7(ctx: ToolContext, filing_id: str, order_id: str, release_charge: float) -> str:
    """Submit the customer's own request to end their SR-22 or FR-44 filing now that the state order's
    requirement is over, so that the certificate is released and a release notice goes to the state.

    One call sets the filing to released with today's date as its end date, records one release notice
    transmission to the ordering state under a new transmission confirmation number, and records one
    filing charge with the reason release notice on that transmission, in the amount given. The customer
    sees the filing shown as released and the charge on the filing history.

    Args:
        filing_id: Id class — the filing reference number of the certificate to release, as read out by
            the representative from the filing lookup.
        order_id: Id class — the reference number of the state order whose requirement has ended, as read
            out by the representative from the state order lookup.
        release_charge: Fixed-format class — the release charge the representative quoted, in USD, a
            non-negative amount with 2 decimal places (rounded to the cent on entry).

    Returns:
        A confirmation sentence (string) naming the filing reference number, the status released with its
        end date (YYYY-MM-DD), the transmission confirmation number of the release notice (text beginning
        with SRT-) and the charge booked in USD with 2 decimal places; receiving it means the release and its
        charge were recorded.
    """
    today = ctx.now()[:10]
    found = ctx.find("sr22_filings", filing_id=filing_id)
    filing = found[0] if found else {}
    cust = filing.get("customer_id", "")
    trn = ctx.make_id("SRT-", filing_id, "release_notice", order_id, today, release_charge)
    ctx.update("sr22_filings", filing_id, status="released", end_date=today)
    tid = ctx.make_id("sxl_", filing_id, "transmission", trn)
    ctx.create("sr22_ledger", tid, sr22_entry_id=tid, filing_id=filing_id, customer_id=cust,
               event_type="sr22_transmission", transmission_number=trn, transmission_type="release_notice",
               transmitted_date=today, entry_date=today)
    fid = ctx.make_id("sxl_", filing_id, "fee", trn, order_id, release_charge)
    ctx.create("sr22_ledger", fid, sr22_entry_id=fid, filing_id=filing_id, customer_id=cust,
               event_type="sr22_fee_assessed", fee_reason="release_notice", transmission_number=trn,
               fee_amount=round(float(release_charge), 2), entry_date=today)
    return (f"Filing {filing_id} released effective {today}; release notice transmitted under {trn}; "
            f"charge {round(float(release_charge), 2):.2f} USD booked.")


@tool(owner="user", rw="write")
def submit_filing_correction_4a6499e2(ctx: ToolContext, filing_id: str, transmission_number: str, corrected_item: str,
                                      corrected_value: str, refiling_charge: float) -> str:
    """Submit the customer's own corrected detail for an SR-22 or FR-44 certificate the state rejected,
    so that Cardinal records the correction and transmits the corrected certificate, and book its
    corrected refiling charge.

    One call replaces the corrected detail on the driver record (or, for a case number, on the state order
    record), sets the filing to filed, records one corrected refiling transmission to the ordering state
    under a new transmission confirmation number, and records one filing charge with the reason corrected
    refiling on that transmission, in the amount given. The customer sees the filing shown as filed again
    and the charge on the filing history.

    Args:
        filing_id: Id class — the filing reference number of the rejected certificate, as read out by the
            representative from the filing lookup.
        transmission_number: Id class — the transmission confirmation number of the transmission the state
            rejected, as read out by the representative from the filing history.
        corrected_item: Enum class — which detail the customer corrects, exactly one of: full_name when the
            state rejected the certificate for a name mismatch and the customer gives the full name as
            printed on the license; date_of_birth when the rejection was a date of birth mismatch and the
            customer gives the date of birth as YYYY-MM-DD; license_number when the rejection was a license
            number mismatch and the customer gives the license number as printed; case_number when the state
            could not find the case and the customer gives the case number from the state's order letter.
        corrected_value: Verbatim class — the corrected detail exactly as the customer reads it from the
            license or order letter, copied character for character with the same letters, digits, spaces and
            punctuation (verbatim).
        refiling_charge: Fixed-format class — the corrected refiling charge the representative quoted, in
            USD, a non-negative amount with 2 decimal places (rounded to the cent on entry).

    Returns:
        A confirmation sentence (string) naming the filing reference number, the corrected detail recorded,
        the status filed, the new transmission confirmation number of the corrected refiling (text beginning
        with SRT-) and the charge booked in USD with 2 decimal places; receiving it means the correction, the
        refiling and its charge were recorded.
    """
    today = ctx.now()[:10]
    found = ctx.find("sr22_filings", filing_id=filing_id)
    filing = found[0] if found else {}
    cust = filing.get("customer_id", "")
    if corrected_item == "case_number":
        ctx.update("state_orders", filing.get("order_id", ""), **{corrected_item: corrected_value})
    else:
        ctx.update("drivers", filing.get("driver_id", ""), **{corrected_item: corrected_value})
    trn = ctx.make_id("SRT-", filing_id, "corrected_refiling", transmission_number, corrected_item,
                      corrected_value, today, refiling_charge)
    ctx.update("sr22_filings", filing_id, status="filed")
    tid = ctx.make_id("sxl_", filing_id, "transmission", trn)
    ctx.create("sr22_ledger", tid, sr22_entry_id=tid, filing_id=filing_id, customer_id=cust,
               event_type="sr22_transmission", transmission_number=trn, transmission_type="corrected_refiling",
               transmitted_date=today, entry_date=today)
    fid = ctx.make_id("sxl_", filing_id, "fee", trn, refiling_charge)
    ctx.create("sr22_ledger", fid, sr22_entry_id=fid, filing_id=filing_id, customer_id=cust,
               event_type="sr22_fee_assessed", fee_reason="corrected_refiling", transmission_number=trn,
               fee_amount=round(float(refiling_charge), 2), entry_date=today)
    return (f"Correction of {corrected_item} recorded for filing {filing_id}; status filed; corrected certificate "
            f"transmitted under {trn}; charge {round(float(refiling_charge), 2):.2f} USD booked.")


@tool(owner="agent", rw="write")
def amend_certificate_policy_9772f7fb(ctx: ToolContext, filing_id: str, new_policy_id: str, issue_transaction_id: str,
                                      policy_amendment_charge: float) -> str:
    """Move an SR-22 or FR-44 certificate onto the household's replacement policy by sending the ordering
    state an amended certificate with the new policy number, and book its policy-number amendment charge.

    One call makes the filing certify the replacement policy given, records one amendment entry with the
    reason policy number change tied to the transaction that issued that policy, one amendment transmission
    to the state under a new transmission confirmation number, and one filing charge with the reason amended
    filing on that transmission, in the amount given. The filing's status does not change. The customer sees
    the certificate under the new policy and the charge on the filing history.

    Args:
        filing_id: Id class — the filing reference number of the certificate being moved, as returned by the
            filing lookup for the household.
        new_policy_id: Id class — the policy reference number of the replacement policy the certificate will
            certify, as returned by the policy lookup for the customer.
        issue_transaction_id: Id class — the transaction reference number of the full-term premium entry that
            issued the replacement policy, as returned by the policy transaction history.
        policy_amendment_charge: Fixed-format class — the policy-number amendment charge to book, in USD, a
            non-negative amount with 2 decimal places (rounded to the cent on entry).

    Returns:
        A confirmation sentence (string) naming the filing reference number, the replacement policy it now
        certifies, the new transmission confirmation number of the amendment (text beginning with SRT-) and
        the charge booked in USD with 2 decimal places; receiving it means the amendment and its charge were
        recorded.
    """
    today = ctx.now()[:10]
    found = ctx.find("sr22_filings", filing_id=filing_id)
    filing = found[0] if found else {}
    cust = filing.get("customer_id", "")
    trn = ctx.make_id("SRT-", filing_id, "policy_number_change", new_policy_id, issue_transaction_id, today,
                      policy_amendment_charge)
    ctx.update("sr22_filings", filing_id, policy_id=new_policy_id)
    aid = ctx.make_id("sxl_", filing_id, "amendment", trn, issue_transaction_id)
    ctx.create("sr22_ledger", aid, sr22_entry_id=aid, filing_id=filing_id, customer_id=cust,
               event_type="sr22_amended_filing", amendment_reason="policy_number_change",
               transmission_number=trn, source_transaction_id=issue_transaction_id, entry_date=today)
    tid = ctx.make_id("sxl_", filing_id, "transmission", trn)
    ctx.create("sr22_ledger", tid, sr22_entry_id=tid, filing_id=filing_id, customer_id=cust,
               event_type="sr22_transmission", transmission_number=trn, transmission_type="amendment",
               transmitted_date=today, entry_date=today)
    fid = ctx.make_id("sxl_", filing_id, "fee", trn, policy_amendment_charge)
    ctx.create("sr22_ledger", fid, sr22_entry_id=fid, filing_id=filing_id, customer_id=cust,
               event_type="sr22_fee_assessed", fee_reason="amended_filing", transmission_number=trn,
               fee_amount=round(float(policy_amendment_charge), 2), entry_date=today)
    return (f"Filing {filing_id} now certifies policy {new_policy_id}; policy-number amendment transmitted under "
            f"{trn}; charge {round(float(policy_amendment_charge), 2):.2f} USD booked.")


@tool(owner="agent", rw="write")
def amend_certificate_name_9daa06e9(ctx: ToolContext, filing_id: str, legal_name: str, name_amendment_charge: float) -> str:
    """Send the ordering state an amended certificate that carries the filed driver's new legal name,
    record that name on the filed driver's record, and book the name amendment charge.

    One call replaces the full name on the record of the driver the filing certifies, records one amendment
    entry with the reason name change, one amendment transmission to the state under a new transmission
    confirmation number, and one filing charge with the reason amended filing on that transmission, in the
    amount given. The filing's status does not change. The customer sees the new name on the driver record
    and the amendment and its charge on the filing history.

    Args:
        filing_id: Id class — the filing reference number of the certificate being amended, as returned by the
            filing lookup for the household.
        legal_name: Verbatim class — the filed driver's new full legal name exactly as the customer reads it
            from the reissued driver's license, copied character for character with the same spelling,
            spacing, capitalization and punctuation (verbatim).
        name_amendment_charge: Fixed-format class — the name amendment charge to book, in USD, a non-negative
            amount with 2 decimal places (rounded to the cent on entry).

    Returns:
        A confirmation sentence (string) naming the filing reference number, the name now on the driver record,
        the new transmission confirmation number of the amendment (text beginning with SRT-) and the charge
        booked in USD with 2 decimal places; receiving it means the amendment and its charge were recorded.
    """
    today = ctx.now()[:10]
    found = ctx.find("sr22_filings", filing_id=filing_id)
    filing = found[0] if found else {}
    cust = filing.get("customer_id", "")
    ctx.update("drivers", filing.get("driver_id", ""), full_name=legal_name)
    trn = ctx.make_id("SRT-", filing_id, "name_change", legal_name, today, name_amendment_charge)
    aid = ctx.make_id("sxl_", filing_id, "amendment", trn)
    ctx.create("sr22_ledger", aid, sr22_entry_id=aid, filing_id=filing_id, customer_id=cust,
               event_type="sr22_amended_filing", amendment_reason="name_change",
               transmission_number=trn, entry_date=today)
    tid = ctx.make_id("sxl_", filing_id, "transmission", trn)
    ctx.create("sr22_ledger", tid, sr22_entry_id=tid, filing_id=filing_id, customer_id=cust,
               event_type="sr22_transmission", transmission_number=trn, transmission_type="amendment",
               transmitted_date=today, entry_date=today)
    fid = ctx.make_id("sxl_", filing_id, "fee", trn, name_amendment_charge)
    ctx.create("sr22_ledger", fid, sr22_entry_id=fid, filing_id=filing_id, customer_id=cust,
               event_type="sr22_fee_assessed", fee_reason="amended_filing", transmission_number=trn,
               fee_amount=round(float(name_amendment_charge), 2), entry_date=today)
    return (f"Name amendment for filing {filing_id} transmitted under {trn}; driver record now reads {legal_name}; "
            f"charge {round(float(name_amendment_charge), 2):.2f} USD booked.")

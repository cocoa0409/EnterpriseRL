"""Hidden task tools of the lender_placed_flood_programs difficulty (Tidemark Lender-Placed Flood
Master Programs). Each tool performs one atomic, already-decided write on a lender's master
program; none of them judges eligibility, prerequisites or amounts."""

from erlbench import ToolContext, tool


class _Acct:
    """Account helpers that compute values only (no reads or writes)."""

    @staticmethod
    def month(stamp: str) -> str:
        return str(stamp)[:7]

    @staticmethod
    def day(stamp: str) -> str:
        return str(stamp)[:10]

    @staticmethod
    def number(prefix: str, rid: str) -> str:
        digits = str(int(rid[-10:], 16) % 1000000).zfill(6)
        return f"{prefix}5{digits}"


@tool(owner="user", rw="write")
def cancel_certificate_on_evidence_b90eab97(ctx: ToolContext, forceplaced_program_id: str, certificate_number: str,
                                            loan_number: str, evidence_policy_number: str, credit_basis: str,
                                            cancellation_effective_date: str, credit_amount: float) -> str:
    """The lender, as holder of the master policy, terminates the lender-placed flood coverage on one
    of its loans because the borrower's own flood policy has been confirmed. One call ends the named
    certificate for the reason that the borrower's coverage is confirmed, books the unearned-premium
    credit for that certificate to the lender's program account on the statement for the current
    month, and lowers the amount the lender owes on the program by the credit. On success the
    certificate shows as cancelled on the given effective date and the credit appears among the
    program's account entries, linked to this cancellation.

    Args:
        forceplaced_program_id: Id class — the reference number of the lender's master program the
            certificate sits under, as returned by the master program lookup.
        certificate_number: Verbatim class — the certificate number exactly as shown on the
            certificate's issue or renewal entry returned by the certificate lookup, copied character
            for character (verbatim).
        loan_number: Verbatim class — the lender's loan number exactly as shown on that certificate's
            entries, copied character for character (verbatim).
        evidence_policy_number: Verbatim class — the policy number of the borrower's own flood policy
            exactly as shown on the borrower evidence entry returned by the tracking lookup, copied
            character for character (verbatim).
        credit_basis: Enum class — how the credit is booked; exactly one of: FLAT_CANCEL (the
            cancellation takes effect on the start date of a certificate term, so every term the
            credit reaches is returned in whole); PRO_RATA_CANCEL (the cancellation takes effect on
            a date inside a certificate term, so that term is returned only for the part from the
            effective date onward).
        cancellation_effective_date: Fixed-format class — the date certificate coverage ends, as
            YYYY-MM-DD (calendar date, no time or time zone).
        credit_amount: Fixed-format class — the unearned-premium credit returned to the lender, in
            USD as a non-negative number with 2 decimal places (cents); the value given is
            rounded half to even to the cent on booking.

    Returns:
        A confirmation string naming the cancellation entry reference, the certificate number, the
        cancellation effective date, the credit booked in USD with 2 decimals and its
        statement month (YYYY-MM), the credit entry reference, and the program's amount owed net of
        the credit in USD with 2 decimals (negative means a credit balance due to the
        lender). The presence of both references indicates the certificate was cancelled and
        credited.
    """
    amt = round(float(credit_amount), 2)
    basis = "FLAT_CANCEL" if credit_basis == "FLAT_CANCEL" else "PRO_RATA_CANCEL"
    stamp = ctx.now()
    cid = ctx.make_id("fpc_", forceplaced_program_id, certificate_number, loan_number, evidence_policy_number,
                      credit_basis, cancellation_effective_date, amt)
    prog = ctx.find("forceplaced_programs", forceplaced_program_id=forceplaced_program_id)
    cust = prog[0].get("customer_id") if prog else ""
    ctx.create("forceplaced_certificates", cid, forceplaced_certificate_event_id=cid,
               forceplaced_program_id=forceplaced_program_id, customer_id=cust,
               event_type="forceplaced_certificate_cancelled", certificate_number=certificate_number,
               loan_number=loan_number, borrower_name="", property_address="", flood_zone="NONE",
               outstanding_principal_balance=0.0, insurable_value=0, borrower_existing_limit=0,
               required_amount=0, secured_contents_value=0, building_limit=0, contents_limit=0,
               lapse_date="", coverage_effective_date="", certificate_expiration_date="", annual_premium=0.0,
               cancellation_reason="BORROWER_COVERAGE_CONFIRMED",
               cancellation_effective_date=cancellation_effective_date, event_date=_Acct.day(stamp))
    bid = ctx.make_id("fpb_", cid, "credit")
    ctx.create("forceplaced_billing", bid, forceplaced_billing_id=bid, forceplaced_program_id=forceplaced_program_id,
               customer_id=cust, event_type="forceplaced_premium_credit", certificate_number=certificate_number,
               statement_month=_Acct.month(stamp), charge_basis=basis, amount=amt,
               posted_date=_Acct.day(stamp), payment_ref="", reference_id=cid)
    bal = round(float(prog[0].get("premium_balance") or 0) - amt, 2) if prog else -amt
    ctx.update("forceplaced_programs", forceplaced_program_id, premium_balance=bal)
    return (f"Certificate {certificate_number} cancelled (entry {cid}) effective {cancellation_effective_date}; "
            f"credit {amt:.2f} USD booked on statement {_Acct.month(stamp)} (entry {bid}); "
            f"program amount owed now {bal:.2f} USD.")


@tool(owner="agent", rw="write")
def renew_certificate_c91c4d46(ctx: ToolContext, forceplaced_program_id: str, certificate_number: str,
                               loan_number: str, outstanding_principal_balance: float, insurable_value: int,
                               required_amount: int, building_limit: int, renewal_rate_per_100: float,
                               coverage_effective_date: str, certificate_expiration_date: str,
                               annual_premium: float) -> str:
    """Renews one existing certificate of lender-placed flood coverage for a further term under the
    lender's master program. One call records the renewal of the named certificate with the balances
    reported for the loan, the mandatory purchase amount, the building limit, the new term dates and
    the premium for the new term, reports the program renewal rate supplied in its confirmation only
    (the rate is not stored on any entry), bills that premium to the lender's program account on the
    statement for the current month, and raises the amount the lender owes on the program by the
    premium. On success the certificate shows a renewal entry for the new term and the premium
    appears among the program's account entries as a renewal charge.

    Args:
        forceplaced_program_id: Id class — the reference number of the lender's master program the
            certificate sits under, as returned by the master program lookup.
        certificate_number: Verbatim class — the certificate number exactly as shown on the
            certificate's existing entries returned by the certificate lookup, copied character for
            character (verbatim).
        loan_number: Verbatim class — the lender's loan number exactly as shown on that certificate's
            entries, copied character for character (verbatim).
        outstanding_principal_balance: Fixed-format class — the unpaid principal balance of the loan
            as the lender reports it for the new term, in USD with 2 decimal places (cents).
        insurable_value: Fixed-format class — the building's replacement cost value as the lender
            reports it for the new term, in USD, whole dollars (integer, no cents).
        required_amount: Fixed-format class — the mandatory purchase amount for the loan for the new
            term, in USD, whole dollars (integer, no cents).
        building_limit: Fixed-format class — the certificate building limit for the new term, in
            USD, whole dollars (integer, no cents).
        renewal_rate_per_100: Fixed-format class — the program renewal rate for this renewal, reported back in the confirmation, in
            USD of annual premium per 100 USD of building limit, a positive number with 4 decimal
            places; the value given is rounded half to even to 4 decimal places.
        coverage_effective_date: Fixed-format class — the start date of the new term, as YYYY-MM-DD
            (calendar date, no time or time zone).
        certificate_expiration_date: Fixed-format class — the last day of the new term, as
            YYYY-MM-DD (calendar date, no time or time zone).
        annual_premium: Fixed-format class — the premium for the new term, in USD as a
            positive number with 2 decimal places (cents); the value given is rounded half to even
            to the cent on booking.

    Returns:
        A confirmation string naming the renewal entry reference, the certificate number, the new
        term as start and end dates (YYYY-MM-DD), the building limit in USD, whole dollars, the renewal
        rate applied (4 decimals), the premium
        billed in USD with 2 decimals and its statement month (YYYY-MM), the charge entry
        reference, and the program's amount owed net of the charge in USD with 2 decimals.
        The presence of both references indicates the renewal was recorded and billed.
    """
    prem = round(float(annual_premium), 2)
    stamp = ctx.now()
    rate = round(float(renewal_rate_per_100), 4)
    rid = ctx.make_id("fpr_", forceplaced_program_id, certificate_number, loan_number, outstanding_principal_balance,
                      insurable_value, required_amount, building_limit, rate, coverage_effective_date,
                      certificate_expiration_date, prem)
    prog = ctx.find("forceplaced_programs", forceplaced_program_id=forceplaced_program_id)
    cust = prog[0].get("customer_id") if prog else ""
    ctx.create("forceplaced_certificates", rid, forceplaced_certificate_event_id=rid,
               forceplaced_program_id=forceplaced_program_id, customer_id=cust,
               event_type="forceplaced_certificate_renewed", certificate_number=certificate_number,
               loan_number=loan_number, borrower_name="", property_address="", flood_zone="NONE",
               outstanding_principal_balance=round(float(outstanding_principal_balance), 2),
               insurable_value=int(insurable_value), borrower_existing_limit=0, required_amount=int(required_amount),
               secured_contents_value=0, building_limit=int(building_limit), contents_limit=0, lapse_date="",
               coverage_effective_date=coverage_effective_date, certificate_expiration_date=certificate_expiration_date,
               annual_premium=prem, cancellation_reason="NONE", cancellation_effective_date="",
               event_date=_Acct.day(stamp))
    bid = ctx.make_id("fpb_", rid, "renewal")
    ctx.create("forceplaced_billing", bid, forceplaced_billing_id=bid, forceplaced_program_id=forceplaced_program_id,
               customer_id=cust, event_type="forceplaced_premium_charged", certificate_number=certificate_number,
               statement_month=_Acct.month(stamp), charge_basis="RENEWAL", amount=prem,
               posted_date=_Acct.day(stamp), payment_ref="", reference_id="")
    bal = round(float(prog[0].get("premium_balance") or 0) + prem, 2) if prog else prem
    ctx.update("forceplaced_programs", forceplaced_program_id, premium_balance=bal)
    return (f"Certificate {certificate_number} renewed (entry {rid}) for {coverage_effective_date} to "
            f"{certificate_expiration_date}, building limit {int(building_limit)} USD at renewal rate {rate:.4f} per 100; "
            f"premium {prem:.2f} USD billed on "
            f"statement {_Acct.month(stamp)} (entry {bid}); program amount owed now {bal:.2f} USD.")


@tool(owner="agent", rw="write")
def issue_residential_certificate_c6c06832(ctx: ToolContext, forceplaced_program_id: str, loan_number: str,
                                           borrower_name: str, property_address: str, flood_zone: str,
                                           outstanding_principal_balance: float, insurable_value: int,
                                           required_amount: int, building_limit: int, lapse_date: str,
                                           coverage_effective_date: str, certificate_expiration_date: str,
                                           annual_premium: float) -> str:
    """Places lender-placed flood building coverage on one residential loan under the lender's master
    program. One call issues a new certificate for the loan with a newly assigned certificate number,
    recording the borrower, the building, its flood zone, the balances the lender reports, the
    mandatory purchase amount, the building limit, the date the borrower's coverage lapsed, the
    coverage dates and the annual premium; it bills that premium to the lender's program account on
    the statement for the current month as a new placement and raises the amount the lender owes on
    the program by the premium. On success the certificate can be found under the program with its
    certificate number and the premium appears among the program's account entries.

    Args:
        forceplaced_program_id: Id class — the reference number of the lender's master program that
            places the coverage, as returned by the master program lookup.
        loan_number: Verbatim class — the lender's loan number exactly as shown on the borrower
            notices returned by the tracking lookup, copied character for character (verbatim).
        borrower_name: Verbatim class — the borrower's full name exactly as the lender states it on
            the call, copied character for character (verbatim).
        property_address: Verbatim class — the street address of the mortgaged building exactly as
            the lender states it on the call, copied character for character (verbatim).
        flood_zone: Enum class — the flood zone on the lender's Standard Flood Hazard Determination
            Form for the building; exactly one of: A (special flood hazard area, no base flood
            elevation); AE (special flood hazard area with base flood elevations); AH (special flood
            hazard area of shallow ponding); AO (special flood hazard area of shallow sheet flow);
            AR (special flood hazard area during flood-control system restoration); A99 (special
            flood hazard area protected by a flood-control system under construction); V (coastal
            high hazard area, no base flood elevation); VE (coastal high hazard area with base flood
            elevations); B (moderate flood hazard area on older maps); C (minimal flood hazard area
            on older maps); X (moderate or minimal flood hazard area); D (undetermined flood hazard);
            NONE (no zone shown on the form).
        outstanding_principal_balance: Fixed-format class — the unpaid principal balance of the loan
            as the lender reports it, in USD with 2 decimal places (cents).
        insurable_value: Fixed-format class — the building's replacement cost value as the lender
            reports it, in USD, whole dollars (integer, no cents).
        required_amount: Fixed-format class — the mandatory purchase amount for the loan, in USD, whole dollars
            (integer, no cents).
        building_limit: Fixed-format class — the certificate building limit, in USD, whole dollars (integer, no
            cents).
        lapse_date: Fixed-format class — the date the borrower's own coverage lapsed or became
            insufficient, as YYYY-MM-DD (calendar date, no time or time zone).
        coverage_effective_date: Fixed-format class — the start date of certificate coverage, as
            YYYY-MM-DD (calendar date, no time or time zone).
        certificate_expiration_date: Fixed-format class — the last day of the certificate term, as
            YYYY-MM-DD (calendar date, no time or time zone).
        annual_premium: Fixed-format class — the annual premium of the certificate, in USD as a
            positive number with 2 decimal places (cents); the value given is rounded half to even
            to the cent on booking.

    Returns:
        A confirmation string giving the newly assigned certificate number (letters followed by
        digits), the issue entry reference, the loan number, the coverage dates (YYYY-MM-DD), the
        building limit in USD, whole dollars, the premium billed in USD with 2 decimals and
        its statement month (YYYY-MM), the charge entry reference, and the program's amount owed
        net of the charge in USD with 2 decimals. A certificate number in the reply
        indicates the certificate was issued and billed.
    """
    prem = round(float(annual_premium), 2)
    stamp = ctx.now()
    iid = ctx.make_id("fpi_", forceplaced_program_id, loan_number, borrower_name, property_address, flood_zone,
                      outstanding_principal_balance, insurable_value, required_amount, building_limit, lapse_date,
                      coverage_effective_date, certificate_expiration_date, prem)
    cert = _Acct.number("LP", iid)
    prog = ctx.find("forceplaced_programs", forceplaced_program_id=forceplaced_program_id)
    cust = prog[0].get("customer_id") if prog else ""
    ctx.create("forceplaced_certificates", iid, forceplaced_certificate_event_id=iid,
               forceplaced_program_id=forceplaced_program_id, customer_id=cust,
               event_type="forceplaced_certificate_issued", certificate_number=cert, loan_number=loan_number,
               borrower_name=borrower_name, property_address=property_address, flood_zone=flood_zone,
               outstanding_principal_balance=round(float(outstanding_principal_balance), 2),
               insurable_value=int(insurable_value), borrower_existing_limit=0, required_amount=int(required_amount),
               secured_contents_value=0, building_limit=int(building_limit), contents_limit=0, lapse_date=lapse_date,
               coverage_effective_date=coverage_effective_date, certificate_expiration_date=certificate_expiration_date,
               annual_premium=prem, cancellation_reason="NONE", cancellation_effective_date="",
               event_date=_Acct.day(stamp))
    bid = ctx.make_id("fpb_", iid, "placement")
    ctx.create("forceplaced_billing", bid, forceplaced_billing_id=bid, forceplaced_program_id=forceplaced_program_id,
               customer_id=cust, event_type="forceplaced_premium_charged", certificate_number=cert,
               statement_month=_Acct.month(stamp), charge_basis="NEW_PLACEMENT", amount=prem,
               posted_date=_Acct.day(stamp), payment_ref="", reference_id="")
    bal = round(float(prog[0].get("premium_balance") or 0) + prem, 2) if prog else prem
    ctx.update("forceplaced_programs", forceplaced_program_id, premium_balance=bal)
    return (f"Certificate {cert} issued (entry {iid}) on loan {loan_number}, coverage {coverage_effective_date} to "
            f"{certificate_expiration_date}, building limit {int(building_limit)} USD; premium {prem:.2f} USD billed on "
            f"statement {_Acct.month(stamp)} (entry {bid}); program amount owed now {bal:.2f} USD.")


@tool(owner="agent", rw="write")
def refund_program_credit_d16acbc2(ctx: ToolContext, forceplaced_program_id: str, refund_amount: float) -> str:
    """Pays back to the lender part or all of the credit balance standing on its master program
    account. One call books a refund disbursement to the lender on the program account on the
    statement for the current month, assigns it a new refund payment reference, and raises the
    amount the lender owes on the program by the refund (bringing a credit balance toward zero). On
    success the refund appears among the program's account entries with its payment reference.

    Args:
        forceplaced_program_id: Id class — the reference number of the lender's master program whose
            credit balance is refunded, as returned by the master program lookup.
        refund_amount: Fixed-format class — the amount paid back to the lender, in USD as a
            positive number with 2 decimal places (cents); the value given is rounded half to even
            to the cent on booking.

    Returns:
        A confirmation string giving the refund entry reference, the newly assigned refund payment
        reference (letters followed by digits), the amount refunded in USD with 2 decimals,
        its statement month (YYYY-MM), and the program's amount owed net of the refund in USD
        with 2 decimals (negative means a credit balance still due to the lender). A payment
        reference in the reply indicates the refund was issued.
    """
    amt = round(float(refund_amount), 2)
    stamp = ctx.now()
    bid = ctx.make_id("fpf_", forceplaced_program_id, amt)
    ref = _Acct.number("RF", bid)
    prog = ctx.find("forceplaced_programs", forceplaced_program_id=forceplaced_program_id)
    cust = prog[0].get("customer_id") if prog else ""
    ctx.create("forceplaced_billing", bid, forceplaced_billing_id=bid, forceplaced_program_id=forceplaced_program_id,
               customer_id=cust, event_type="forceplaced_refund_disbursed", certificate_number="",
               statement_month=_Acct.month(stamp), charge_basis="REFUND", amount=amt,
               posted_date=_Acct.day(stamp), payment_ref=ref, reference_id="")
    bal = round(float(prog[0].get("premium_balance") or 0) + amt, 2) if prog else amt
    ctx.update("forceplaced_programs", forceplaced_program_id, premium_balance=bal)
    return (f"Refund {ref} of {amt:.2f} USD issued to the lender (entry {bid}) on statement {_Acct.month(stamp)}; "
            f"program amount owed now {bal:.2f} USD.")


@tool(owner="user", rw="write")
def cancel_certificate_for_loan_event_5b69d826(ctx: ToolContext, forceplaced_program_id: str,
                                               certificate_number: str, loan_number: str, loan_event: str,
                                               cancellation_effective_date: str, credit_amount: float) -> str:
    """The lender, as holder of the master policy, ends the lender-placed flood coverage on one of its
    loans because of an event on the loan itself. One call cancels the named certificate for the
    stated loan event on the given effective date, books the unearned-premium credit for that
    certificate to the lender's program account on the statement for the current month (figured
    part-way through the term), and lowers the amount the lender owes on the program by the credit.
    On success the certificate shows as cancelled for that reason and the credit appears among the
    program's account entries, linked to this cancellation.

    Args:
        forceplaced_program_id: Id class — the reference number of the lender's master program the
            certificate sits under, as returned by the master program lookup.
        certificate_number: Verbatim class — the certificate number exactly as shown on the
            certificate's issue or renewal entry returned by the certificate lookup, copied
            character for character (verbatim).
        loan_number: Verbatim class — the lender's loan number exactly as shown on that certificate's
            entries, copied character for character (verbatim).
        loan_event: Enum class — the loan event ending the coverage; exactly one of:
            LOAN_PAID_OFF (the loan was paid in full); SERVICING_TRANSFERRED (servicing of the loan
            moved to another servicer); REMOVED_FROM_SFHA (a FEMA Letter of Map Amendment or Revision
            took the building out of the Special Flood Hazard Area).
        cancellation_effective_date: Fixed-format class — the date certificate coverage ends, as
            YYYY-MM-DD (calendar date, no time or time zone).
        credit_amount: Fixed-format class — the unearned-premium credit returned to the lender, in
            USD as a non-negative number with 2 decimal places (cents); the value given is
            rounded half to even to the cent on booking.

    Returns:
        A confirmation string naming the cancellation entry reference, the certificate number, the
        reason, the cancellation effective date, the credit booked in USD with 2 decimals
        and its statement month (YYYY-MM), the credit entry reference, and the program's amount owed
        net of the credit in USD with 2 decimals (negative means a credit balance due to
        the lender). The presence of both references indicates the certificate was cancelled and
        credited.
    """
    amt = round(float(credit_amount), 2)
    stamp = ctx.now()
    reason = loan_event if loan_event in ("LOAN_PAID_OFF", "SERVICING_TRANSFERRED", "REMOVED_FROM_SFHA") else "NONE"
    cid = ctx.make_id("fpc_", forceplaced_program_id, certificate_number, loan_number, loan_event,
                      cancellation_effective_date, amt)
    prog = ctx.find("forceplaced_programs", forceplaced_program_id=forceplaced_program_id)
    cust = prog[0].get("customer_id") if prog else ""
    ctx.create("forceplaced_certificates", cid, forceplaced_certificate_event_id=cid,
               forceplaced_program_id=forceplaced_program_id, customer_id=cust,
               event_type="forceplaced_certificate_cancelled", certificate_number=certificate_number,
               loan_number=loan_number, borrower_name="", property_address="", flood_zone="NONE",
               outstanding_principal_balance=0.0, insurable_value=0, borrower_existing_limit=0,
               required_amount=0, secured_contents_value=0, building_limit=0, contents_limit=0,
               lapse_date="", coverage_effective_date="", certificate_expiration_date="", annual_premium=0.0,
               cancellation_reason=reason,
               cancellation_effective_date=cancellation_effective_date, event_date=_Acct.day(stamp))
    bid = ctx.make_id("fpb_", cid, "credit")
    ctx.create("forceplaced_billing", bid, forceplaced_billing_id=bid, forceplaced_program_id=forceplaced_program_id,
               customer_id=cust, event_type="forceplaced_premium_credit", certificate_number=certificate_number,
               statement_month=_Acct.month(stamp), charge_basis="PRO_RATA_CANCEL", amount=amt,
               posted_date=_Acct.day(stamp), payment_ref="", reference_id=cid)
    bal = round(float(prog[0].get("premium_balance") or 0) - amt, 2) if prog else -amt
    ctx.update("forceplaced_programs", forceplaced_program_id, premium_balance=bal)
    return (f"Certificate {certificate_number} cancelled for {loan_event} (entry {cid}) effective "
            f"{cancellation_effective_date}; credit {amt:.2f} USD booked on statement {_Acct.month(stamp)} (entry {bid}); "
            f"program amount owed now {bal:.2f} USD.")


@tool(owner="agent", rw="write")
def issue_commercial_certificate_61c928bb(ctx: ToolContext, forceplaced_program_id: str, loan_number: str,
                                          borrower_name: str, property_address: str, flood_zone: str,
                                          outstanding_principal_balance: float, insurable_value: int,
                                          required_amount: int, building_limit: int, secured_contents_value: int,
                                          contents_limit: int, lapse_date: str, coverage_effective_date: str,
                                          certificate_expiration_date: str, annual_premium: float) -> str:
    """Places lender-placed flood building and business contents coverage on one commercial loan
    under the lender's master program. One call issues a new certificate for the loan with a newly
    assigned certificate number, recording the borrower, the building, its flood zone, the balances
    and contents value the lender reports, the mandatory purchase amount, the building and contents
    limits, the date the borrower's coverage lapsed, the coverage dates and the annual premium; it
    bills that premium to the lender's program account on the statement for the current month as a
    new placement and raises the amount the lender owes on the program by the premium. On success
    the certificate can be found under the program with its certificate number and the premium
    appears among the program's account entries.

    Args:
        forceplaced_program_id: Id class — the reference number of the lender's master program that
            places the coverage, as returned by the master program lookup.
        loan_number: Verbatim class — the lender's loan number exactly as shown on the borrower
            notices returned by the tracking lookup, copied character for character (verbatim).
        borrower_name: Verbatim class — the borrowing business's legal name exactly as the lender
            states it on the call, copied character for character (verbatim).
        property_address: Verbatim class — the street address of the mortgaged building exactly as
            the lender states it on the call, copied character for character (verbatim).
        flood_zone: Enum class — the flood zone on the lender's Standard Flood Hazard Determination
            Form for the building; exactly one of: A (special flood hazard area, no base flood
            elevation); AE (special flood hazard area with base flood elevations); AH (special flood
            hazard area of shallow ponding); AO (special flood hazard area of shallow sheet flow);
            AR (special flood hazard area during flood-control system restoration); A99 (special
            flood hazard area protected by a flood-control system under construction); V (coastal
            high hazard area, no base flood elevation); VE (coastal high hazard area with base flood
            elevations); B (moderate flood hazard area on older maps); C (minimal flood hazard area
            on older maps); X (moderate or minimal flood hazard area); D (undetermined flood hazard);
            NONE (no zone shown on the form).
        outstanding_principal_balance: Fixed-format class — the unpaid principal balance of the loan
            as the lender reports it, in USD with 2 decimal places (cents).
        insurable_value: Fixed-format class — the building's replacement cost value as the lender
            reports it, in USD, whole dollars (integer, no cents).
        required_amount: Fixed-format class — the mandatory purchase amount for the loan, in USD, whole dollars
            (integer, no cents).
        building_limit: Fixed-format class — the certificate building limit, in USD, whole dollars (integer, no
            cents).
        secured_contents_value: Fixed-format class — the value of business contents securing the loan
            as the lender reports it, in USD, whole dollars (integer, no cents); 0 when contents do not secure
            the loan.
        contents_limit: Fixed-format class — the certificate contents limit, in USD, whole dollars (integer, no
            cents); 0 when no contents coverage is placed.
        lapse_date: Fixed-format class — the date the borrower's own coverage lapsed or became
            insufficient, as YYYY-MM-DD (calendar date, no time or time zone).
        coverage_effective_date: Fixed-format class — the start date of certificate coverage, as
            YYYY-MM-DD (calendar date, no time or time zone).
        certificate_expiration_date: Fixed-format class — the last day of the certificate term, as
            YYYY-MM-DD (calendar date, no time or time zone).
        annual_premium: Fixed-format class — the annual premium of the certificate, in USD as a
            positive number with 2 decimal places (cents); the value given is rounded half to even
            to the cent on booking.

    Returns:
        A confirmation string giving the newly assigned certificate number (letters followed by
        digits), the issue entry reference, the loan number, the coverage dates (YYYY-MM-DD), the
        building and contents limits in USD, whole dollars, the premium billed in USD with 2
        decimals and its statement month (YYYY-MM), the charge entry reference, and the program's
        amount owed net of the charge in USD with 2 decimals. A certificate number in the
        reply indicates the certificate was issued and billed.
    """
    prem = round(float(annual_premium), 2)
    stamp = ctx.now()
    iid = ctx.make_id("fpi_", forceplaced_program_id, loan_number, borrower_name, property_address, flood_zone,
                      outstanding_principal_balance, insurable_value, required_amount, building_limit,
                      secured_contents_value, contents_limit, lapse_date, coverage_effective_date,
                      certificate_expiration_date, prem)
    cert = _Acct.number("LC", iid)
    prog = ctx.find("forceplaced_programs", forceplaced_program_id=forceplaced_program_id)
    cust = prog[0].get("customer_id") if prog else ""
    ctx.create("forceplaced_certificates", iid, forceplaced_certificate_event_id=iid,
               forceplaced_program_id=forceplaced_program_id, customer_id=cust,
               event_type="forceplaced_certificate_issued", certificate_number=cert, loan_number=loan_number,
               borrower_name=borrower_name, property_address=property_address, flood_zone=flood_zone,
               outstanding_principal_balance=round(float(outstanding_principal_balance), 2),
               insurable_value=int(insurable_value), borrower_existing_limit=0, required_amount=int(required_amount),
               secured_contents_value=int(secured_contents_value), building_limit=int(building_limit),
               contents_limit=int(contents_limit), lapse_date=lapse_date,
               coverage_effective_date=coverage_effective_date, certificate_expiration_date=certificate_expiration_date,
               annual_premium=prem, cancellation_reason="NONE", cancellation_effective_date="",
               event_date=_Acct.day(stamp))
    bid = ctx.make_id("fpb_", iid, "placement")
    ctx.create("forceplaced_billing", bid, forceplaced_billing_id=bid, forceplaced_program_id=forceplaced_program_id,
               customer_id=cust, event_type="forceplaced_premium_charged", certificate_number=cert,
               statement_month=_Acct.month(stamp), charge_basis="NEW_PLACEMENT", amount=prem,
               posted_date=_Acct.day(stamp), payment_ref="", reference_id="")
    bal = round(float(prog[0].get("premium_balance") or 0) + prem, 2) if prog else prem
    ctx.update("forceplaced_programs", forceplaced_program_id, premium_balance=bal)
    return (f"Certificate {cert} issued (entry {iid}) on loan {loan_number}, coverage {coverage_effective_date} to "
            f"{certificate_expiration_date}, building limit {int(building_limit)} USD, contents limit {int(contents_limit)} "
            f"USD; premium {prem:.2f} USD billed on statement {_Acct.month(stamp)} (entry {bid}); program amount owed now "
            f"{bal:.2f} USD.")

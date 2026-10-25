"""Hidden task tools for the insurance_claim_services difficulty (Ridgecrest Restoration & Reconstruction).

Each tool lands one atomic write on the insured's claim file. None of them checks a policy condition:
the amounts, sequence numbers and references are worked out by the caller from the published rules. Each
body enforces only the argument formats its docstring states.
"""

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

from erlbench import ToolContext, tool


class _Money:
    """Exact half-up rounding to the cent, argument-format checks, and the shared supplement write of these tools."""

    @staticmethod
    def cents(value):
        """Return the value rounded half up to the cent, or None when it is not a positive number."""
        try:
            d = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return None
        if not d.is_finite():
            return None
        q = d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if q <= 0:
            return None
        return float(q)

    @staticmethod
    def sequence(value):
        """Return the value as an integer of at least 1, or None when it is not one."""
        if isinstance(value, bool):
            return None
        if isinstance(value, int):
            return value if value >= 1 else None
        if isinstance(value, float) and value.is_integer() and value >= 1:
            return int(value)
        if isinstance(value, str) and value.strip().isdigit() and int(value.strip()) >= 1:
            return int(value.strip())
        return None

    @staticmethod
    def prepare(ctx, claim_file_id, related_job_id, supplement_number, requested_amount, reason):
        """Check the arguments and work out the supplement row; returns (error, row). It writes nothing."""
        amount = _Money.cents(requested_amount)
        if amount is None:
            return "Error: requested_amount must be a positive number of US dollars; nothing was recorded.", None
        number = _Money.sequence(supplement_number)
        if number is None:
            return "Error: supplement_number must be an integer of at least 1; nothing was recorded.", None
        files = ctx.find("claims_files", claim_file_id=claim_file_id)
        if not files:
            return f"Error: no claim file {claim_file_id}; nothing was recorded.", None
        rid = ctx.make_id("crq_", claim_file_id, related_job_id, number, reason, amount)
        row = dict(claim_request_id=rid, claim_file_id=claim_file_id, customer_id=files[0].get("customer_id", ""),
                   event_type="claims_supplement_submit", supplement_number=number, supplement_reason=reason,
                   coverage_part="dwelling", related_job_id=related_job_id, request_date=ctx.now()[:10],
                   requested_amount=amount)
        return None, row

    @staticmethod
    def confirm(row, label):
        """Format the confirmation string for a recorded supplement row."""
        return (f"Supplement {row['claim_request_id']} recorded on claim file {row['claim_file_id']} for {label} "
                f"{row['related_job_id']}: number {row['supplement_number']}, reason {row['supplement_reason']}, "
                f"coverage dwelling, date {row['request_date']}, amount requested {row['requested_amount']:.2f}.")


@tool(owner="agent", rw="write")
def submit_regulated_scope_supplement_ec41bed4(ctx: ToolContext, claim_file_id: str, related_job_id: str,
                                               supplement_number: int, requested_amount: float) -> str:
    """Records on the insured's claim file the scope-omission supplement the company prepared for the
    regulated-material work billed on a water mitigation job that the carrier's initial approval did not carry,
    as delivered today to the insured or their public adjuster. One call records one scope_omission supplement on
    the dwelling coverage of that claim file, dated today, naming the water job and carrying the amount requested;
    the supplement then shows on the claim file as awaiting the carrier's decision. Nothing on the job or on the
    carrier receivable changes. Success is the returned confirmation carrying the new supplement reference.

    Args:
        claim_file_id: Id class — the reference number of the insured's claim file, as returned by the claim file lookup for this customer.
        related_job_id: Id class — the reference number of the water mitigation job whose regulated-material lines the supplement claims, as returned by the water job lookup for this claim file.
        supplement_number: Fixed-format class — the sequence number this supplement takes on the claim file, an integer of at least 1 written without separators or decimals.
        requested_amount: Fixed-format class — the amount the supplement asks the carrier to approve, in US dollars, a positive number with 2 decimal places; a value with more places is rounded half up to the cent when recorded.

    Returns:
        A confirmation string naming the supplement reference (text id of the new supplement), the claim file
        reference, the related job reference, the supplement number (whole number), the reason scope_omission,
        the coverage dwelling, the recording date (YYYY-MM-DD) and the amount requested (US dollars, two
        decimals). Receiving it means the supplement is on the claim file awaiting the carrier's decision. A
        string starting with "Error:" means nothing was recorded.
    """
    error, row = _Money.prepare(ctx, claim_file_id, related_job_id, supplement_number, requested_amount,
                                "scope_omission")
    if error:
        return error
    ctx.create("claims_requests", row["claim_request_id"], **row)
    return _Money.confirm(row, "water job")


@tool(owner="agent", rw="write")
def submit_category_reassessment_supplement_86febceb(ctx: ToolContext, claim_file_id: str, related_job_id: str,
                                                     supplement_number: int, requested_amount: float) -> str:
    """Records on the insured's claim file the category reassessment supplement the company prepared for a water
    mitigation job whose recorded water category differs from the category of the tier it was dispatched at, as
    delivered today to the insured or their public adjuster. One call records one price_variance supplement on
    the dwelling coverage of that claim file, dated today, naming the water job and carrying the amount
    requested; the supplement then shows on the claim file as awaiting the carrier's decision. Nothing on the job
    or on the carrier receivable changes. Success is the returned confirmation carrying the new supplement
    reference.

    Args:
        claim_file_id: Id class — the reference number of the insured's claim file, as returned by the claim file lookup for this customer.
        related_job_id: Id class — the reference number of the water mitigation job the reassessment prices, as returned by the water job lookup for this claim file.
        supplement_number: Fixed-format class — the sequence number this supplement takes on the claim file, an integer of at least 1 written without separators or decimals.
        requested_amount: Fixed-format class — the amount the supplement asks the carrier to approve, in US dollars, a positive number with 2 decimal places; a value with more places is rounded half up to the cent when recorded.

    Returns:
        A confirmation string naming the supplement reference (text id of the new supplement), the claim file
        reference, the related job reference, the supplement number (whole number), the reason price_variance,
        the coverage dwelling, the recording date (YYYY-MM-DD) and the amount requested (US dollars, two
        decimals). Receiving it means the supplement is on the claim file awaiting the carrier's decision. A
        string starting with "Error:" means nothing was recorded.
    """
    error, row = _Money.prepare(ctx, claim_file_id, related_job_id, supplement_number, requested_amount,
                                "price_variance")
    if error:
        return error
    ctx.create("claims_requests", row["claim_request_id"], **row)
    return _Money.confirm(row, "water job")


@tool(owner="agent", rw="write")
def submit_mold_protocol_supplement_d9a0c26a(ctx: ToolContext, claim_file_id: str, related_job_id: str,
                                             supplement_number: int, requested_amount: float) -> str:
    """Records on the insured's claim file the mold protocol supplement the company prepared from the independent
    assessor's protocol for a mold job awaiting clearance, as delivered today to the insured. One call records
    one mold_remediation supplement on the dwelling coverage of that claim file, dated today, naming the mold job
    and carrying the amount requested; the supplement then shows on the claim file as awaiting the carrier's
    decision. Nothing on the mold jobs or on the carrier receivable changes. Success is the returned
    confirmation carrying the new supplement reference.

    Args:
        claim_file_id: Id class — the reference number of the insured's claim file, as returned by the claim file lookup for this customer.
        related_job_id: Id class — the reference number of the mold remediation job the protocol covers, as returned by the mold job lookup for this claim file.
        supplement_number: Fixed-format class — the sequence number this supplement takes on the claim file, an integer of at least 1 written without separators or decimals.
        requested_amount: Fixed-format class — the amount the supplement asks the carrier to approve, in US dollars, a positive number with 2 decimal places; a value with more places is rounded half up to the cent when recorded.

    Returns:
        A confirmation string naming the supplement reference (text id of the new supplement), the claim file
        reference, the related mold job reference, the supplement number (whole number), the reason
        mold_remediation, the coverage dwelling, the recording date (YYYY-MM-DD) and the amount requested (US
        dollars, two decimals). Receiving it means the supplement is on the claim file awaiting the carrier's
        decision. A string starting with "Error:" means nothing was recorded.
    """
    error, row = _Money.prepare(ctx, claim_file_id, related_job_id, supplement_number, requested_amount,
                                "mold_remediation")
    if error:
        return error
    ctx.create("claims_requests", row["claim_request_id"], **row)
    return _Money.confirm(row, "mold job")


@tool(owner="user", rw="write")
def submit_mold_reconciliation_7e4d140d(ctx: ToolContext, claim_file_id: str, related_job_id: str,
                                        supplement_number: int, requested_amount: float) -> str:
    """The insured submits to their insurance carrier, from the company's claim portal, the final mold supplement
    the company prepared, claiming the scope actually billed on a mold job awaiting clearance. One call records
    one mold_remediation supplement on the dwelling coverage of the claim file, dated today, naming the mold job
    and carrying the amount requested; the supplement then shows on the claim file as awaiting the carrier's
    decision. Nothing on the mold jobs or on the carrier receivable changes. Success is the returned
    confirmation carrying the new supplement reference.

    Args:
        claim_file_id: Id class — the reference number of the insured's claim file, as returned by the claim file lookup for this customer.
        related_job_id: Id class — the reference number of the mold remediation job the supplement names, as returned by the mold job lookup for this claim file.
        supplement_number: Fixed-format class — the sequence number this supplement takes on the claim file, an integer of at least 1 written without separators or decimals.
        requested_amount: Fixed-format class — the amount the supplement asks the carrier to approve, in US dollars, a positive number with 2 decimal places; a value with more places is rounded half up to the cent when recorded.

    Returns:
        A confirmation string naming the supplement reference (text id of the new supplement), the claim file
        reference, the related mold job reference, the supplement number (whole number), the reason
        mold_remediation, the coverage dwelling, the submission date (YYYY-MM-DD) and the amount requested (US
        dollars, two decimals). Receiving it means the supplement is on the claim file awaiting the carrier's
        decision. A string starting with "Error:" means nothing was recorded.
    """
    error, row = _Money.prepare(ctx, claim_file_id, related_job_id, supplement_number, requested_amount,
                                "mold_remediation")
    if error:
        return error
    ctx.create("claims_requests", row["claim_request_id"], **row)
    return _Money.confirm(row, "mold job")


@tool(owner="user", rw="write")
def submit_depreciation_release_d117c1f9(ctx: ToolContext, claim_file_id: str, related_job_id: str,
                                         requested_amount: float) -> str:
    """The insured submits to their insurance carrier, from the company's claim portal, a request to release the
    recoverable depreciation the carrier withheld on the dwelling coverage of their claim file, naming the
    completed reconstruction contract as proof of completion. One call records one depreciation release request
    on the dwelling coverage, dated today, carrying the amount requested; it then shows on the claim file as
    submitted. Nothing on the contract or on the carrier receivable changes. Success is the returned confirmation
    carrying the new request reference.

    Args:
        claim_file_id: Id class — the reference number of the insured's claim file, as returned by the claim file lookup for this customer.
        related_job_id: Id class — the reference number of the completed reconstruction contract the request names, as returned by the reconstruction contract lookup for this claim file.
        requested_amount: Fixed-format class — the depreciation the request asks the carrier to release, in US dollars, a positive number with 2 decimal places; a value with more places is rounded half up to the cent when recorded.

    Returns:
        A confirmation string naming the request reference (text id of the new release request), the claim file
        reference, the completed contract reference, the coverage dwelling, the submission date (YYYY-MM-DD) and
        the amount requested (US dollars, two decimals). Receiving it means the release request is on the claim
        file. A string starting with "Error:" means nothing was recorded.
    """
    amount = _Money.cents(requested_amount)
    if amount is None:
        return "Error: requested_amount must be a positive number of US dollars; nothing was recorded."
    files = ctx.find("claims_files", claim_file_id=claim_file_id)
    if not files:
        return f"Error: no claim file {claim_file_id}; nothing was recorded."
    customer_id = files[0].get("customer_id", "")
    rid = ctx.make_id("crq_", claim_file_id, related_job_id, "dwelling", amount)
    today = ctx.now()[:10]
    ctx.create("claims_requests", rid, claim_request_id=rid, claim_file_id=claim_file_id, customer_id=customer_id,
               event_type="claims_depreciation_release_request", coverage_part="dwelling",
               related_job_id=related_job_id, request_date=today, requested_amount=amount)
    return (f"Release request {rid} submitted on claim file {claim_file_id} for contract {related_job_id}: "
            f"coverage dwelling, date {today}, amount requested {amount:.2f}.")


@tool(owner="agent", rw="write")
def post_credited_line_writeoff_e2edbc44(ctx: ToolContext, claim_file_id: str, source_approval_id: str,
                                         amount: float) -> str:
    """Posts on the insured's claim file a write-off with reason carrier_denied_line that reduces one approval line
    of the carrier, for the approved value of work the water job credited or conceded as goodwill or signed
    deductive change orders removed, which the company no longer bills and so does not collect. One call records one
    write-off line on the claim file, dated today, naming the approval line it reduces, and lowers the claim
    file's carrier receivable by the same amount. Success is the returned confirmation carrying the new write-off
    reference and the receivable after posting.

    Args:
        claim_file_id: Id class — the reference number of the insured's claim file, as returned by the claim file lookup for this customer.
        source_approval_id: Id class — the reference number of the carrier approval line the write-off reduces, as returned by the approval lookup for this claim file.
        amount: Fixed-format class — the amount written off, in US dollars, a positive number with 2 decimal places; a value with more places is rounded half up to the cent when recorded.

    Returns:
        A confirmation string naming the write-off reference (text id of the new line), the claim file
        reference, the approval line reduced, the reason carrier_denied_line, the posting date (YYYY-MM-DD), the
        amount written off (US dollars, two decimals) and the carrier receivable after posting (US dollars, two
        decimals). Receiving it means the write-off stands on the claim file. A string starting with "Error:"
        means nothing was recorded.
    """
    value = _Money.cents(amount)
    if value is None:
        return "Error: amount must be a positive number of US dollars; nothing was recorded."
    files = ctx.find("claims_files", claim_file_id=claim_file_id)
    if not files:
        return f"Error: no claim file {claim_file_id}; nothing was recorded."
    row = files[0]
    customer_id = row.get("customer_id", "")
    receivable = float((Decimal(str(row.get("carrier_receivable") or 0)) - Decimal(str(value))).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP))
    rid = ctx.make_id("cwo_", claim_file_id, source_approval_id, "carrier_denied_line", value)
    today = ctx.now()[:10]
    ctx.create("claims_approvals", rid, claim_approval_id=rid, claim_file_id=claim_file_id, customer_id=customer_id,
               event_type="claims_receivable_writeoff", source_approval_id=source_approval_id,
               writeoff_reason="carrier_denied_line", coverage_part="dwelling", posted_date=today, amount=value)
    ctx.update("claims_files", claim_file_id, carrier_receivable=receivable)
    return (f"Write-off {rid} posted on claim file {claim_file_id} against approval {source_approval_id}: reason "
            f"carrier_denied_line, date {today}, amount {value:.2f}; carrier receivable now {receivable:.2f}.")

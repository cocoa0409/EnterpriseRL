"""Hidden task tools of the documentation_release_desk difficulty (category: bol).

Each tool performs one atomic documentation action on a transport document record and is
reached only through the unlock_* -> call_* meta-tools after its name is read from the
extended charter. No tool checks a business precondition, computes a fee or reconciles a
ledger: the caller decides every value from the published policy and the records, and the
tool lands exactly the write it is given.
"""

from erlbench import ToolContext, tool


class _Doc:
    """Read-back helpers for the transport document record a tool writes against (not tools)."""

    @staticmethod
    def party(ctx: ToolContext, bl_id: str) -> str:
        rows = ctx.find("bills_of_lading", bl_id=bl_id)
        return rows[0].get("customer_id") if rows else ""

    @staticmethod
    def field(ctx: ToolContext, bl_id: str, name: str, default):
        rows = ctx.find("bills_of_lading", bl_id=bl_id)
        return rows[0].get(name, default) if rows else default


# ------------------------------------------------------------------------------------------
# Post-issuance correction of a paper document whose originals must come back first
# ------------------------------------------------------------------------------------------
@tool(owner="user", rw="write")
def return_originals_for_correction_b9bd03b3(ctx: ToolContext, bl_id: str, bl_set_sequence: int,
                                              originals_count: int) -> str:
    """The shipper printed on a transport document lodges its original bills of lading back with the line at the origin office so that a requested correction of the printed document can go ahead.

    One call records one lodgement of originals of one set: a documentation entry is added to
    the transport document showing the originals handed in at the origin office on today's
    date, and the count of originals still in circulation on the document goes down by the
    number lodged. Nothing is charged. Afterwards the customer can see the lodgement in the
    documentation history and the reduced number of originals outstanding on the document.

    Args:
        bl_id: Id class — reference number of the transport document whose originals are lodged, as returned by the transport document lookup for the bill of lading number the caller quotes.
        bl_set_sequence: Fixed-format class — the set of originals the lodged originals belong to, written in the unit "integer; 1 = first set issued, 2 = replacement or switch set" (in the documentation history the same number reads "integer; 1 = first set, 2 = replacement or switch set"); a whole number with no decimals, dimensionless apart from that set numbering.
        originals_count: Fixed-format class — how many original documents are lodged in this call, written in the unit "integer, original documents"; a whole number of 1 or more, no decimals.

    Returns:
        A confirmation sentence naming the documentation entry reference (an opaque text id beginning "bse_"), the transport document reference, the set number and the number of originals lodged at the origin office. The sentence appearing is the success signal; the lodgement is then visible in the documentation history.
    """
    rid = ctx.make_id("bse_", bl_id, bl_set_sequence, originals_count, "origin_office", ctx.now()[:10])
    ctx.create("bol_ledger", rid, bol_event_id=rid, bl_id=bl_id, customer_id=_Doc.party(ctx, bl_id),
               event_type="bol_originals_surrendered", event_date=ctx.now()[:10], charge_code="none",
               amount_usd=0.0, bl_set_sequence=int(bl_set_sequence), originals_count=int(originals_count),
               surrender_location="origin_office", release_method="not_applicable", payment_reference="")
    left = int(_Doc.field(ctx, bl_id, "originals_outstanding", 0) or 0) - int(originals_count)
    ctx.update("bills_of_lading", bl_id, originals_outstanding=left)
    return (f"Lodgement {rid} recorded on document {bl_id}: {int(originals_count)} original(s) of set "
            f"{int(bl_set_sequence)} handed in at the origin office.")


@tool(owner="agent", rw="write")
def apply_particular_correction_a24e9121(ctx: ToolContext, bl_id: str, booking_id: str, request_id: str,
                                          corrected_field: str, requested_value: str) -> str:
    """Apply a registered correction request to the printed particulars of an issued transport document and close the request as completed.

    One call rewrites exactly one printed particular of the document with the new wording or
    figure and marks the correction request that asked for it as completed. No fee is booked by
    this action and no new set of originals is issued by it. Afterwards the document shows the
    corrected particular and the request shows the outcome completed.

    Args:
        bl_id: Id class — reference number of the transport document to correct, as returned by the transport document lookup.
        booking_id: Id class — reference number of the booking the document covers, as shown on the transport document record and returned by the booking lookup.
        request_id: Id class — reference number of the correction request on file for this document, as returned by the documentation service request lookup.
        corrected_field: Enum class — the particular being rewritten; one of consignee_name (the consignee printed on the document), notify_party_name (the notify party printed on the document), cargo_description (the description of goods printed), package_count (the number of packages printed), gross_weight_kg (the gross cargo weight printed), shipper_name (the shipper printed), port_of_discharge (the port of discharge printed). It must be the particular named on the correction request.
        requested_value: Verbatim class — the new wording or figure for that particular, copied character for character from the correction request on file, which holds it exactly as the customer supplied it; keep every word, digit, space and punctuation mark with no translation, normalisation, summarising, addition or deletion (verbatim).

    Returns:
        A confirmation sentence naming the transport document reference, the particular corrected, the new printed value and the correction request reference now marked completed. The sentence appearing is the success signal.
    """
    value = requested_value
    if corrected_field == "package_count":
        value = int(requested_value)
    elif corrected_field == "gross_weight_kg":
        value = round(float(requested_value), 1)
    ctx.update("bills_of_lading", bl_id, **{corrected_field: value})
    ctx.update("bol_service_requests", request_id, outcome="completed")
    return (f"Document {bl_id} (booking {booking_id}): {corrected_field} now reads '{value}'. "
            f"Correction request {request_id} completed.")


@tool(owner="agent", rw="write")
def charge_correction_fee_18211c73(ctx: ToolContext, bl_id: str, booking_id: str, request_id: str,
                                   amount_usd: float) -> str:
    """Book the correction fee for one executed correction request on an issued transport document.

    One call adds one correction-fee charge to the document's documentation account, tied to the
    correction request it charges, dated today, and raises the documentation charges due on the
    document by the amount booked. Afterwards the customer sees the correction fee in the
    documentation history and in the charges due.

    Args:
        bl_id: Id class — reference number of the transport document charged, as returned by the transport document lookup.
        booking_id: Id class — reference number of the booking the document covers, as shown on the transport document record and returned by the booking lookup.
        request_id: Id class — reference number of the correction request this fee charges, as returned by the documentation service request lookup.
        amount_usd: Fixed-format class — the fee booked, in the unit USD, written to 2 decimal places (for example 150.00); no currency sign.

    Returns:
        A confirmation sentence naming the new documentation charge reference (an opaque text id beginning "bcf_"), the transport document reference, the correction request charged, the amount booked in USD with 2 decimal places and the documentation charges now due. The sentence appearing is the success signal.
    """
    amount = round(float(amount_usd), 2)
    seq = int(_Doc.field(ctx, bl_id, "bl_set_sequence", 1) or 1)
    rid = ctx.make_id("bcf_", bl_id, booking_id, request_id, amount)
    ctx.create("bol_ledger", rid, bol_event_id=rid, bl_id=bl_id, customer_id=_Doc.party(ctx, bl_id),
               event_type="bol_correction_fee_charged", event_date=ctx.now()[:10], charge_code="correction_fee",
               amount_usd=amount, request_id=request_id, bl_set_sequence=seq,
               originals_count=0, surrender_location="not_applicable", release_method="not_applicable",
               payment_reference="")
    due = round(float(_Doc.field(ctx, bl_id, "charges_due_usd", 0) or 0) + amount, 2)
    ctx.update("bills_of_lading", bl_id, charges_due_usd=due)
    return (f"Correction fee {rid} of USD {amount:.2f} booked on document {bl_id} for request {request_id}; "
            f"documentation charges due now USD {due:.2f}.")


@tool(owner="agent", rw="write")
def issue_corrected_set_a7062696(ctx: ToolContext, bl_id: str, request_id: str, bl_set_sequence: int,
                                 originals_count: int) -> str:
    """Issue the corrected transport document as a new set of originals after a correction that required the previous originals back.

    One call makes the given set the set in force on the document, dates its issue today, adds the
    given number of originals to the originals in circulation and records the originals of the new
    set as put into circulation in the documentation history. No issuance fee is booked. Afterwards
    the customer sees the new set number, the new date of issue and the originals outstanding.

    Args:
        bl_id: Id class — reference number of the transport document being reissued as a corrected set, as returned by the transport document lookup.
        request_id: Id class — reference number of the correction request the corrected set carries, as returned by the documentation service request lookup.
        bl_set_sequence: Fixed-format class — the number of the new set of originals, written in the unit "integer; 1 = first set issued, 2 = replacement or switch set" (in the documentation history the same number reads "integer; 1 = first set, 2 = replacement or switch set"); a whole number with no decimals, dimensionless apart from that set numbering.
        originals_count: Fixed-format class — how many original documents of the new set are put into circulation, written in the unit "integer, original documents"; a whole number, 0 or more, no decimals.

    Returns:
        A confirmation sentence naming the documentation entry reference of the originals put into circulation (an opaque text id beginning "boi_"), the transport document reference, the correction request carried, the new set number, the number of originals issued and the originals now outstanding. The sentence appearing is the success signal.
    """
    rid = ctx.make_id("boi_", bl_id, request_id, bl_set_sequence, originals_count)
    ctx.create("bol_ledger", rid, bol_event_id=rid, bl_id=bl_id, customer_id=_Doc.party(ctx, bl_id),
               event_type="bol_originals_issued", event_date=ctx.now()[:10], charge_code="none", amount_usd=0.0,
               request_id=request_id, bl_set_sequence=int(bl_set_sequence), originals_count=int(originals_count),
               surrender_location="not_applicable", release_method="not_applicable", payment_reference="")
    left = int(_Doc.field(ctx, bl_id, "originals_outstanding", 0) or 0) + int(originals_count)
    ctx.update("bills_of_lading", bl_id, bl_set_sequence=int(bl_set_sequence), issued_date=ctx.now()[:10],
               originals_outstanding=left)
    return (f"Corrected set {int(bl_set_sequence)} issued on document {bl_id} for request {request_id}: "
            f"{int(originals_count)} original(s) put into circulation (entry {rid}); originals outstanding now {left}.")


# ------------------------------------------------------------------------------------------
# Issuance of an approved document, full-set surrender at origin and the telex release fee
# ------------------------------------------------------------------------------------------
@tool(owner="agent", rw="write")
def issue_document_with_originals_c9d717be(ctx: ToolContext, bl_id: str, booking_id: str, originals_count: int,
                                           issuance_fee_usd: float) -> str:
    """Issue an approved transport document: date its issue today, book the issuance fee of the set in force and put that set's originals into circulation.

    One call moves the document from approved to issued with today's date of issue, adds one
    issuance-fee charge for the set in force to the documentation account (raising the
    documentation charges due by that fee) and, when the given number of originals is above
    zero, records those originals as put into circulation and adds them to the originals
    outstanding. Afterwards the customer sees the document as issued, the issuance fee and the
    originals in circulation.

    Args:
        bl_id: Id class — reference number of the approved transport document to issue, as returned by the transport document lookup for the bill of lading number the caller quotes.
        booking_id: Id class — reference number of the booking the document covers, as shown on the transport document record and returned by the booking lookup.
        originals_count: Fixed-format class — how many original documents of the set in force are put into circulation, written in the unit "integer, original documents"; a whole number, 0 or more, no decimals.
        issuance_fee_usd: Fixed-format class — the issuance fee booked for the set, in the unit USD, written to 2 decimal places (for example 75.00); no currency sign.

    Returns:
        A confirmation sentence naming the issuance-fee entry reference (an opaque text id beginning "bif_"), the originals-issued entry reference (beginning "boi_", or the word none when 0 originals were given and no originals entry was recorded), the transport document reference, the booking reference, the set number, the fee in USD with 2 decimal places, the originals put into circulation and the originals now outstanding. The sentence appearing is the success signal; the document then shows the status issued.
    """
    party = _Doc.party(ctx, bl_id)
    day = ctx.now()[:10]
    seq = int(_Doc.field(ctx, bl_id, "bl_set_sequence", 1) or 1)
    fee = round(float(issuance_fee_usd), 2)
    fid = ctx.make_id("bif_", bl_id, booking_id, seq, fee)
    ctx.create("bol_ledger", fid, bol_event_id=fid, bl_id=bl_id, customer_id=party, event_type="bol_issuance_fee_charged",
               event_date=day, charge_code="document_issuance_fee", amount_usd=fee, bl_set_sequence=seq,
               originals_count=0, surrender_location="not_applicable", release_method="not_applicable",
               payment_reference="")
    iid = "none"
    if int(originals_count) > 0:
        iid = ctx.make_id("boi_", bl_id, booking_id, seq, originals_count)
        ctx.create("bol_ledger", iid, bol_event_id=iid, bl_id=bl_id, customer_id=party, event_type="bol_originals_issued",
                   event_date=day, charge_code="none", amount_usd=0.0, bl_set_sequence=seq,
                   originals_count=int(originals_count), surrender_location="not_applicable",
                   release_method="not_applicable", payment_reference="")
    left = int(_Doc.field(ctx, bl_id, "originals_outstanding", 0) or 0) + int(originals_count)
    due = round(float(_Doc.field(ctx, bl_id, "charges_due_usd", 0) or 0) + fee, 2)
    ctx.update("bills_of_lading", bl_id, status="issued", issued_date=day, originals_outstanding=left,
               charges_due_usd=due)
    return (f"Document {bl_id} (booking {booking_id}) issued as set {seq}: issuance fee USD {fee:.2f} booked "
            f"(entry {fid}); {int(originals_count)} original(s) put into circulation (entry {iid}); "
            f"originals outstanding now {left}.")


@tool(owner="user", rw="write")
def surrender_full_set_at_origin_68a55055(ctx: ToolContext, bl_id: str, request_id: str, bl_set_sequence: int,
                                          originals_count: int) -> str:
    """The shipper printed on a transport document surrenders the full set of its originals at the origin office, completing the surrender a telex release needs.

    One call records the surrender of the given originals of the given set at the origin office
    on today's date, lowers the originals still in circulation by that number and moves the
    document to the status surrendered. Nothing is charged by this action. Afterwards the customer
    sees the surrender in the documentation history and the document shown as surrendered.

    Args:
        bl_id: Id class — reference number of the transport document whose originals are surrendered, as returned by the transport document lookup for the bill of lading number the caller quotes.
        request_id: Id class — reference number of the telex release request on file for the document that this surrender answers, as returned by the documentation service request lookup.
        bl_set_sequence: Fixed-format class — the set the surrendered originals belong to, written in the unit "integer; 1 = first set issued, 2 = replacement or switch set" (in the documentation history the same number reads "integer; 1 = first set, 2 = replacement or switch set"); a whole number with no decimals, dimensionless apart from that set numbering.
        originals_count: Fixed-format class — how many original documents are surrendered in this call, written in the unit "integer, original documents"; a whole number of 1 or more, no decimals.

    Returns:
        A confirmation sentence naming the surrender entry reference (an opaque text id beginning "bss_"), the transport document reference, the telex release request answered, the set number, the number of originals surrendered at the origin office and the originals still outstanding. The sentence appearing is the success signal; the document then shows the status surrendered.
    """
    rid = ctx.make_id("bss_", bl_id, request_id, bl_set_sequence, originals_count, "origin_office", ctx.now()[:10])
    ctx.create("bol_ledger", rid, bol_event_id=rid, bl_id=bl_id, customer_id=_Doc.party(ctx, bl_id),
               event_type="bol_originals_surrendered", event_date=ctx.now()[:10], charge_code="none", amount_usd=0.0,
               request_id=request_id, bl_set_sequence=int(bl_set_sequence), originals_count=int(originals_count),
               surrender_location="origin_office", release_method="not_applicable", payment_reference="")
    left = int(_Doc.field(ctx, bl_id, "originals_outstanding", 0) or 0) - int(originals_count)
    ctx.update("bills_of_lading", bl_id, status="surrendered", originals_outstanding=left)
    return (f"Surrender {rid} recorded on document {bl_id} for request {request_id}: {int(originals_count)} original(s) of set "
            f"{int(bl_set_sequence)} surrendered at the origin office; originals outstanding now {left}; status surrendered.")


@tool(owner="agent", rw="write")
def charge_telex_release_fee_be5da3ed(ctx: ToolContext, bl_id: str, booking_id: str, request_id: str,
                                      amount_usd: float) -> str:
    """Book the telex release fee of a registered telex release request on a transport document and close the request as completed.

    One call adds one telex-release-fee charge to the document's documentation account, tied to the
    telex release request it charges and dated today, raises the documentation charges due by the
    amount and marks the telex release request completed. Afterwards the customer sees the telex
    release fee in the documentation history and the request shown as completed.

    Args:
        bl_id: Id class — reference number of the transport document charged, as returned by the transport document lookup.
        booking_id: Id class — reference number of the booking the document covers, as shown on the transport document record and returned by the booking lookup.
        request_id: Id class — reference number of the telex release request on file for the document, as returned by the documentation service request lookup.
        amount_usd: Fixed-format class — the fee booked, in the unit USD, written to 2 decimal places (for example 55.00); no currency sign.

    Returns:
        A confirmation sentence naming the new documentation charge reference (an opaque text id beginning "btf_"), the transport document reference, the telex release request completed, the amount booked in USD with 2 decimal places and the documentation charges now due. The sentence appearing is the success signal.
    """
    amount = round(float(amount_usd), 2)
    seq = int(_Doc.field(ctx, bl_id, "bl_set_sequence", 1) or 1)
    rid = ctx.make_id("btf_", bl_id, booking_id, request_id, amount)
    ctx.create("bol_ledger", rid, bol_event_id=rid, bl_id=bl_id, customer_id=_Doc.party(ctx, bl_id),
               event_type="bol_release_fee_charged", event_date=ctx.now()[:10], charge_code="telex_release_fee",
               amount_usd=amount, request_id=request_id, bl_set_sequence=seq, originals_count=0,
               surrender_location="not_applicable", release_method="not_applicable", payment_reference="")
    due = round(float(_Doc.field(ctx, bl_id, "charges_due_usd", 0) or 0) + amount, 2)
    ctx.update("bills_of_lading", bl_id, charges_due_usd=due)
    ctx.update("bol_service_requests", request_id, outcome="completed")
    return (f"Telex release fee {rid} of USD {amount:.2f} booked on document {bl_id} (booking {booking_id}); "
            f"request {request_id} completed; documentation charges due now USD {due:.2f}.")

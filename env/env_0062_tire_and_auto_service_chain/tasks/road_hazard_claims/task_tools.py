"""Hidden task tools for the road_hazard_claims difficulty (category: hazard).

Each tool performs one atomic write on a road hazard certificate. Tools never judge eligibility,
never aggregate history and never compute a policy amount: the caller passes every computed value.
"""

from erlbench import ToolContext, tool


class _Fmt:
    """Formatting helpers (values only, no reads or writes)."""

    @staticmethod
    def claim_number(row_id: str) -> str:
        """A claim number of the form RHC- plus 7 digits derived from a row id."""
        return "RHC-2" + f"{int(row_id[-6:], 16) % 1000000:06d}"


@tool(owner="user", rw="write")
def confirm_life_of_tread_cancellation_58ab2fcf(ctx: ToolContext, hazard_certificate_id: str,
                                                refund_amount: float, refund_tender: str) -> str:
    """The holder of a Crestline Road Hazard Life-of-Tread Protection certificate confirms, in person,
    the cancellation of that certificate and accepts the refund quoted to them. One call confirms the
    cancellation request awaiting the holder's confirmation on the certificate, or records a confirmed
    cancellation request when none is awaiting confirmation, changes the certificate's status to cancelled with
    today's date as its closing date, sets its remaining roadside service calls to zero, and books one
    pro-rata cancellation refund entry for the stated amount to the stated tender. Once it succeeds the
    certificate no longer covers any tire and the refund shows on the certificate's history.

    Args:
        hazard_certificate_id: Id class — reference number of the road hazard certificate being
            cancelled, as returned by the certificate lookup for this holder.
        refund_amount: Fixed-format class — the refund paid to the holder, in USD, rounded to 2 decimal
            places; 0.00 when no refund is due.
        refund_tender: Enum class — the tender the certificate was paid with, which receives the refund:
            cash_or_debit when the certificate was paid in cash or by debit card; bank_card when the
            certificate was paid with a bank-issued credit card.

    Returns:
        str: a confirmation line naming the confirmed cancellation request reference (cancel request id), the
        certificate reference with its new status cancelled, the closing date (YYYY-MM-DD), the refund
        entry reference (refund entry id), the refund amount in USD with 2 decimal places and the
        tender refunded. A line starting with "Cancelled" means the cancellation and refund are on file;
        a line starting with "Error:" means the tender was not one of the listed values and nothing was
        written.
    """
    if refund_tender not in ("cash_or_debit", "bank_card"):
        return "Error: refund_tender must be cash_or_debit or bank_card."
    today = ctx.now()[:10]
    amount = round(float(refund_amount), 2)
    tender = refund_tender
    awaiting = sorted(ctx.find("hazard_cancellation_requests", hazard_certificate_id=hazard_certificate_id,
                               request_status="pending_customer_confirmation"),
                      key=lambda r: r.get("created_at") or "")
    if awaiting:
        req_id = awaiting[-1]["hazard_cancel_request_id"]
        ctx.update("hazard_cancellation_requests", req_id, request_status="confirmed")
    else:
        req_id = ctx.make_id("hcr_", hazard_certificate_id, amount, refund_tender)
        ctx.create("hazard_cancellation_requests", req_id, hazard_cancel_request_id=req_id,
                   customer_id=(ctx.find("hazard_certificates", hazard_certificate_id=hazard_certificate_id) or [{}])[0].get("customer_id", ""),
                   hazard_certificate_id=hazard_certificate_id, request_status="confirmed", created_at=ctx.now())
    ctx.update("hazard_certificates", hazard_certificate_id, status="cancelled", closed_date=today,
               roadside_calls_remaining=0)
    evt_id = ctx.make_id("hev_", hazard_certificate_id, amount, refund_tender, "refund")
    ctx.create("hazard_events", evt_id, hazard_event_id=evt_id, hazard_certificate_id=hazard_certificate_id,
               customer_id=(ctx.find("hazard_certificates", hazard_certificate_id=hazard_certificate_id) or [{}])[0].get("customer_id", ""),
               event_type="hazard_cancellation_refund", event_date=today, amount=amount,
               refund_basis="pro_rata", payment_method=tender)
    return (f"Cancelled: cancel request id {req_id}; certificate {hazard_certificate_id} status cancelled, "
            f"closing date {today}; refund entry id {evt_id}, amount {amount:.2f} USD to {tender}.")


@tool(owner="agent", rw="write")
def post_hazard_counter_replacement_324c4972(ctx: ToolContext, hazard_certificate_id: str, tire_position: str,
                                              damage_type: str, service_date: str, store_id: str, odometer: int,
                                              remaining_tread_32nds: int, coverage_pct: int,
                                              replacement_price: float, amount: float) -> str:
    """Posts to a road hazard certificate a covered replacement that a Crestline store already carried
    out at its counter, so that the plan's share of that replacement is on the certificate's claim
    history. One call opens a new claim number and books one replacement entry for the wheel position
    with the service date, store, odometer, tread measured on the damaged tire, damage type, coverage
    percentage, price the percentage was applied to and the plan's share. Once it succeeds the
    replacement counts toward the certificate's claims and benefits paid.

    Args:
        hazard_certificate_id: Id class — reference number of the road hazard certificate the
            replacement is posted to, as returned by the certificate lookup for this holder.
        tire_position: Enum class — wheel position of the replaced tire: LF for the left front wheel;
            RF for the right front wheel; LR for the left rear wheel; RR for the right rear wheel; SP for
            the matching full-size spare; none when no wheel position applies to the entry.
        damage_type: Enum class — damage the technician found on the replaced tire: puncture_tread for a
            puncture in the tread area; puncture_shoulder for a puncture in the shoulder; sidewall_cut
            for a cut or gash in the sidewall; impact_break for a break or bulge from an impact;
            bead_damage for damage at the bead; none when no damage applies to the entry.
        service_date: Fixed-format class — date the store replaced the tire, as YYYY-MM-DD.
        store_id: Id class — reference number of the Crestline store that replaced the tire, as shown on
            the tread inspection record of the damaged tire.
        odometer: Fixed-format class — odometer at the replacement, in integer miles.
        remaining_tread_32nds: Fixed-format class — tread measured on the damaged tire, as an
            integer, 32nds of an inch.
        coverage_pct: Fixed-format class — share of the price the plan pays, an integer percent 0-100.
        replacement_price: Fixed-format class — price per tire the coverage percentage was applied to, in
            USD, rounded to 2 decimal places.
        amount: Fixed-format class — the plan's share of the replacement, in USD, rounded to 2 decimal
            places.

    Returns:
        str: a confirmation line with the replacement entry reference (replacement entry id), the new
        claim number (RHC- followed by 7 digits), the wheel position, the coverage percentage and the
        plan's share in USD with 2 decimal places. A line starting with "Posted" means the replacement
        is on the certificate.
    """
    amt = round(float(amount), 2)
    price = round(float(replacement_price), 2)
    evt_id = ctx.make_id("hev_", hazard_certificate_id, tire_position, damage_type, service_date, store_id,
                         odometer, remaining_tread_32nds, coverage_pct, price, amt)
    claim = _Fmt.claim_number(evt_id)
    cert = (ctx.find("hazard_certificates", hazard_certificate_id=hazard_certificate_id) or [{}])[0]
    ctx.create("hazard_events", evt_id, hazard_event_id=evt_id, hazard_certificate_id=hazard_certificate_id,
               customer_id=cert.get("customer_id", ""), event_type="hazard_replacement",
               event_date=ctx.now()[:10], service_date=service_date, store_id=store_id, claim_number=claim,
               odometer=int(odometer), tire_position=tire_position, damage_type=damage_type,
               remaining_tread_32nds=int(remaining_tread_32nds), coverage_pct=int(coverage_pct),
               replacement_price=price, amount=amt)
    return (f"Posted: replacement entry id {evt_id}; claim number {claim}; position {tire_position}; "
            f"coverage {int(coverage_pct)} percent; plan share {amt:.2f} USD.")


@tool(owner="agent", rw="write")
def reimburse_hazard_outside_replacement_5f5d3272(ctx: ToolContext, hazard_certificate_id: str, tire_position: str,
                                                   damage_type: str, service_date: str,
                                                   remaining_tread_32nds: int, coverage_pct: int,
                                                   amount: float, payment_method: str) -> str:
    """Books the reimbursement of a covered tire replacement the holder bought from a shop outside the
    Crestline network while far from any Crestline store. One call opens a new claim number and books
    one out-of-area replacement reimbursement entry on the certificate with the receipt date, wheel
    position, damage on the receipt, tread on the receipt, coverage percentage, amount reimbursed and the
    tender it is paid to. Once it succeeds the reimbursement counts toward the certificate's claims,
    the position's replacements and the benefits paid.

    Args:
        hazard_certificate_id: Id class — reference number of the road hazard certificate the
            reimbursement is paid under, as returned by the certificate lookup for this holder.
        tire_position: Enum class — wheel position of the replaced tire: LF for the left front wheel;
            RF for the right front wheel; LR for the left rear wheel; RR for the right rear wheel; SP for
            the matching full-size spare; none when no wheel position applies to the entry.
        damage_type: Enum class — damage shown on the receipt: puncture_tread for a puncture in the tread
            area; puncture_shoulder for a puncture in the shoulder; sidewall_cut for a cut or gash in the
            sidewall; impact_break for a break or bulge from an impact; bead_damage for damage at the
            bead; none when no damage applies to the entry.
        service_date: Fixed-format class — date printed on the outside shop's receipt, as YYYY-MM-DD.
        remaining_tread_32nds: Fixed-format class — tread depth shown on the outside shop's receipt for the
            damaged tire, as an integer, 32nds of an inch.
        coverage_pct: Fixed-format class — share applied to the replacement, an integer percent 0-100.
        amount: Fixed-format class — amount reimbursed to the holder, in USD, rounded to 2 decimal places.
        payment_method: Enum class — tender the reimbursement is paid to: none when no tender applies;
            cash_or_debit when the certificate was paid in cash or by debit card; bank_card when the
            certificate was paid with a bank-issued credit card; crestline_card when the certificate was
            paid with a Crestline credit card; fleet_account when the certificate was charged to a
            Crestline fleet account.

    Returns:
        str: a confirmation line with the reimbursement entry reference (reimbursement entry id), the
        new claim number (RHC- followed by 7 digits), the wheel position, the coverage percentage, the
        amount reimbursed in USD with 2 decimal places and the tender. A line starting with "Reimbursed"
        means the reimbursement is on the certificate.
    """
    amt = round(float(amount), 2)
    evt_id = ctx.make_id("hev_", hazard_certificate_id, tire_position, damage_type, service_date,
                         remaining_tread_32nds, coverage_pct, amt, payment_method)
    claim = _Fmt.claim_number(evt_id)
    cert = (ctx.find("hazard_certificates", hazard_certificate_id=hazard_certificate_id) or [{}])[0]
    ctx.create("hazard_events", evt_id, hazard_event_id=evt_id, hazard_certificate_id=hazard_certificate_id,
               customer_id=cert.get("customer_id", ""), event_type="hazard_third_party_reimbursement",
               event_date=ctx.now()[:10], service_date=service_date, claim_number=claim,
               tire_position=tire_position, damage_type=damage_type,
               remaining_tread_32nds=int(remaining_tread_32nds), coverage_pct=int(coverage_pct),
               amount=amt, reimbursement_type="replacement", payment_method=payment_method)
    return (f"Reimbursed: reimbursement entry id {evt_id}; claim number {claim}; position {tire_position}; "
            f"coverage {int(coverage_pct)} percent; amount {amt:.2f} USD to {payment_method}.")


@tool(owner="user", rw="write")
def authorize_hazard_store_replacement_0d9adf2d(ctx: ToolContext, hazard_certificate_id: str, tire_position: str,
                                                damage_type: str, service_date: str, store_id: str, odometer: int,
                                                remaining_tread_32nds: int, coverage_pct: int,
                                                replacement_price: float, amount: float) -> str:
    """The holder of a road hazard certificate authorizes, in person, a covered replacement of a damaged
    tire at a Crestline store on the terms quoted to them. One call opens a new claim number and books one
    replacement entry on the certificate for the wheel position with the service date, store, odometer,
    tread measured on the damaged tire, damage type, coverage percentage, price the percentage applies
    to and the plan's share. Once it succeeds the replacement is on the certificate's claim history and
    the store can mount the new tire.

    Args:
        hazard_certificate_id: Id class — reference number of the road hazard certificate the
            replacement is claimed under, as read out by the agent from the certificate lookup.
        tire_position: Enum class — wheel position of the replaced tire: LF for the left front wheel;
            RF for the right front wheel; LR for the left rear wheel; RR for the right rear wheel; SP for
            the matching full-size spare; none when no wheel position applies to the entry.
        damage_type: Enum class — damage the technician found on the tire: puncture_tread for a puncture
            in the tread area; puncture_shoulder for a puncture in the shoulder; sidewall_cut for a cut or
            gash in the sidewall; impact_break for a break or bulge from an impact; bead_damage for damage
            at the bead; none when no damage applies to the entry.
        service_date: Fixed-format class — date of the replacement, as YYYY-MM-DD.
        store_id: Id class — reference number of the Crestline store replacing the tire, as shown on the
            tread inspection record of the damaged tire.
        odometer: Fixed-format class — odometer at the replacement, in integer miles.
        remaining_tread_32nds: Fixed-format class — tread measured on the damaged tire, as an integer,
            32nds of an inch.
        coverage_pct: Fixed-format class — share of the price the plan pays, an integer percent 0-100.
        replacement_price: Fixed-format class — price per tire the coverage percentage applies to, in USD,
            rounded to 2 decimal places.
        amount: Fixed-format class — the plan's share of the replacement, in USD, rounded to 2 decimal
            places.

    Returns:
        str: a confirmation line with the replacement entry reference (replacement entry id), the new
        claim number (RHC- followed by 7 digits), the wheel position, the coverage percentage and the
        plan's share in USD with 2 decimal places. A line starting with "Authorized" means the
        replacement is on the certificate.
    """
    amt = round(float(amount), 2)
    price = round(float(replacement_price), 2)
    evt_id = ctx.make_id("hev_", hazard_certificate_id, tire_position, damage_type, service_date, store_id,
                         odometer, remaining_tread_32nds, coverage_pct, price, amt, "authorized")
    claim = _Fmt.claim_number(evt_id)
    cert = (ctx.find("hazard_certificates", hazard_certificate_id=hazard_certificate_id) or [{}])[0]
    ctx.create("hazard_events", evt_id, hazard_event_id=evt_id, hazard_certificate_id=hazard_certificate_id,
               customer_id=cert.get("customer_id", ""), event_type="hazard_replacement",
               event_date=ctx.now()[:10], service_date=service_date, store_id=store_id, claim_number=claim,
               odometer=int(odometer), tire_position=tire_position, damage_type=damage_type,
               remaining_tread_32nds=int(remaining_tread_32nds), coverage_pct=int(coverage_pct),
               replacement_price=price, amount=amt)
    return (f"Authorized: replacement entry id {evt_id}; claim number {claim}; position {tire_position}; "
            f"coverage {int(coverage_pct)} percent; plan share {amt:.2f} USD.")


@tool(owner="agent", rw="write")
def reimburse_hazard_outside_tow_3bff1c36(ctx: ToolContext, hazard_certificate_id: str, claim_number: str,
                                          service_date: str, tow_miles: int, amount: float, payment_method: str) -> str:
    """Books the reimbursement of a tow the holder paid an outside operator for while far from any
    Crestline store, and uses one of the certificate's roadside service calls. One call books one
    out-of-area tow reimbursement entry with the receipt date, towing distance, amount reimbursed and
    tender, and lowers the certificate's remaining roadside calls by one. The entry is booked under the
    claim number given; when the claim number is left empty, the call opens a new claim number (RHC-2
    followed by 6 digits) and books the entry under it.
    The entry is then part of the certificate's claim history and benefits paid.

    Args:
        hazard_certificate_id: Id class — reference number of the road hazard certificate the tow is
            reimbursed under, as returned by the certificate lookup for this holder.
        claim_number: Fixed-format class — claim number to book the tow under, in the format RHC-
            followed by 7 digits (e.g. RHC-0482913), as shown on a claim entry of the certificate; an
            empty string means no claim number is given and a new one is opened.
        service_date: Fixed-format class — date printed on the tow operator's receipt, as YYYY-MM-DD.
        tow_miles: Fixed-format class — towing distance shown on the receipt, in integer miles.
        amount: Fixed-format class — amount reimbursed for the tow, in USD, rounded to 2 decimal places.
        payment_method: Enum class — tender the reimbursement is paid to: none when no tender applies;
            cash_or_debit when the certificate was paid in cash or by debit card; bank_card when the
            certificate was paid with a bank-issued credit card; crestline_card when the certificate was
            paid with a Crestline credit card; fleet_account when the certificate was charged to a
            Crestline fleet account.

    Returns:
        str: a confirmation line with the reimbursement entry reference (reimbursement entry id), the
        claim number the entry is booked under (the given one, or the newly opened one), the amount
        reimbursed in USD with 2 decimal places, the tender, and the roadside calls left on the
        certificate (an integer). A line starting with "Reimbursed" means the tow is on
        the certificate.
    """
    amt = round(float(amount), 2)
    evt_id = ctx.make_id("hev_", hazard_certificate_id, claim_number, service_date, tow_miles, amt, payment_method, "tow")
    claim = claim_number or _Fmt.claim_number(evt_id)
    cert = (ctx.find("hazard_certificates", hazard_certificate_id=hazard_certificate_id) or [{}])[0]
    left = max(0, int(cert.get("roadside_calls_remaining") or 0) - 1)
    ctx.create("hazard_events", evt_id, hazard_event_id=evt_id, hazard_certificate_id=hazard_certificate_id,
               customer_id=cert.get("customer_id", ""), event_type="hazard_third_party_reimbursement",
               event_date=ctx.now()[:10], service_date=service_date, claim_number=claim, tire_position="none",
               damage_type="none", tow_miles=int(tow_miles), coverage_pct=100, amount=amt,
               reimbursement_type="tow", payment_method=payment_method)
    ctx.update("hazard_certificates", hazard_certificate_id, roadside_calls_remaining=left)
    return (f"Reimbursed: reimbursement entry id {evt_id}; claim number {claim}; tow amount {amt:.2f} USD to "
            f"{payment_method}; roadside calls left {left}.")


@tool(owner="agent", rw="write")
def reimburse_hazard_outside_repair_444e27b0(ctx: ToolContext, hazard_certificate_id: str, claim_number: str,
                                             tire_position: str, damage_type: str, service_date: str,
                                             amount: float, payment_method: str) -> str:
    """Books the reimbursement of a tire repair the holder paid an outside shop for while far from any
    Crestline store, under a given claim number. One call books one
    out-of-area repair reimbursement entry with the claim number, wheel position, damage, receipt date,
    amount reimbursed and tender. Once it succeeds the repair counts toward the position's covered
    repairs and the certificate's benefits paid.

    Args:
        hazard_certificate_id: Id class — reference number of the road hazard certificate the repair is
            reimbursed under, as returned by the certificate lookup for this holder.
        claim_number: Fixed-format class — claim number to book the repair under, in the format
            RHC- followed by 7 digits (e.g. RHC-0482913), as shown on a claim entry of the certificate.
        tire_position: Enum class — wheel position of the repaired tire: LF for the left front wheel;
            RF for the right front wheel; LR for the left rear wheel; RR for the right rear wheel; SP for
            the matching full-size spare; none when no wheel position applies to the entry.
        damage_type: Enum class — damage on the receipt: puncture_tread for a puncture in the tread area;
            puncture_shoulder for a puncture in the shoulder; sidewall_cut for a cut or gash in the
            sidewall; impact_break for a break or bulge from an impact; bead_damage for damage at the
            bead; none when no damage applies to the entry.
        service_date: Fixed-format class — date printed on the outside shop's receipt, as YYYY-MM-DD.
        amount: Fixed-format class — amount reimbursed for the repair, in USD, rounded to 2 decimal places.
        payment_method: Enum class — tender the reimbursement is paid to: none when no tender applies;
            cash_or_debit when the certificate was paid in cash or by debit card; bank_card when the
            certificate was paid with a bank-issued credit card; crestline_card when the certificate was
            paid with a Crestline credit card; fleet_account when the certificate was charged to a
            Crestline fleet account.

    Returns:
        str: a confirmation line with the reimbursement entry reference (reimbursement entry id), the
        claim number, the wheel position, the amount reimbursed in USD with 2 decimal places and the
        tender. A line starting with "Reimbursed" means the repair is on the certificate.
    """
    amt = round(float(amount), 2)
    evt_id = ctx.make_id("hev_", hazard_certificate_id, claim_number, tire_position, damage_type, service_date,
                         amt, payment_method, "repair")
    cert = (ctx.find("hazard_certificates", hazard_certificate_id=hazard_certificate_id) or [{}])[0]
    ctx.create("hazard_events", evt_id, hazard_event_id=evt_id, hazard_certificate_id=hazard_certificate_id,
               customer_id=cert.get("customer_id", ""), event_type="hazard_third_party_reimbursement",
               event_date=ctx.now()[:10], service_date=service_date, claim_number=claim_number,
               tire_position=tire_position, damage_type=damage_type, coverage_pct=100, amount=amt,
               reimbursement_type="repair", payment_method=payment_method)
    return (f"Reimbursed: reimbursement entry id {evt_id}; claim number {claim_number}; position {tire_position}; "
            f"repair amount {amt:.2f} USD to {payment_method}.")

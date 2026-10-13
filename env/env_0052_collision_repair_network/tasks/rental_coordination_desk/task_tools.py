"""Hidden task tools of the rental_coordination_desk difficulty (Crestline Collision & Glass).

Each tool performs one atomic write on a replacement-rental reservation and is reached only through
unlock_* -> call_*; its name is published in the rental charter's extended policies. No tool checks a
business precondition or works out an amount: the caller supplies the value the policy gives.
"""

from erlbench import ToolContext, tool


class _Reservation:
    """Internal lookups shared by the tools below (not a tool)."""

    @staticmethod
    def renter_of(ctx: ToolContext, rental_reservation_id: str):
        rows = ctx.find("rental_reservations", rental_reservation_id=rental_reservation_id)
        return rows[0].get("customer_id") if rows else None


@tool(owner="agent", rw="write")
def credit_rental_billing_error_4d32ac17(ctx: ToolContext, rental_reservation_id: str, source_entry_id: str,
                                         amount_usd: float) -> str:
    """Book a billing-error credit against one customer charge on a replacement-rental reservation. The
    credit reduces what the renter owes on the rental by the amount given and names the charge it
    corrects; once booked it appears in the rental's day and money history as a customer credit with
    reason billing_error, dated today, and the renter's outstanding share falls by that amount.

    Args:
        rental_reservation_id: Id class — reference number of the rental reservation the charge was
            posted on, as returned by the rental reservation lookup.
        source_entry_id: Id class — reference number of the customer charge entry being corrected, as
            returned by the rental day and money history lookup.
        amount_usd: Fixed-format class — amount credited, in USD, 2 decimal places, positive; the value
            is rounded half-up to the cent when booked.

    Returns:
        A dictionary receipt: status ("booked" when the credit was recorded), rental_entry_id (reference
        number of the new credit entry), rental_reservation_id (the reservation credited),
        source_entry_id (the charge the credit names), credit_reason (always "billing_error"),
        amount_usd (the amount credited, USD with 2 decimal places) and entry_date (booking date,
        YYYY-MM-DD).
    """
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("rbe_", rental_reservation_id, source_entry_id, amount)
    day = ctx.now()[:10]
    ctx.create("rental_ledger", rid, rental_entry_id=rid, rental_reservation_id=rental_reservation_id,
               customer_id=_Reservation.renter_of(ctx, rental_reservation_id), event_type="rental_customer_credit",
               entry_date=day, source_entry_id=source_entry_id, credit_reason="billing_error", amount_usd=amount)
    return str({"status": "booked", "rental_entry_id": rid, "rental_reservation_id": rental_reservation_id,
                "source_entry_id": source_entry_id, "credit_reason": "billing_error", "amount_usd": amount,
                "entry_date": day})


@tool(owner="agent", rw="write")
def credit_repair_customer_discount_d339b3bd(ctx: ToolContext, rental_reservation_id: str, source_entry_id: str,
                                             amount_usd: float) -> str:
    """Book the repair-customer discount on a customer-pay replacement rental as a credit against the
    rental's time charge. The renter's outstanding share falls by the amount given; the credit appears
    in the rental's day and money history as a customer credit with reason customer_pay_discount,
    dated today, naming the charge it reduces.

    Args:
        rental_reservation_id: Id class — reference number of the rental reservation, as returned by the
            rental reservation lookup.
        source_entry_id: Id class — reference number of the time charge entry the discount reduces, as
            returned by the rental day and money history lookup.
        amount_usd: Fixed-format class — discount amount credited, in USD, 2 decimal places, positive;
            the value is rounded half-up to the cent when booked.

    Returns:
        A dictionary receipt: status ("booked" when the discount was recorded), rental_entry_id
        (reference number of the new credit entry), rental_reservation_id (the reservation credited),
        source_entry_id (the time charge the discount names), credit_reason (always
        "customer_pay_discount"), amount_usd (the amount credited, USD with 2 decimal places) and
        entry_date (booking date, YYYY-MM-DD).
    """
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("rcd_", rental_reservation_id, source_entry_id, amount)
    day = ctx.now()[:10]
    ctx.create("rental_ledger", rid, rental_entry_id=rid, rental_reservation_id=rental_reservation_id,
               customer_id=_Reservation.renter_of(ctx, rental_reservation_id), event_type="rental_customer_credit",
               entry_date=day, source_entry_id=source_entry_id, credit_reason="customer_pay_discount",
               amount_usd=amount)
    return str({"status": "booked", "rental_entry_id": rid, "rental_reservation_id": rental_reservation_id,
                "source_entry_id": source_entry_id, "credit_reason": "customer_pay_discount", "amount_usd": amount,
                "entry_date": day})


@tool(owner="agent", rw="write")
def charge_young_renter_fee_a6a6d206(ctx: ToolContext, rental_reservation_id: str, days_count: int,
                                     amount_usd: float) -> str:
    """Post the young-renter fee to the renter's share of a returned replacement rental's final invoice.
    One customer charge of kind young_renter is added to the rental's day and money history, dated
    today, for the rental days it covers and the amount given; the renter's outstanding share rises by
    that amount.

    Args:
        rental_reservation_id: Id class — reference number of the rental reservation, as returned by the
            rental reservation lookup.
        days_count: Fixed-format class — rental days the young-renter charge covers, an integer count in
            integer rental days (whole days, no fraction).
        amount_usd: Fixed-format class — young-renter charge amount, in USD, 2 decimal places, positive;
            the value is rounded half-up to the cent when posted.

    Returns:
        A dictionary receipt: status ("posted" when the charge was recorded), rental_entry_id (reference
        number of the new charge entry), rental_reservation_id (the reservation charged), charge_type
        (always "young_renter"), settlement_kind (always "final"), days_count (integer rental days
        covered), amount_usd (the amount charged, USD with 2 decimal places) and entry_date (posting
        date, YYYY-MM-DD).
    """
    amount = round(float(amount_usd), 2)
    days = int(days_count)
    rid = ctx.make_id("ryr_", rental_reservation_id, days, amount)
    day = ctx.now()[:10]
    ctx.create("rental_ledger", rid, rental_entry_id=rid, rental_reservation_id=rental_reservation_id,
               customer_id=_Reservation.renter_of(ctx, rental_reservation_id), event_type="rental_customer_charge",
               entry_date=day, settlement_kind="final", charge_type="young_renter", days_count=days,
               amount_usd=amount)
    return str({"status": "posted", "rental_entry_id": rid, "rental_reservation_id": rental_reservation_id,
                "charge_type": "young_renter", "settlement_kind": "final", "days_count": days,
                "amount_usd": amount, "entry_date": day})


@tool(owner="user", rw="write")
def accept_rental_goodwill_credit_52804ea3(ctx: ToolContext, rental_reservation_id: str, source_entry_id: str,
                                           amount_usd: float) -> str:
    """Let the renter accept, on their own rental, the goodwill credit the desk has offered against one of
    the rental's customer charges. Accepting books the credit: a customer credit with reason goodwill,
    dated today, naming the charge it reduces, appears in the rental's day and money history and the
    renter's outstanding share falls by the amount accepted.

    Args:
        rental_reservation_id: Id class — reference number of the renter's rental reservation, as read out
            by the desk from the rental reservation lookup.
        source_entry_id: Id class — reference number of the customer charge the goodwill credit reduces, as
            read out by the desk from the rental day and money history lookup.
        amount_usd: Fixed-format class — goodwill amount accepted, in USD, 2 decimal places, positive; the
            value is rounded half-up to the cent when booked.

    Returns:
        A dictionary receipt: status ("accepted" when the credit was booked), rental_entry_id (reference
        number of the new credit entry), rental_reservation_id (the reservation credited),
        source_entry_id (the charge the credit names), credit_reason (always "goodwill"), amount_usd (the
        amount credited, USD with 2 decimal places) and entry_date (booking date, YYYY-MM-DD).
    """
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("rgw_", rental_reservation_id, source_entry_id, amount)
    day = ctx.now()[:10]
    ctx.create("rental_ledger", rid, rental_entry_id=rid, rental_reservation_id=rental_reservation_id,
               customer_id=_Reservation.renter_of(ctx, rental_reservation_id), event_type="rental_customer_credit",
               entry_date=day, source_entry_id=source_entry_id, credit_reason="goodwill", amount_usd=amount)
    return str({"status": "accepted", "rental_entry_id": rid, "rental_reservation_id": rental_reservation_id,
                "source_entry_id": source_entry_id, "credit_reason": "goodwill", "amount_usd": amount,
                "entry_date": day})


@tool(owner="agent", rw="write")
def authorize_network_courtesy_days_8334cede(ctx: ToolContext, rental_reservation_id: str, claim_repair_id: str,
                                             authorization_number: int, days_count: int) -> str:
    """Authorize network courtesy days on an insurance replacement rental: covered rental days paid by the
    network for a delay the network caused on the insurance claim repair the rental is for. One covered-day
    authorization (reason network_delay_courtesy, paid by the network, no insurer request) is added to the
    rental's day and money history, dated today; the rental's covered days grow by the days given.

    Args:
        rental_reservation_id: Id class — reference number of the rental reservation, as returned by the
            rental reservation lookup.
        claim_repair_id: Id class — reference number of the insurance claim repair order the rental is for, as
            shown on the reservation and returned by the claim repair lookup.
        authorization_number: Fixed-format class — ordinal of this authorization on the reservation, an
            integer >= 1 (one more than the highest authorization number already on the rental).
        days_count: Fixed-format class — courtesy days authorized, an integer count in integer rental days.

    Returns:
        A dictionary receipt: status ("authorized" when the authorization was recorded), rental_entry_id
        (reference number of the new authorization entry), rental_reservation_id (the reservation),
        authorization_number (integer ordinal), authorization_reason (always "network_delay_courtesy"),
        paid_by (always "network"), days_count (integer days authorized) and entry_date (YYYY-MM-DD).
    """
    days, number = int(days_count), int(authorization_number)
    rid = ctx.make_id("rnc_", rental_reservation_id, claim_repair_id, number, days)
    day = ctx.now()[:10]
    ctx.create("rental_ledger", rid, rental_entry_id=rid, rental_reservation_id=rental_reservation_id,
               customer_id=_Reservation.renter_of(ctx, rental_reservation_id), event_type="rental_authorization",
               entry_date=day, authorization_number=number, authorization_reason="network_delay_courtesy",
               extension_request_id=None, paid_by="network", days_count=days)
    return str({"status": "authorized", "rental_entry_id": rid, "rental_reservation_id": rental_reservation_id,
                "authorization_number": number, "authorization_reason": "network_delay_courtesy", "paid_by": "network",
                "days_count": days, "entry_date": day})


@tool(owner="agent", rw="write")
def authorize_insurer_extension_days_b8e4d7d7(ctx: ToolContext, rental_reservation_id: str, claim_repair_id: str,
                                              extension_request_id: str, authorization_number: int,
                                              days_count: int) -> str:
    """Post an extension the insurer approved as covered rental days paid by the insurer on an insurance
    replacement rental. One covered-day authorization naming the approved extension request, with that
    request's ground as its reason and paid by the insurer, is added to the rental's day and money history,
    dated today; the rental's covered days grow by the days given.

    Args:
        rental_reservation_id: Id class — reference number of the rental reservation, as returned by the
            rental reservation lookup.
        claim_repair_id: Id class — reference number of the insurance claim repair order the rental is for, as
            shown on the reservation and returned by the claim repair lookup.
        extension_request_id: Id class — reference number of the insurer-approved extension request being
            posted, as returned by the rental extension request lookup.
        authorization_number: Fixed-format class — ordinal of this authorization on the reservation, an
            integer >= 1 (one more than the highest authorization number already on the rental).
        days_count: Fixed-format class — extension days authorized, an integer count in integer rental days.

    Returns:
        A dictionary receipt: status ("authorized" when the authorization was recorded), rental_entry_id
        (reference number of the new authorization entry), rental_reservation_id (the reservation),
        extension_request_id (the approved request named), authorization_number (integer ordinal),
        authorization_reason (the request's ground: repair_delay_supplement, parts_delay or
        total_loss_settlement), paid_by (always "insurer"), days_count (integer days authorized) and
        entry_date (YYYY-MM-DD).
    """
    days, number = int(days_count), int(authorization_number)
    requests = ctx.find("rental_extension_requests", extension_request_id=extension_request_id)
    reason = requests[0].get("request_reason") if requests else None
    rid = ctx.make_id("rie_", rental_reservation_id, claim_repair_id, extension_request_id, number, days)
    day = ctx.now()[:10]
    ctx.create("rental_ledger", rid, rental_entry_id=rid, rental_reservation_id=rental_reservation_id,
               customer_id=_Reservation.renter_of(ctx, rental_reservation_id), event_type="rental_authorization",
               entry_date=day, authorization_number=number, authorization_reason=reason,
               extension_request_id=extension_request_id, paid_by="insurer", days_count=days)
    return str({"status": "authorized", "rental_entry_id": rid, "rental_reservation_id": rental_reservation_id,
                "extension_request_id": extension_request_id, "authorization_number": number,
                "authorization_reason": reason, "paid_by": "insurer", "days_count": days, "entry_date": day})


@tool(owner="user", rw="write")
def authorize_self_pay_days_charge_125d1a79(ctx: ToolContext, rental_reservation_id: str, days_count: int,
                                            amount_usd: float) -> str:
    """Let the renter authorize, on their own returned insurance rental, the charge for the rental days no
    insurer or network authorization covers. Authorizing posts one customer charge of kind uncovered_days on
    the final invoice, dated today, for the days and amount given; the renter's outstanding share rises by
    that amount.

    Args:
        rental_reservation_id: Id class — reference number of the renter's rental reservation, as read out by
            the desk from the rental reservation lookup.
        days_count: Fixed-format class — self-pay rental days the charge covers, an integer count in integer
            rental days.
        amount_usd: Fixed-format class — self-pay charge amount, in USD, 2 decimal places, positive; the value
            is rounded half-up to the cent when posted.

    Returns:
        A dictionary receipt: status ("authorized" when the charge was posted), rental_entry_id (reference
        number of the new charge entry), rental_reservation_id (the reservation charged), charge_type (always
        "uncovered_days"), settlement_kind (always "final"), days_count (integer days covered), amount_usd (the
        amount charged, USD with 2 decimal places) and entry_date (posting date, YYYY-MM-DD).
    """
    amount, days = round(float(amount_usd), 2), int(days_count)
    rid = ctx.make_id("rsp_", rental_reservation_id, days, amount)
    day = ctx.now()[:10]
    ctx.create("rental_ledger", rid, rental_entry_id=rid, rental_reservation_id=rental_reservation_id,
               customer_id=_Reservation.renter_of(ctx, rental_reservation_id), event_type="rental_customer_charge",
               entry_date=day, settlement_kind="final", charge_type="uncovered_days", days_count=days,
               amount_usd=amount)
    return str({"status": "authorized", "rental_entry_id": rid, "rental_reservation_id": rental_reservation_id,
                "charge_type": "uncovered_days", "settlement_kind": "final", "days_count": days, "amount_usd": amount,
                "entry_date": day})

"""Hidden task tools of the alterations_and_tailoring difficulty (Marlowe & Finch Alterations).

Each tool books exactly one entry on one alteration ticket and moves that ticket's balance due by the
entry's amount; none of them judges eligibility, prerequisites or amounts.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def book_rush_fee_44a954b1(ctx: ToolContext, ticket_id: str, amount: float) -> str:
    """Book the rush service fee on one alteration ticket. One call adds a single rush fee charge, dated today, to the ticket's charges and raises the ticket's balance due by that amount; the customer then sees the rush fee among the ticket's charges and a higher balance due.

    Args:
        ticket_id: Id class — the reference number of the alteration ticket that receives the rush fee, as returned by the alteration ticket lookup for this customer.
        amount: Fixed-format class — the rush fee to charge, in USD, 2 decimal places, positive (dollars and cents); the value is stored exactly as given, rounded to 2 decimal places.

    Returns:
        A confirmation sentence (text) naming the new charge reference number (an opaque string starting with "arf_"), the ticket reference number, the rush fee booked in USD with 2 decimal places, and the ticket's new balance due in USD with 2 decimal places; receiving it means the rush fee is now standing on the ticket.
    """
    rid = ctx.make_id("arf_", ticket_id, amount)
    ctx.create("alteration_charges", rid, alteration_charge_id=rid, ticket_id=ticket_id,
               customer_id=(ctx.find("alteration_tickets", ticket_id=ticket_id) or [{}])[0].get("customer_id", ""),
               event_type="alteration_charge", charge_date=ctx.now()[:10], amount=round(float(amount), 2),
               charge_type="rush_fee", operation_code="not_applicable", fitting_number=0,
               waiver_reason="not_applicable", original_alteration_charge_id="", payment_kind="not_applicable",
               tender_type="not_applicable")
    old = float((ctx.find("alteration_tickets", ticket_id=ticket_id) or [{}])[0].get("balance_due") or 0)
    new_balance = round(old + round(float(amount), 2), 2)
    ctx.update("alteration_tickets", ticket_id, balance_due=new_balance)
    return (f"Rush fee {rid} booked on ticket {ticket_id}: {round(float(amount), 2):.2f} USD; "
            f"balance due now {new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def waive_rush_fee_f377d7ac(ctx: ToolContext, ticket_id: str, original_alteration_charge_id: str, amount: float) -> str:
    """Waive all or part of the rush fee charged on one alteration ticket as a Finch Circle rush fee waiver. One call adds a single waiver entry, dated today, that names the rush fee charge it waives, and lowers the ticket's balance due by the amount waived; the customer then sees the waiver beside the rush fee and a lower balance due.

    Args:
        ticket_id: Id class — the reference number of the alteration ticket that carries the charge being waived, as returned by the alteration ticket lookup for this customer.
        original_alteration_charge_id: Id class — the reference number of the rush fee charge being waived, as returned by the alteration charge lookup for that ticket.
        amount: Fixed-format class — the amount waived, in USD, 2 decimal places, positive (dollars and cents); the value is stored exactly as given, rounded to 2 decimal places.

    Returns:
        A confirmation sentence (text) naming the new waiver reference number (an opaque string starting with "awr_"), the ticket reference number, the charge reference number waived, the amount waived in USD with 2 decimal places, and the ticket's new balance due in USD with 2 decimal places; receiving it means the waiver is now standing on the ticket.
    """
    rid = ctx.make_id("awr_", ticket_id, original_alteration_charge_id, amount)
    ctx.create("alteration_charges", rid, alteration_charge_id=rid, ticket_id=ticket_id,
               customer_id=(ctx.find("alteration_tickets", ticket_id=ticket_id) or [{}])[0].get("customer_id", ""),
               event_type="alteration_charge_waiver", charge_date=ctx.now()[:10], amount=round(float(amount), 2),
               charge_type="not_applicable", operation_code="not_applicable", fitting_number=0,
               waiver_reason="loyalty_rush_waiver", original_alteration_charge_id=original_alteration_charge_id,
               payment_kind="not_applicable", tender_type="not_applicable")
    old = float((ctx.find("alteration_tickets", ticket_id=ticket_id) or [{}])[0].get("balance_due") or 0)
    new_balance = round(old - round(float(amount), 2), 2)
    ctx.update("alteration_tickets", ticket_id, balance_due=new_balance)
    return (f"Waiver {rid} booked on ticket {ticket_id} against charge {original_alteration_charge_id}: "
            f"{round(float(amount), 2):.2f} USD waived; balance due now {new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def waive_complimentary_work_96f02105(ctx: ToolContext, ticket_id: str, original_alteration_charge_id: str, amount: float) -> str:
    """Waive all or part of one operation charge on an alteration ticket as complimentary basic work for a garment bought at Marlowe & Finch. One call adds a single waiver entry, dated today, that names the operation charge it waives, and lowers the ticket's balance due by the amount waived; the customer then sees the complimentary waiver beside that operation and a lower balance due.

    Args:
        ticket_id: Id class — the reference number of the alteration ticket that carries the charge being waived, as returned by the alteration ticket lookup for this customer.
        original_alteration_charge_id: Id class — the reference number of the operation charge being waived, as returned by the alteration charge lookup for that ticket.
        amount: Fixed-format class — the amount waived, in USD, 2 decimal places, positive (dollars and cents); the value is stored exactly as given, rounded to 2 decimal places.

    Returns:
        A confirmation sentence (text) naming the new waiver reference number (an opaque string starting with "acw_"), the ticket reference number, the charge reference number waived, the amount waived in USD with 2 decimal places, and the ticket's new balance due in USD with 2 decimal places; receiving it means the waiver is now standing on the ticket.
    """
    rid = ctx.make_id("acw_", ticket_id, original_alteration_charge_id, amount)
    ctx.create("alteration_charges", rid, alteration_charge_id=rid, ticket_id=ticket_id,
               customer_id=(ctx.find("alteration_tickets", ticket_id=ticket_id) or [{}])[0].get("customer_id", ""),
               event_type="alteration_charge_waiver", charge_date=ctx.now()[:10], amount=round(float(amount), 2),
               charge_type="not_applicable", operation_code="not_applicable", fitting_number=0,
               waiver_reason="complimentary_basic", original_alteration_charge_id=original_alteration_charge_id,
               payment_kind="not_applicable", tender_type="not_applicable")
    old = float((ctx.find("alteration_tickets", ticket_id=ticket_id) or [{}])[0].get("balance_due") or 0)
    new_balance = round(old - round(float(amount), 2), 2)
    ctx.update("alteration_tickets", ticket_id, balance_due=new_balance)
    return (f"Waiver {rid} booked on ticket {ticket_id} against charge {original_alteration_charge_id}: "
            f"{round(float(amount), 2):.2f} USD waived; balance due now {new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def waive_quote_overrun_938dcea5(ctx: ToolContext, ticket_id: str, original_alteration_charge_id: str, amount: float) -> str:
    """Waive the part of an alteration ticket's operation charges that runs above the quote the customer was given, as a quote overrun waiver. One call adds a single waiver entry, dated today, that names the operation charge it is booked against, and lowers the ticket's balance due by the amount waived; the customer then sees the quote overrun waiver and a lower balance due.

    Args:
        ticket_id: Id class — the reference number of the alteration ticket that carries the charge being waived, as returned by the alteration ticket lookup for this customer.
        original_alteration_charge_id: Id class — the reference number of the operation charge that took the ticket's charges above its quote being waived, as returned by the alteration charge lookup for that ticket.
        amount: Fixed-format class — the amount waived, in USD, 2 decimal places, positive (dollars and cents); the value is stored exactly as given, rounded to 2 decimal places.

    Returns:
        A confirmation sentence (text) naming the new waiver reference number (an opaque string starting with "aqw_"), the ticket reference number, the charge reference number waived, the amount waived in USD with 2 decimal places, and the ticket's new balance due in USD with 2 decimal places; receiving it means the waiver is now standing on the ticket.
    """
    rid = ctx.make_id("aqw_", ticket_id, original_alteration_charge_id, amount)
    ctx.create("alteration_charges", rid, alteration_charge_id=rid, ticket_id=ticket_id,
               customer_id=(ctx.find("alteration_tickets", ticket_id=ticket_id) or [{}])[0].get("customer_id", ""),
               event_type="alteration_charge_waiver", charge_date=ctx.now()[:10], amount=round(float(amount), 2),
               charge_type="not_applicable", operation_code="not_applicable", fitting_number=0,
               waiver_reason="quote_overrun", original_alteration_charge_id=original_alteration_charge_id,
               payment_kind="not_applicable", tender_type="not_applicable")
    old = float((ctx.find("alteration_tickets", ticket_id=ticket_id) or [{}])[0].get("balance_due") or 0)
    new_balance = round(old - round(float(amount), 2), 2)
    ctx.update("alteration_tickets", ticket_id, balance_due=new_balance)
    return (f"Waiver {rid} booked on ticket {ticket_id} against charge {original_alteration_charge_id}: "
            f"{round(float(amount), 2):.2f} USD waived; balance due now {new_balance:.2f} USD.")


@tool(owner="agent", rw="write")
def book_lined_surcharge_bf0414f9(ctx: ToolContext, ticket_id: str, operation_code: str, amount: float) -> str:
    """Book the lined-garment surcharge for one operation on an alteration ticket whose garment is lined. One call adds a single lined surcharge charge, dated today, for the named operation and raises the ticket's balance due by that amount; the customer then sees the lined surcharge listed under that operation and a higher balance due.

    Args:
        ticket_id: Id class — the reference number of the alteration ticket that receives the surcharge, as returned by the alteration ticket lookup for this customer.
        operation_code: Enum class — the operation the surcharge belongs to, exactly as the operation is written on that operation's charge; one of hem_plain (a plain hem), hem_cuffed (a cuffed hem), hem_blind_stitch (a blind-stitched hem), sleeve_shorten_plain (plain sleeve shortening), waist_take_in (taking in a waist), waist_let_out (letting out a waist), taper_legs (tapering trouser legs), side_seams_take_in (taking in the side seams), jacket_sleeve_shorten (shortening suit jacket sleeves), jacket_sleeve_shorten_working_buttons (shortening jacket sleeves with working buttons), jacket_take_in (taking in a jacket), trouser_hem_cuffed (a cuffed suit trouser hem), trouser_waist_adjust (adjusting a suit trouser waist), shoulder_adjust (adjusting jacket shoulders), gown_hem_single_layer (a single-layer gown hem), gown_hem_multi_layer (a multi-layer gown hem), bodice_take_in (taking in a bodice), strap_adjust (adjusting straps), tuxedo_trouser_hem (a tuxedo trouser hem), bridal_hem_multi_layer (a multi-layer bridal hem), bustle_add (adding a bustle), bridal_bodice_take_in (taking in a bridal bodice), sleeve_or_strap_adjust (adjusting bridal sleeves or straps), veil_shorten (shortening a veil), leather_sleeve_shorten (shortening leather sleeves), leather_hem (a leather hem), zipper_replace (replacing a zipper), beaded_hem (a beaded or sequined hem).
        amount: Fixed-format class — the lined surcharge to charge, in USD, 2 decimal places, positive (dollars and cents); the value is stored exactly as given, rounded to 2 decimal places.

    Returns:
        A confirmation sentence (text) naming the new charge reference number (an opaque string starting with "als_"), the ticket reference number, the operation the surcharge belongs to, the surcharge booked in USD with 2 decimal places, and the ticket's new balance due in USD with 2 decimal places; receiving it means the lined surcharge is now standing on the ticket.
    """
    code = str(operation_code)
    rid = ctx.make_id("als_", ticket_id, operation_code, amount)
    ctx.create("alteration_charges", rid, alteration_charge_id=rid, ticket_id=ticket_id,
               customer_id=(ctx.find("alteration_tickets", ticket_id=ticket_id) or [{}])[0].get("customer_id", ""),
               event_type="alteration_charge", charge_date=ctx.now()[:10], amount=round(float(amount), 2),
               charge_type="lined_surcharge", operation_code=code, fitting_number=0,
               waiver_reason="not_applicable", original_alteration_charge_id="", payment_kind="not_applicable",
               tender_type="not_applicable")
    old = float((ctx.find("alteration_tickets", ticket_id=ticket_id) or [{}])[0].get("balance_due") or 0)
    new_balance = round(old + round(float(amount), 2), 2)
    ctx.update("alteration_tickets", ticket_id, balance_due=new_balance)
    return (f"Lined surcharge {rid} booked on ticket {ticket_id} for {code}: {round(float(amount), 2):.2f} USD; "
            f"balance due now {new_balance:.2f} USD.")


@tool(owner="user", rw="write")
def book_extra_fitting_87db3b08(ctx: ToolContext, ticket_id: str, fitting_number: int, amount: float) -> str:
    """The customer records, and accepts the fee for, one more fitting with the tailor beyond the fittings included in the price of the alteration ticket. One call adds a single extra fitting fee charge, dated today, carrying the fitting's place among the extra fittings, and raises the ticket's balance due by the fee; it does not set a date or time for the fitting. The customer then sees the extra fitting fee on the ticket and a higher balance due.

    Args:
        ticket_id: Id class — the reference number of the customer's alteration ticket the fitting is for, as the agent reads it out from the ticket lookup.
        fitting_number: Fixed-format class — the place of this fitting among the extra (charged) fittings of the ticket, an integer counted from 1.
        amount: Fixed-format class — the fee for this extra fitting, in USD, 2 decimal places, positive (dollars and cents) as the agent states it; the value is stored exactly as given, rounded to 2 decimal places.

    Returns:
        A confirmation sentence (text) naming the new charge reference number (an opaque string starting with "aef_"), the ticket reference number, the extra fitting number as an integer, the fee booked in USD with 2 decimal places, and the ticket's new balance due in USD with 2 decimal places; receiving it means the extra fitting fee is standing on the ticket.
    """
    rid = ctx.make_id("aef_", ticket_id, fitting_number, amount)
    ctx.create("alteration_charges", rid, alteration_charge_id=rid, ticket_id=ticket_id,
               customer_id=(ctx.find("alteration_tickets", ticket_id=ticket_id) or [{}])[0].get("customer_id", ""),
               event_type="alteration_charge", charge_date=ctx.now()[:10], amount=round(float(amount), 2),
               charge_type="extra_fitting_fee", operation_code="not_applicable", fitting_number=int(fitting_number),
               waiver_reason="not_applicable", original_alteration_charge_id="", payment_kind="not_applicable",
               tender_type="not_applicable")
    old = float((ctx.find("alteration_tickets", ticket_id=ticket_id) or [{}])[0].get("balance_due") or 0)
    new_balance = round(old + round(float(amount), 2), 2)
    ctx.update("alteration_tickets", ticket_id, balance_due=new_balance)
    return (f"Extra fitting {int(fitting_number)} fee charged as {rid} on ticket {ticket_id}: fee "
            f"{round(float(amount), 2):.2f} USD; balance due now {new_balance:.2f} USD.")


@tool(owner="user", rw="write")
def pay_ticket_deposit_a1dd4c80(ctx: ToolContext, ticket_id: str, amount: float, tender_type: str) -> str:
    """The customer pays the deposit on their own alteration ticket with one tender. One call adds a single deposit payment, dated today, to the ticket and lowers the ticket's balance due by the amount paid; the customer then sees the deposit among the ticket's payments and a lower balance due.

    Args:
        ticket_id: Id class — the reference number of the customer's alteration ticket, as the agent reads it out from the ticket lookup.
        amount: Fixed-format class — the deposit paid, in USD, 2 decimal places, positive (dollars and cents) as the agent states it; the value is stored exactly as given, rounded to 2 decimal places.
        tender_type: Enum class — how the customer pays, as the customer chooses; one of mf_card (charged to the customer's Marlowe & Finch store card or Marlowe & Finch Mastercard), bank_card (charged to another bank's credit card), debit (paid with a debit card), cash (paid in cash at the store counter), gift_card (paid from a Marlowe & Finch gift card).

    Returns:
        A confirmation sentence (text) naming the new payment reference number (an opaque string starting with "adp_"), the ticket reference number, the deposit paid in USD with 2 decimal places, the tender used, and the ticket's new balance due in USD with 2 decimal places; receiving it means the deposit is paid and recorded on the ticket.
    """
    tender = str(tender_type)
    rid = ctx.make_id("adp_", ticket_id, amount, tender_type)
    ctx.create("alteration_charges", rid, alteration_charge_id=rid, ticket_id=ticket_id,
               customer_id=(ctx.find("alteration_tickets", ticket_id=ticket_id) or [{}])[0].get("customer_id", ""),
               event_type="alteration_payment", charge_date=ctx.now()[:10], amount=round(float(amount), 2),
               charge_type="not_applicable", operation_code="not_applicable", fitting_number=0,
               waiver_reason="not_applicable", original_alteration_charge_id="", payment_kind="deposit",
               tender_type=tender)
    old = float((ctx.find("alteration_tickets", ticket_id=ticket_id) or [{}])[0].get("balance_due") or 0)
    new_balance = round(old - round(float(amount), 2), 2)
    ctx.update("alteration_tickets", ticket_id, balance_due=new_balance)
    return (f"Deposit {rid} paid on ticket {ticket_id}: {round(float(amount), 2):.2f} USD by {tender}; "
            f"balance due now {new_balance:.2f} USD.")

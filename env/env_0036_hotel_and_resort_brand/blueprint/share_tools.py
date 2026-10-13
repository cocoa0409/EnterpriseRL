"""Shared tools for env_0036_hotel_and_resort_brand (Ashbury Hotels & Resorts guest services
and loyalty desk). Output of the erl-scenario-blueprint skill.

Every tool here is a SHARE tool, always present in its owner's tool list:
  - one record finder per table (the customers finder doubles as the identity entry);
  - the identity-verification write (the tool itself compares the stated details against the
    profile and passes at 2 matching details; it stores only the verified outcome);
  - the transfer-to-human write (exactly two reasons; a customer asking for a person 2 times
    qualifies as CUSTOMER_REQUESTED).
Customer-originated writes and every business write live in each difficulty's task_tools.py.
"""

from erlbench import ToolContext, tool


def _clean(d):
    # keep only the criteria the caller actually supplied
    return {k: v for k, v in d.items() if v not in ("", None)}


def _norm(v):
    # letters and digits only, case-folded: a stated reference number matches however it is spoken
    return "".join(ch for ch in str(v or "").casefold() if ch.isalnum())


def _narrow(rows, stated):
    # keep rows whose stated business reference numbers match after normalisation
    return [r for r in rows if all(_norm(r.get(k)) == _norm(v) for k, v in stated.items())]


# ----------------------------------------------------------------------------- customers
@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", name: str = "", phone_number: str = "",
                   email: str = "", organization_name: str = "") -> str:
    """Look up a guest or client profile at Ashbury Hotels & Resorts and establish whose account this
    contact is about. Search by the customer reference number, or by what a caller can naturally
    state: full name, phone number, email address or, for a group, meeting or corporate client, the
    organisation name. Every criterion is optional; supply whichever are known, and add another one
    if several profiles match. The profile returned carries the guest's contact details, date of
    birth, billing postal code, the last four digits of the card on file, the date the profile was
    created, and whether it belongs to an individual traveller or to an organisation's contact.
    Finding a profile does not verify the caller's identity.

    Args:
        customer_id: The customer reference number, if already known; leave "" otherwise.
        name: The caller's full name as they state it; leave "" if not given.
        phone_number: The phone number the caller gives, written NNN-NNN-NNNN; leave "" if not given.
        email: The email address the caller gives; leave "" if not given.
        organization_name: The organisation a group, meeting or corporate contact represents; leave "" if not given.
    """
    match = _clean({"customer_id": customer_id, "name": name, "phone_number": phone_number,
                    "email": email, "organization_name": organization_name})
    if not match:
        return "Error: provide at least one detail to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer profile matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} profiles match {match}; ask the caller for one more detail."
    return str(rows[0])


# ----------------------------------------------------------------------------- reservations
@tool(owner="agent", rw="read")
def find_booking_reservations(ctx: ToolContext, reservation_id: str = "", customer_id: str = "",
                              loyalty_member_id: str = "", group_block_id: str = "",
                              confirmation_number: str = "") -> str:
    """Look up room reservations. Each reservation shows the rate plan, hotel, brand, award category
    and award season, room type, arrival and departure dates, nights, adults, nightly rate and tax
    rate, booking date and channel, how it is guaranteed, any Ashbury Rewards membership, group block
    or corporate client code attached, points and Free Night Award nights used, and its status
    together with any cancellation, no-show, relocation, check-in, check-out or Best Rate Guarantee
    dates. Search by any reference you hold; all criteria are optional and combine.

    Args:
        reservation_id: Reference number of the reservation itself; leave "" if unknown.
        customer_id: Reference number of the guest holding the reservations; leave "" if unknown.
        loyalty_member_id: Reference number of the Ashbury Rewards membership credited for the reservations; leave "" if unknown.
        group_block_id: Reference number of the group block the reservations belong to; leave "" if unknown.
        confirmation_number: The 8-digit confirmation number the guest quotes; leave "" if not given.
    """
    match = _clean({"reservation_id": reservation_id, "customer_id": customer_id,
                    "loyalty_member_id": loyalty_member_id, "group_block_id": group_block_id})
    stated = _clean({"confirmation_number": confirmation_number})
    if not match and not stated:
        return "Error: provide at least one reference to look up reservations."
    rows = ctx.find("booking_reservations", **match) if match else ctx.fuzzy_find("booking_reservations", **stated)
    rows = _narrow(rows, stated)
    return str(rows) if rows else f"No reservations found for {dict(match, **stated)}."


@tool(owner="agent", rw="read")
def find_booking_charges(ctx: ToolContext, charge_id: str = "", reservation_id: str = "",
                         customer_id: str = "", related_charge_id: str = "") -> str:
    """Look up the money movements recorded on reservations before or instead of a stay: deposits and
    prepayments collected, refunded, forfeited or transferred to the guest bill, cancellation
    penalties, no-show charges and penalty reversals. Each entry shows its amount, posting date,
    how the amount was determined, whether it moved on the card on file or the advance deposit, the
    earlier entry it relates to and any reversal reason. All criteria are optional and combine.

    Args:
        charge_id: Reference number of the entry itself; leave "" if unknown.
        reservation_id: Reference number of the reservation the entries belong to; leave "" if unknown.
        customer_id: Reference number of the guest; leave "" if unknown.
        related_charge_id: Reference number of an earlier entry, to find the entries that refund, forfeit, transfer or reverse it; leave "" if unknown.
    """
    match = _clean({"charge_id": charge_id, "reservation_id": reservation_id,
                    "customer_id": customer_id, "related_charge_id": related_charge_id})
    if not match:
        return "Error: provide at least one reference to look up reservation charges."
    rows = ctx.find("booking_charges", **match)
    return str(rows) if rows else f"No reservation charges found for {match}."


# ----------------------------------------------------------------------------- folios
@tool(owner="agent", rw="read")
def find_folio_accounts(ctx: ToolContext, folio_id: str = "", customer_id: str = "",
                        reservation_id: str = "", loyalty_member_id: str = "",
                        folio_number: str = "") -> str:
    """Look up guest folios, the bill of each stay. A folio shows the hotel and its brand, the
    reservation it bills, the folio number printed on the bill, the dates it was opened and last
    settled, the membership credited for the stay, the current balance and whether it is open,
    settled or reopened for correction. All criteria are optional and combine.

    Args:
        folio_id: Reference number of the folio itself; leave "" if unknown.
        customer_id: Reference number of the guest; leave "" if unknown.
        reservation_id: Reference number of the reservation whose stay the folio bills; leave "" if unknown.
        loyalty_member_id: Reference number of the Ashbury Rewards membership credited for the stay; leave "" if unknown.
        folio_number: The 7-digit folio number printed on the guest's bill; leave "" if not given.
    """
    match = _clean({"folio_id": folio_id, "customer_id": customer_id,
                    "reservation_id": reservation_id, "loyalty_member_id": loyalty_member_id})
    stated = _clean({"folio_number": folio_number})
    if not match and not stated:
        return "Error: provide at least one reference to look up folios."
    rows = ctx.find("folio_accounts", **match) if match else ctx.fuzzy_find("folio_accounts", **stated)
    rows = _narrow(rows, stated)
    return str(rows) if rows else f"No folios found for {dict(match, **stated)}."


@tool(owner="agent", rw="read")
def find_folio_postings(ctx: ToolContext, posting_id: str = "", folio_id: str = "",
                        customer_id: str = "", related_posting_id: str = "") -> str:
    """Look up the lines of guest folios: room and room tax, resort fees, restaurant, minibar, spa,
    parking, pet and cleaning charges, late check-out and early departure fees, payments, refunds,
    adjustments and elite breakfast credits. Each line shows its transaction code, amount, the
    business date it belongs to, the date it was posted, its line number on the bill, the original
    line it corrects and any adjustment reason. All criteria are optional and combine.

    Args:
        posting_id: Reference number of the folio line itself; leave "" if unknown.
        folio_id: Reference number of the folio whose lines are wanted; leave "" if unknown.
        customer_id: Reference number of the guest; leave "" if unknown.
        related_posting_id: Reference number of an original line, to find the lines that correct, offset or refund it; leave "" if unknown.
    """
    match = _clean({"posting_id": posting_id, "folio_id": folio_id, "customer_id": customer_id,
                    "related_posting_id": related_posting_id})
    if not match:
        return "Error: provide at least one reference to look up folio lines."
    rows = ctx.find("folio_postings", **match)
    return str(rows) if rows else f"No folio lines found for {match}."


@tool(owner="agent", rw="read")
def find_folio_disputes(ctx: ToolContext, dispute_id: str = "", customer_id: str = "",
                        folio_id: str = "", posting_id: str = "") -> str:
    """Look up billing disputes that guest services has referred to a hotel's finance team. Each
    referral shows the folio and the single folio line disputed, the reason code, the amount of the
    correction requested, when it was registered and whether it is still with the hotel, upheld or
    declined. All criteria are optional and combine.

    Args:
        dispute_id: Reference number of the referral itself; leave "" if unknown.
        customer_id: Reference number of the guest; leave "" if unknown.
        folio_id: Reference number of the folio concerned; leave "" if unknown.
        posting_id: Reference number of the disputed folio line; leave "" if unknown.
    """
    match = _clean({"dispute_id": dispute_id, "customer_id": customer_id, "folio_id": folio_id,
                    "posting_id": posting_id})
    if not match:
        return "Error: provide at least one reference to look up billing disputes."
    rows = ctx.find("folio_disputes", **match)
    return str(rows) if rows else f"No billing disputes found for {match}."


# ----------------------------------------------------------------------------- loyalty
@tool(owner="agent", rw="read")
def find_loyalty_memberships(ctx: ToolContext, loyalty_member_id: str = "", customer_id: str = "",
                             member_number: str = "") -> str:
    """Look up Ashbury Rewards memberships. A membership shows the member number, current elite tier,
    the date that tier took effect and the date it is guaranteed through, enrolment and closing
    dates, status, any linked Ashbury Rewards co-brand card, the points balance and the elite night
    credits of the current calendar year. All criteria are optional and combine.

    Args:
        loyalty_member_id: Reference number of the membership itself; leave "" if unknown.
        customer_id: Reference number of the member's profile; leave "" if unknown.
        member_number: The 9-digit Ashbury Rewards member number the caller quotes; leave "" if not given.
    """
    match = _clean({"loyalty_member_id": loyalty_member_id, "customer_id": customer_id})
    stated = _clean({"member_number": member_number})
    if not match and not stated:
        return "Error: provide at least one reference to look up memberships."
    rows = ctx.find("loyalty_memberships", **match) if match else ctx.fuzzy_find("loyalty_memberships", **stated)
    rows = _narrow(rows, stated)
    return str(rows) if rows else f"No Ashbury Rewards memberships found for {dict(match, **stated)}."


@tool(owner="agent", rw="read")
def find_loyalty_transactions(ctx: ToolContext, transaction_id: str = "", loyalty_member_id: str = "",
                              customer_id: str = "", reservation_id: str = "", certificate_id: str = "",
                              counterparty_member_id: str = "", related_transaction_id: str = "") -> str:
    """Look up Ashbury Rewards account activity: points earned on stays, elite bonuses, welcome and
    promotion bonuses, purchases, transfers, award redemptions and refunds, Free Night Award
    top-offs, expiries and reversals, and elite night credits. Each transaction shows its points or
    nights, the stay or award it relates to, posting date, source, the qualifying spend it was
    computed on, any purchase price, the other member of a transfer and the transaction it
    reverses or mirrors. All criteria are optional and combine.

    Args:
        transaction_id: Reference number of the transaction itself; leave "" if unknown.
        loyalty_member_id: Reference number of the membership; leave "" if unknown.
        customer_id: Reference number of the member's profile; leave "" if unknown.
        reservation_id: Reference number of the stay or award reservation concerned; leave "" if unknown.
        certificate_id: Reference number of the Free Night Award a top-off concerns; leave "" if unknown.
        counterparty_member_id: Reference number of the other membership in a points transfer; leave "" if unknown.
        related_transaction_id: Reference number of an earlier transaction, to find what reverses or mirrors it; leave "" if unknown.
    """
    match = _clean({"transaction_id": transaction_id, "loyalty_member_id": loyalty_member_id,
                    "customer_id": customer_id, "reservation_id": reservation_id,
                    "certificate_id": certificate_id, "counterparty_member_id": counterparty_member_id,
                    "related_transaction_id": related_transaction_id})
    if not match:
        return "Error: provide at least one reference to look up account activity."
    rows = ctx.find("loyalty_transactions", **match)
    return str(rows) if rows else f"No Ashbury Rewards activity found for {match}."


# ----------------------------------------------------------------------------- free night awards
@tool(owner="agent", rw="read")
def find_free_night_certificates(ctx: ToolContext, certificate_id: str = "", customer_id: str = "",
                                 loyalty_member_id: str = "", reservation_id: str = "",
                                 replaced_certificate_id: str = "", certificate_number: str = "") -> str:
    """Look up Free Night Awards held in Ashbury Rewards accounts. Each award shows its type, award
    number, why it was issued, the issue and expiry dates, its status, the reservation and night it
    is applied to or was used on, any top-off points added, the award it replaces and the date it
    was used up, expired or forfeited. All criteria are optional and combine.

    Args:
        certificate_id: Reference number of the award itself; leave "" if unknown.
        customer_id: Reference number of the member's profile; leave "" if unknown.
        loyalty_member_id: Reference number of the membership holding the awards; leave "" if unknown.
        reservation_id: Reference number of the reservation an award is applied to; leave "" if unknown.
        replaced_certificate_id: Reference number of an earlier award, to find the award reissued for it; leave "" if unknown.
        certificate_number: The award number shown in the member's account (FNA followed by 8 digits); leave "" if not given.
    """
    match = _clean({"certificate_id": certificate_id, "customer_id": customer_id,
                    "loyalty_member_id": loyalty_member_id, "reservation_id": reservation_id,
                    "replaced_certificate_id": replaced_certificate_id})
    stated = _clean({"certificate_number": certificate_number})
    if not match and not stated:
        return "Error: provide at least one reference to look up Free Night Awards."
    rows = ctx.find("free_night_certificates", **match) if match else ctx.fuzzy_find("free_night_certificates", **stated)
    rows = _narrow(rows, stated)
    return str(rows) if rows else f"No Free Night Awards found for {dict(match, **stated)}."


@tool(owner="agent", rw="read")
def find_certificate_activity(ctx: ToolContext, activity_id: str = "", certificate_id: str = "",
                              customer_id: str = "", reservation_id: str = "") -> str:
    """Look up the history of Free Night Awards: when an award was placed on hold for a reservation
    night, released back to the account, used on a completed stay or forfeited. Each record shows
    the reservation and night, the standard-room points price of that night, any top-off points,
    the date and the reason. All criteria are optional and combine.

    Args:
        activity_id: Reference number of the history record itself; leave "" if unknown.
        certificate_id: Reference number of the award; leave "" if unknown.
        customer_id: Reference number of the member's profile; leave "" if unknown.
        reservation_id: Reference number of the reservation concerned; leave "" if unknown.
    """
    match = _clean({"activity_id": activity_id, "certificate_id": certificate_id,
                    "customer_id": customer_id, "reservation_id": reservation_id})
    if not match:
        return "Error: provide at least one reference to look up award history."
    rows = ctx.find("certificate_activity", **match)
    return str(rows) if rows else f"No Free Night Award history found for {match}."


# ----------------------------------------------------------------------------- group blocks
@tool(owner="agent", rw="read")
def find_group_blocks(ctx: ToolContext, group_block_id: str = "", customer_id: str = "",
                      group_code: str = "") -> str:
    """Look up group room block contracts. A block shows the block type, booking code, group name,
    hotel and brand, block dates, rooms on the peak night, contracted and currently held room
    nights, group rate and tax rate, cut-off date, signing and cancellation dates, status, the
    deposit held and the balance on the group master account. All criteria are optional and
    combine.

    Args:
        group_block_id: Reference number of the block itself; leave "" if unknown.
        customer_id: Reference number of the organiser's profile; leave "" if unknown.
        group_code: The 6-character group booking code the caller quotes; leave "" if not given.
    """
    match = _clean({"group_block_id": group_block_id, "customer_id": customer_id})
    stated = _clean({"group_code": group_code})
    if not match and not stated:
        return "Error: provide at least one reference to look up group blocks."
    rows = ctx.find("group_blocks", **match) if match else ctx.fuzzy_find("group_blocks", **stated)
    rows = _narrow(rows, stated)
    return str(rows) if rows else f"No group blocks found for {dict(match, **stated)}."


@tool(owner="agent", rw="read")
def find_group_ledger(ctx: ToolContext, group_entry_id: str = "", group_block_id: str = "",
                      customer_id: str = "", related_entry_id: str = "", amendment_id: str = "") -> str:
    """Look up the ledger of group blocks: room nights allocated, added, reduced and released at
    cut-off; deposits received, refunded, applied and forfeited; attrition and cancellation
    charges, rooms billed to the master account, complimentary room credits and organiser
    payments. Each entry shows its amount, room nights, date, basis, the entry it relates to and
    any addendum it implements. All criteria are optional and combine.

    Args:
        group_entry_id: Reference number of the entry itself; leave "" if unknown.
        group_block_id: Reference number of the block; leave "" if unknown.
        customer_id: Reference number of the organiser's profile; leave "" if unknown.
        related_entry_id: Reference number of an earlier entry, to find what refunds, applies or offsets it; leave "" if unknown.
        amendment_id: Reference number of a contract addendum, to find the entries implementing it; leave "" if unknown.
    """
    match = _clean({"group_entry_id": group_entry_id, "group_block_id": group_block_id,
                    "customer_id": customer_id, "related_entry_id": related_entry_id,
                    "amendment_id": amendment_id})
    if not match:
        return "Error: provide at least one reference to look up the group ledger."
    rows = ctx.find("group_ledger", **match)
    return str(rows) if rows else f"No group ledger entries found for {match}."


@tool(owner="agent", rw="read")
def find_group_amendments(ctx: ToolContext, amendment_id: str = "", customer_id: str = "",
                          group_block_id: str = "") -> str:
    """Look up contract addenda issued on group blocks: whether each adds or removes room nights,
    how many, when it was issued, and whether it is awaiting the organiser's signature, signed or
    withdrawn. All criteria are optional and combine.

    Args:
        amendment_id: Reference number of the addendum itself; leave "" if unknown.
        customer_id: Reference number of the organiser's profile; leave "" if unknown.
        group_block_id: Reference number of the block amended; leave "" if unknown.
    """
    match = _clean({"amendment_id": amendment_id, "customer_id": customer_id,
                    "group_block_id": group_block_id})
    if not match:
        return "Error: provide at least one reference to look up contract addenda."
    rows = ctx.find("group_amendments", **match)
    return str(rows) if rows else f"No contract addenda found for {match}."


# ----------------------------------------------------------------------------- meetings & events
@tool(owner="agent", rw="read")
def find_meeting_contracts(ctx: ToolContext, meeting_contract_id: str = "", customer_id: str = "",
                           group_block_id: str = "") -> str:
    """Look up meeting, banquet and wedding event contracts. A contract shows the package, event
    name, hotel, event date, contracted, guaranteed and actual attendance, any linked group room
    block, signing and cancellation dates, status, the deposit held and the balance due. All
    criteria are optional and combine.

    Args:
        meeting_contract_id: Reference number of the event contract itself; leave "" if unknown.
        customer_id: Reference number of the client contact's profile; leave "" if unknown.
        group_block_id: Reference number of the group room block contracted alongside; leave "" if unknown.
    """
    match = _clean({"meeting_contract_id": meeting_contract_id, "customer_id": customer_id,
                    "group_block_id": group_block_id})
    if not match:
        return "Error: provide at least one reference to look up event contracts."
    rows = ctx.find("meeting_contracts", **match)
    return str(rows) if rows else f"No event contracts found for {match}."


@tool(owner="agent", rw="read")
def find_meeting_ledger(ctx: ToolContext, meeting_entry_id: str = "", meeting_contract_id: str = "",
                        customer_id: str = "", related_entry_id: str = "") -> str:
    """Look up the bill of meeting and banquet events: deposits received, refunded, applied and
    forfeited; package, room rental, service charge, tax and incidental fee charges; minimum
    shortfall and cancellation charges; and client payments. Each entry shows its amount, the count
    it was computed on, date, bill component and related entry. All criteria are optional and
    combine.

    Args:
        meeting_entry_id: Reference number of the entry itself; leave "" if unknown.
        meeting_contract_id: Reference number of the event contract; leave "" if unknown.
        customer_id: Reference number of the client contact's profile; leave "" if unknown.
        related_entry_id: Reference number of an earlier entry, to find what refunds, applies or is charged on it; leave "" if unknown.
    """
    match = _clean({"meeting_entry_id": meeting_entry_id, "meeting_contract_id": meeting_contract_id,
                    "customer_id": customer_id, "related_entry_id": related_entry_id})
    if not match:
        return "Error: provide at least one reference to look up the event bill."
    rows = ctx.find("meeting_ledger", **match)
    return str(rows) if rows else f"No event bill entries found for {match}."


# ----------------------------------------------------------------------------- resort clubs
@tool(owner="agent", rw="read")
def find_club_memberships(ctx: ToolContext, club_membership_id: str = "", customer_id: str = "",
                          membership_number: str = "") -> str:
    """Look up resort club memberships. A membership shows the level, membership number, resort,
    start date, billing cycle, registered dependants, any freeze dates, the date a cancellation
    notice was received, the termination date, status, the dues balance and the guest passes left
    this membership year. All criteria are optional and combine.

    Args:
        club_membership_id: Reference number of the membership itself; leave "" if unknown.
        customer_id: Reference number of the primary member's profile; leave "" if unknown.
        membership_number: The club membership number the caller quotes (CLB followed by 6 digits); leave "" if not given.
    """
    match = _clean({"club_membership_id": club_membership_id, "customer_id": customer_id})
    stated = _clean({"membership_number": membership_number})
    if not match and not stated:
        return "Error: provide at least one reference to look up club memberships."
    rows = ctx.find("club_memberships", **match) if match else ctx.fuzzy_find("club_memberships", **stated)
    rows = _narrow(rows, stated)
    return str(rows) if rows else f"No club memberships found for {dict(match, **stated)}."


@tool(owner="agent", rw="read")
def find_club_ledger(ctx: ToolContext, club_entry_id: str = "", club_membership_id: str = "",
                     customer_id: str = "", related_entry_id: str = "") -> str:
    """Look up the account of resort club memberships: initiation fees, dues invoices, freeze and
    late fees, payments and credits, and the guest passes allocated, used and lapsed together with
    guest fees. Each entry shows its amount or passes, date, dues period, related entry and, for
    guest visits, the guest's name. All criteria are optional and combine.

    Args:
        club_entry_id: Reference number of the entry itself; leave "" if unknown.
        club_membership_id: Reference number of the membership; leave "" if unknown.
        customer_id: Reference number of the member's profile; leave "" if unknown.
        related_entry_id: Reference number of an earlier entry, to find what pays, credits or relates to it; leave "" if unknown.
    """
    match = _clean({"club_entry_id": club_entry_id, "club_membership_id": club_membership_id,
                    "customer_id": customer_id, "related_entry_id": related_entry_id})
    if not match:
        return "Error: provide at least one reference to look up the club account."
    rows = ctx.find("club_ledger", **match)
    return str(rows) if rows else f"No club account entries found for {match}."


@tool(owner="agent", rw="read")
def find_club_notices(ctx: ToolContext, notice_id: str = "", customer_id: str = "",
                      club_membership_id: str = "") -> str:
    """Look up membership notices prepared for resort club members: cancellation, cancellation on
    relocation, and medical freeze notices, each showing when it was prepared and whether it is
    awaiting the member's signature, signed or withdrawn. All criteria are optional and combine.

    Args:
        notice_id: Reference number of the notice itself; leave "" if unknown.
        customer_id: Reference number of the member's profile; leave "" if unknown.
        club_membership_id: Reference number of the membership concerned; leave "" if unknown.
    """
    match = _clean({"notice_id": notice_id, "customer_id": customer_id,
                    "club_membership_id": club_membership_id})
    if not match:
        return "Error: provide at least one reference to look up membership notices."
    rows = ctx.find("club_notices", **match)
    return str(rows) if rows else f"No membership notices found for {match}."


# ----------------------------------------------------------------------------- logs
@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "", customer_id: str = "") -> str:
    """Look up whether a customer's identity has been verified in this contact, and when the latest
    verification attempt was made. All criteria are optional and combine.

    Args:
        verification_id: Reference number of the verification record itself; leave "" if unknown.
        customer_id: Reference number of the customer; leave "" if unknown.
    """
    match = _clean({"verification_id": verification_id, "customer_id": customer_id})
    if not match:
        return "Error: provide at least one reference to look up verification records."
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No verification record found for {match}."


@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up transfers of a customer to a human representative, with the reason and the moment of
    each transfer. All criteria are optional and combine.

    Args:
        handoff_id: Reference number of the transfer record itself; leave "" if unknown.
        customer_id: Reference number of the customer; leave "" if unknown.
    """
    match = _clean({"handoff_id": handoff_id, "customer_id": customer_id})
    if not match:
        return "Error: provide at least one reference to look up transfers."
    rows = ctx.find("human_handoffs", **match)
    return str(rows) if rows else f"No transfers to a representative found for {match}."


# ----------------------------------------------------------------------------- verification
@tool(owner="agent", rw="write")
def verify_customer_identity(ctx: ToolContext, customer_id: str, phone_number: str = "",
                             email: str = "", date_of_birth: str = "", postal_code: str = "",
                             card_last4: str = "") -> str:
    """Verify the caller's identity and record the outcome for this contact. No reservation, folio,
    points, award, group, event or club business may be discussed or carried out on an account
    until this verification has passed. The comparison is made by this tool: each detail the caller
    states is compared with the customer's profile, and verification passes only when at least 2 of
    them match. The customer reference number only retrieves the profile and never counts as a
    match. Callers usually give only some details, so pass exactly the values the caller stated,
    unchanged, and leave the rest "". If an attempt fails and a later attempt with further details
    passes, the pass stands.

    Args:
        customer_id: The customer reference number read from the profile lookup. Required; used only to retrieve the profile and never counted as a match.
        phone_number: The phone number the caller states, written NNN-NNN-NNNN; leave "" if not stated.
        email: The email address the caller states; leave "" if not stated.
        date_of_birth: The caller's date of birth, written YYYY-MM-DD; leave "" if not stated.
        postal_code: The postal code of the caller's billing address; leave "" if not stated.
        card_last4: The last four digits of the payment card the caller says is on file; leave "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look the customer up first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The locator customer_id is deliberately not in `supplied`.
    supplied = {"phone_number": phone_number, "email": email, "date_of_birth": date_of_birth,
                "postal_code": postal_code, "card_last4": card_last4}
    matched = sum(1 for field, value in supplied.items()
                  if value and str(rec.get(field) or "").strip().lower() == str(value).strip().lower())
    verified = matched >= 2
    rid = ctx.make_id("ver_", customer_id)
    prior = ctx.find("identity_verifications", verification_id=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("identity_verifications", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("identity_verifications", rid, verification_id=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for {customer_id} ({matched} detail(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 2 details "
                 "matched). Ask the caller for another detail on file and try again.")


# ----------------------------------------------------------------------------- handoff
@tool(owner="agent", rw="write")
def transfer_to_human_agent(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Transfer the customer to a human guest services representative and record the transfer and
    its reason. Use POLICY_NOT_COVERED when no Ashbury Hotels & Resorts policy allows the request to
    be resolved; use CUSTOMER_REQUESTED when the customer has explicitly asked to speak with a
    person 2 times.

    Args:
        customer_id: The customer reference number read from the profile lookup (the profile must exist).
        reason: The reason for the transfer, exactly one of POLICY_NOT_COVERED (no policy allows the request to be resolved) or CUSTOMER_REQUESTED (the customer has explicitly asked for a person 2 times); never free text.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown transfer reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record the transfer."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Transfer to a human representative recorded for {customer_id} ({reason})."

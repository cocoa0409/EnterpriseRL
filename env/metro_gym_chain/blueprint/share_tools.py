"""Shared tools for metro_gym_chain. Output of the erl-scenario-blueprint skill.
Path: env/metro_gym_chain/blueprint/share_tools.py

Living in share_tools.py makes every tool here a SHARE tool: always present in its owner's tool
list, directly callable in every task. This file holds the three utilities every difficulty
reuses: the complete record-lookup layer (one finder per table -- and the customers finder
DOUBLES AS THE IDENTITY ENTRY by additionally taking the caller-stateable attributes), the
identity-verification write, and the transfer-to-human handoff.

Customer-originated writes (a member confirming a cancellation, disposing of their own balance,
signing up for something only they can consent to) do NOT live here -- those are difficulty-
specific hidden task tools (owner="user"), authored per difficulty in task_tools.py and reached
through unlock_user_discoverable_tool / call_user_discoverable_tool.

The identity-verification write compares the caller-supplied attribute values against the
member's profile itself and derives the match count to decide the outcome, but stores only the
`verified` boolean, never the match count. It, and the handoff write, take the INTERNAL
customer_id (read from the customers finder's return) purely as a locator to fetch the profile --
fetching a record is not proving identity, so customer_id never counts toward the match.
Identity verification requires at least 2 matching attributes (K = 2). The handoff reason is a
closed set of exactly two values: POLICY_NOT_COVERED and CUSTOMER_REQUESTED (the customer must
have explicitly asked for a human representative at least 3 times, R = 3).
"""

from erlbench import ToolContext, tool


# ---------------------------------------------------------------------------
# Uniform id-lookup layer: one share read tool per table, every `_id`-postfix
# field optional. Any record is reachable from the located member by construction.
# ---------------------------------------------------------------------------

@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", phone_number: str = "",
                    email: str = "", full_name: str = "", date_of_birth: str = "",
                    photo_id_last4: str = "", member_since_date: str = "",
                    home_club_id: str = "") -> str:
    """Look up a member's profile and establish whose account a call is about. Search by the
    member's reference number if it is already known, or by whatever the caller can naturally
    state -- their mobile number, email, full name, date of birth, the last 4 digits of the photo
    id on file, the date their profile was opened, or their home club reference number. Every
    search criterion is optional; supply whichever are known. The returned profile carries the
    member's contact details, identity-document details on file, home club, and the date the
    profile was opened. Looking a member up this way is not the same as verifying their identity;
    identity is verified separately before any account changes are made.

    Args:
        customer_id: The member's reference number, if already known; leave "" otherwise.
        phone_number: The registered mobile number on file, 10 digits with no punctuation; leave
            "" if not provided.
        email: The registered email address on file; leave "" if not provided.
        full_name: The member's full name; leave "" if not provided.
        date_of_birth: The member's date of birth, YYYY-MM-DD; leave "" if not provided.
        photo_id_last4: The last 4 digits of the photo id scanned at signup; leave "" if not
            provided.
        member_since_date: The date the member's profile was first opened, YYYY-MM-DD; leave ""
            if not provided.
        home_club_id: The reference number of the club the member most recently designated as
            home club; leave "" if not provided.
    """
    match = {k: v for k, v in {
        "customer_id": customer_id, "phone_number": phone_number, "email": email,
        "full_name": full_name, "date_of_birth": date_of_birth,
        "photo_id_last4": photo_id_last4, "member_since_date": member_since_date,
        "home_club_id": home_club_id,
    }.items() if v}
    if not match:
        return "Error: provide at least one reference number or profile detail to find the member."
    rows = ctx.find("customers", **match)
    if not rows:
        return f"No member matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} members match {match}; ask for one more detail to tell them apart."
    return str(rows[0])


@tool(owner="agent", rw="read")
def find_clubs(ctx: ToolContext, club_id: str = "") -> str:
    """Look up a club location's details -- its name, metro zone, whether it keeps 24-hour
    access hours, and whether it has a pool.

    Args:
        club_id: The club's reference number; leave "" to list every club location.
    """
    match = {k: v for k, v in {"club_id": club_id}.items() if v}
    rows = ctx.find("clubs", **match)
    return str(rows) if rows else f"No club records for {match}."


@tool(owner="agent", rw="read")
def find_membership_holdings(ctx: ToolContext, membership_id: str = "", customer_id: str = "",
                              home_club_id: str = "") -> str:
    """Look up club membership contracts -- the tier held, lifecycle status, home club, dues
    balance owed, guest-visit allowance remaining, and any freeze dates on file.

    Args:
        membership_id: The membership contract's own reference number; leave "" if unknown.
        customer_id: The reference number of the member who owns the membership; leave "" if
            unknown.
        home_club_id: The reference number of the club the membership is registered to; leave ""
            if unknown.
    """
    match = {k: v for k, v in {"membership_id": membership_id, "customer_id": customer_id,
                                "home_club_id": home_club_id}.items() if v}
    rows = ctx.find("membership_holdings", **match)
    return str(rows) if rows else f"No membership records for {match}."


@tool(owner="agent", rw="read")
def find_membership_events(ctx: ToolContext, event_id: str = "", membership_id: str = "",
                            customer_id: str = "", club_id: str = "") -> str:
    """Look up the billing and usage history on a membership -- dues charges, payments, waivers,
    guest-visit grants and usage, check-ins, and freeze history.

    Args:
        event_id: The specific history entry's own reference number; leave "" if unknown.
        membership_id: The reference number of the membership contract the entry belongs to;
            leave "" if unknown.
        customer_id: The reference number of the member the entry belongs to; leave "" if unknown.
        club_id: The reference number of the club a guest visit or check-in occurred at; leave ""
            if unknown.
    """
    match = {k: v for k, v in {"event_id": event_id, "membership_id": membership_id,
                                "customer_id": customer_id, "club_id": club_id}.items() if v}
    rows = ctx.find("membership_events", **match)
    return str(rows) if rows else f"No membership history entries for {match}."


@tool(owner="agent", rw="read")
def find_membership_cancellation_requests(ctx: ToolContext, cancellation_request_id: str = "",
                                           customer_id: str = "", membership_id: str = "") -> str:
    """Look up a membership cancellation request -- the effective date it will take hold and
    whether it is still pending, has been confirmed, or was withdrawn.

    Args:
        cancellation_request_id: The request's own reference number; leave "" if unknown.
        customer_id: The reference number of the member who filed the request; leave "" if
            unknown.
        membership_id: The reference number of the membership contract the request concerns;
            leave "" if unknown.
    """
    match = {k: v for k, v in {"cancellation_request_id": cancellation_request_id,
                                "customer_id": customer_id,
                                "membership_id": membership_id}.items() if v}
    rows = ctx.find("membership_cancellation_requests", **match)
    return str(rows) if rows else f"No cancellation requests for {match}."


@tool(owner="agent", rw="read")
def find_pt_holdings(ctx: ToolContext, pt_holding_id: str = "", customer_id: str = "") -> str:
    """Look up personal-training packages -- the tier held, lifecycle status, expiration date,
    sessions remaining, and the assigned trainer.

    Args:
        pt_holding_id: The package's own reference number; leave "" if unknown.
        customer_id: The reference number of the member who owns the package; leave "" if
            unknown.
    """
    match = {k: v for k, v in {"pt_holding_id": pt_holding_id,
                                "customer_id": customer_id}.items() if v}
    rows = ctx.find("pt_holdings", **match)
    return str(rows) if rows else f"No personal-training package records for {match}."


@tool(owner="agent", rw="read")
def find_pt_events(ctx: ToolContext, event_id: str = "", pt_holding_id: str = "",
                    customer_id: str = "") -> str:
    """Look up the session history on a personal-training package -- sessions redeemed, late
    cancellations, refunds, expirations, trainer reassignments, and bonus session grants.

    Args:
        event_id: The specific history entry's own reference number; leave "" if unknown.
        pt_holding_id: The reference number of the package the entry belongs to; leave "" if
            unknown.
        customer_id: The reference number of the member the entry belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"event_id": event_id, "pt_holding_id": pt_holding_id,
                                "customer_id": customer_id}.items() if v}
    rows = ctx.find("pt_events", **match)
    return str(rows) if rows else f"No personal-training history entries for {match}."


@tool(owner="agent", rw="read")
def find_class_pass_holdings(ctx: ToolContext, class_pass_id: str = "", customer_id: str = "") -> str:
    """Look up class-credit packs -- the tier held, lifecycle status, expiration date, and
    credits remaining.

    Args:
        class_pass_id: The pack's own reference number; leave "" if unknown.
        customer_id: The reference number of the member who owns the pack; leave "" if unknown.
    """
    match = {k: v for k, v in {"class_pass_id": class_pass_id,
                                "customer_id": customer_id}.items() if v}
    rows = ctx.find("class_pass_holdings", **match)
    return str(rows) if rows else f"No class-credit pack records for {match}."


@tool(owner="agent", rw="read")
def find_class_fitness_events(ctx: ToolContext, event_id: str = "", class_pass_id: str = "",
                               customer_id: str = "", club_id: str = "",
                               class_session_id: str = "") -> str:
    """Look up the booking history on a class-credit pack -- classes booked, in-window
    cancellations, no-shows, waitlist promotions, expirations, and refunds.

    Args:
        event_id: The specific history entry's own reference number; leave "" if unknown.
        class_pass_id: The reference number of the pack the entry belongs to; leave "" if unknown.
        customer_id: The reference number of the member the entry belongs to; leave "" if unknown.
        club_id: The reference number of the club the class was held at; leave "" if unknown.
        class_session_id: The reference number of the specific scheduled class; leave "" if
            unknown.
    """
    match = {k: v for k, v in {"event_id": event_id, "class_pass_id": class_pass_id,
                                "customer_id": customer_id, "club_id": club_id,
                                "class_session_id": class_session_id}.items() if v}
    rows = ctx.find("class_fitness_events", **match)
    return str(rows) if rows else f"No class-booking history entries for {match}."


@tool(owner="agent", rw="read")
def find_corporate_wellness_enrollments(ctx: ToolContext, enrollment_id: str = "",
                                         customer_id: str = "",
                                         employer_account_id: str = "") -> str:
    """Look up corporate wellness enrollments -- the employer's partnership tier, lifecycle
    status, employer name, and the balance billed to the employer's master account.

    Args:
        enrollment_id: The enrollment's own reference number; leave "" if unknown.
        customer_id: The reference number of the enrolled employee-member; leave "" if unknown.
        employer_account_id: The employer's corporate wellness account reference number; leave ""
            if unknown.
    """
    match = {k: v for k, v in {"enrollment_id": enrollment_id, "customer_id": customer_id,
                                "employer_account_id": employer_account_id}.items() if v}
    rows = ctx.find("corporate_wellness_enrollments", **match)
    return str(rows) if rows else f"No corporate wellness enrollment records for {match}."


@tool(owner="agent", rw="read")
def find_corporate_wellness_events(ctx: ToolContext, event_id: str = "", enrollment_id: str = "",
                                    customer_id: str = "", employer_account_id: str = "") -> str:
    """Look up the billing history on a corporate wellness enrollment -- dues billed to the
    employer's master account, payments received, and waivers granted.

    Args:
        event_id: The specific history entry's own reference number; leave "" if unknown.
        enrollment_id: The reference number of the enrollment the entry belongs to; leave "" if
            unknown.
        customer_id: The reference number of the enrolled employee-member; leave "" if unknown.
        employer_account_id: The employer's corporate wellness account reference number; leave ""
            if unknown.
    """
    match = {k: v for k, v in {"event_id": event_id, "enrollment_id": enrollment_id,
                                "customer_id": customer_id,
                                "employer_account_id": employer_account_id}.items() if v}
    rows = ctx.find("corporate_wellness_events", **match)
    return str(rows) if rows else f"No corporate wellness history entries for {match}."


@tool(owner="agent", rw="read")
def find_retail_credit_accounts(ctx: ToolContext, credit_account_id: str = "",
                                 customer_id: str = "") -> str:
    """Look up pro-shop store-credit accounts -- the tier held, lifecycle status, and the current
    spendable balance.

    Args:
        credit_account_id: The account's own reference number; leave "" if unknown.
        customer_id: The reference number of the member who owns the account; leave "" if
            unknown.
    """
    match = {k: v for k, v in {"credit_account_id": credit_account_id,
                                "customer_id": customer_id}.items() if v}
    rows = ctx.find("retail_credit_accounts", **match)
    return str(rows) if rows else f"No store-credit account records for {match}."


@tool(owner="agent", rw="read")
def find_retail_credit_events(ctx: ToolContext, event_id: str = "", credit_account_id: str = "",
                               customer_id: str = "") -> str:
    """Look up the transaction history on a store-credit account -- top-ups, redemptions,
    refunds, expirations, and automatic reloads.

    Args:
        event_id: The specific history entry's own reference number; leave "" if unknown.
        credit_account_id: The reference number of the account the entry belongs to; leave "" if
            unknown.
        customer_id: The reference number of the member the entry belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"event_id": event_id, "credit_account_id": credit_account_id,
                                "customer_id": customer_id}.items() if v}
    rows = ctx.find("retail_credit_events", **match)
    return str(rows) if rows else f"No store-credit transaction entries for {match}."


@tool(owner="agent", rw="read")
def find_household_addon_holdings(ctx: ToolContext, addon_id: str = "", customer_id: str = "") -> str:
    """Look up household add-on memberships -- the relationship tier, lifecycle status, the
    dependent's name and date of birth, and the balance owed.

    Args:
        addon_id: The add-on's own reference number; leave "" if unknown.
        customer_id: The reference number of the primary member the add-on is attached to; leave
            "" if unknown.
    """
    match = {k: v for k, v in {"addon_id": addon_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("household_addon_holdings", **match)
    return str(rows) if rows else f"No household add-on records for {match}."


@tool(owner="agent", rw="read")
def find_household_addon_events(ctx: ToolContext, event_id: str = "", addon_id: str = "",
                                 customer_id: str = "") -> str:
    """Look up the billing history on a household add-on -- dues charges, payments, and waivers.

    Args:
        event_id: The specific history entry's own reference number; leave "" if unknown.
        addon_id: The reference number of the add-on the entry belongs to; leave "" if unknown.
        customer_id: The reference number of the primary member the entry belongs to; leave "" if
            unknown.
    """
    match = {k: v for k, v in {"event_id": event_id, "addon_id": addon_id,
                                "customer_id": customer_id}.items() if v}
    rows = ctx.find("household_addon_events", **match)
    return str(rows) if rows else f"No household add-on history entries for {match}."


@tool(owner="agent", rw="read")
def find_locker_rental_holdings(ctx: ToolContext, locker_rental_id: str = "",
                                 customer_id: str = "", club_id: str = "") -> str:
    """Look up locker rentals -- the tier rented, lifecycle status, club and locker number, and
    the balance owed.

    Args:
        locker_rental_id: The rental's own reference number; leave "" if unknown.
        customer_id: The reference number of the member who owns the rental; leave "" if unknown.
        club_id: The reference number of the club the locker is located at; leave "" if unknown.
    """
    match = {k: v for k, v in {"locker_rental_id": locker_rental_id, "customer_id": customer_id,
                                "club_id": club_id}.items() if v}
    rows = ctx.find("locker_rental_holdings", **match)
    return str(rows) if rows else f"No locker rental records for {match}."


@tool(owner="agent", rw="read")
def find_locker_rental_events(ctx: ToolContext, event_id: str = "", locker_rental_id: str = "",
                               customer_id: str = "") -> str:
    """Look up the billing history on a locker rental -- monthly fees, damage and lost-key fees,
    payments, and waivers.

    Args:
        event_id: The specific history entry's own reference number; leave "" if unknown.
        locker_rental_id: The reference number of the rental the entry belongs to; leave "" if
            unknown.
        customer_id: The reference number of the member the entry belongs to; leave "" if unknown.
    """
    match = {k: v for k, v in {"event_id": event_id, "locker_rental_id": locker_rental_id,
                                "customer_id": customer_id}.items() if v}
    rows = ctx.find("locker_rental_events", **match)
    return str(rows) if rows else f"No locker rental history entries for {match}."


@tool(owner="agent", rw="read")
def find_day_pass_holdings(ctx: ToolContext, day_pass_id: str = "", customer_id: str = "",
                            club_id: str = "", sponsor_employer_account_id: str = "") -> str:
    """Look up day and trial passes -- the tier purchased, lifecycle status, club, validity
    window, and visits remaining.

    Args:
        day_pass_id: The pass's own reference number; leave "" if unknown.
        customer_id: The reference number of the member or visitor who owns the pass; leave "" if
            unknown.
        club_id: The reference number of the club the pass was purchased at or is valid for;
            leave "" if unknown.
        sponsor_employer_account_id: For a Corporate Guest Pass, the sponsoring employer's
            corporate wellness account reference number; leave "" if unknown.
    """
    match = {k: v for k, v in {
        "day_pass_id": day_pass_id, "customer_id": customer_id, "club_id": club_id,
        "sponsor_employer_account_id": sponsor_employer_account_id}.items() if v}
    rows = ctx.find("day_pass_holdings", **match)
    return str(rows) if rows else f"No day/trial pass records for {match}."


@tool(owner="agent", rw="read")
def find_day_pass_events(ctx: ToolContext, event_id: str = "", day_pass_id: str = "",
                          customer_id: str = "", club_id: str = "") -> str:
    """Look up the usage history on a day or trial pass -- visits used, expiration forfeitures,
    refunds, and extensions.

    Args:
        event_id: The specific history entry's own reference number; leave "" if unknown.
        day_pass_id: The reference number of the pass the entry belongs to; leave "" if unknown.
        customer_id: The reference number of the member or visitor the entry belongs to; leave ""
            if unknown.
        club_id: The reference number of the club a visit was used at; leave "" if unknown.
    """
    match = {k: v for k, v in {"event_id": event_id, "day_pass_id": day_pass_id,
                                "customer_id": customer_id, "club_id": club_id}.items() if v}
    rows = ctx.find("day_pass_events", **match)
    return str(rows) if rows else f"No day/trial pass history entries for {match}."


@tool(owner="agent", rw="read")
def find_identity_verifications(ctx: ToolContext, verification_id: str = "",
                                 customer_id: str = "") -> str:
    """Look up the identity-verification outcome currently on file for a member.

    Args:
        verification_id: The verification record's own reference number; leave "" if unknown.
        customer_id: The reference number of the member being checked; leave "" if unknown.
    """
    match = {k: v for k, v in {"verification_id": verification_id,
                                "customer_id": customer_id}.items() if v}
    rows = ctx.find("identity_verifications", **match)
    return str(rows) if rows else f"No identity verification records for {match}."


@tool(owner="agent", rw="read")
def find_human_handoffs(ctx: ToolContext, handoff_id: str = "", customer_id: str = "") -> str:
    """Look up prior hand-offs to a human representative for a member.

    Args:
        handoff_id: The hand-off record's own reference number; leave "" if unknown.
        customer_id: The reference number of the member handed off; leave "" if unknown.
    """
    match = {k: v for k, v in {"handoff_id": handoff_id, "customer_id": customer_id}.items() if v}
    rows = ctx.find("human_handoffs", **match)
    return str(rows) if rows else f"No hand-off records for {match}."


# ---------------------------------------------------------------------------
# Identity verification (K = 2 matching attributes)
# ---------------------------------------------------------------------------

@tool(owner="agent", rw="write")
def verify_member_identity(ctx: ToolContext, customer_id: str, phone_number: str = "",
                            email: str = "", date_of_birth: str = "",
                            photo_id_last4: str = "", member_since_date: str = "") -> str:
    """Verify a caller's identity before looking up or changing anything on their account, and
    record the outcome. This tool performs the comparison itself: it checks each piece of
    identity information the caller states against the profile on file, counts how many match,
    and passes only when at least 2 match. The member's reference number is used solely to
    retrieve the profile and is never counted as a match itself. Callers can usually state only
    some of the information on file, so pass only the values actually given, exactly as stated,
    and leave the rest blank. If an earlier attempt in the same call failed and a later attempt
    supplies enough additional information to pass, the pass is recorded and stands.

    Args:
        customer_id: The member's reference number, read from looking up their profile. Required;
            used only to retrieve that profile and not counted toward the number of matches.
        phone_number: The mobile number the caller states, 10 digits with no punctuation; leave
            "" if not stated.
        email: The email address the caller states; leave "" if not stated.
        date_of_birth: The date of birth the caller states, YYYY-MM-DD; leave "" if not stated.
        photo_id_last4: The last 4 digits of a photo id the caller states; leave "" if not
            stated.
        member_since_date: The date the caller states their profile was opened, YYYY-MM-DD; leave
            "" if not stated.
    """
    if not customer_id:
        return "Error: customer_id is required; look up the member first and pass their reference number."
    rows = ctx.find("customers", customer_id=customer_id)
    if not rows:
        return f"Error: no member {customer_id}; cannot verify."
    rec = rows[0]
    supplied = {"phone_number": phone_number, "email": email, "date_of_birth": date_of_birth,
                "photo_id_last4": photo_id_last4, "member_since_date": member_since_date}
    matched = sum(1 for field, value in supplied.items() if value and str(rec.get(field)) == str(value))
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
            else f"Identity NOT verified for {customer_id} (only {matched} of the required 2 "
                 "details matched). Ask the caller for another detail on file and call this tool again.")


# ---------------------------------------------------------------------------
# Transfer to a human representative (reason in {POLICY_NOT_COVERED, CUSTOMER_REQUESTED}; R = 3)
# ---------------------------------------------------------------------------

@tool(owner="agent", rw="write")
def transfer_to_human_representative(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """Hand the caller over to a human representative to continue the conversation, and record
    the hand-off and its reason.

    Args:
        customer_id: The member's reference number, read from looking up their profile. The
            profile must already exist.
        reason: The reason for the hand-off, one of exactly two values:
            POLICY_NOT_COVERED -- current policy offers no way to resolve the caller's request;
            CUSTOMER_REQUESTED -- the caller has explicitly asked to speak with a human
            representative at least 3 times in this conversation.
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown hand-off reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("customers", customer_id=customer_id):
        return f"Error: no member {customer_id}; cannot record hand-off."
    rid = ctx.make_id("hof_", customer_id, reason)
    ctx.create("human_handoffs", rid, handoff_id=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Hand-off to a human representative recorded for {customer_id} ({reason})."

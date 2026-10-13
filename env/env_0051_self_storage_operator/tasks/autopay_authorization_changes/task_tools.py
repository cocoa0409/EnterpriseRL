"""Hidden task tools for the autopay_authorization_changes difficulty (Bluegate AutoPay).

Each tool performs one atomic write on the AutoPay notice record of one authorization. The amount
written is the figure the caller passes in; no tool looks at balances, drafts or other records to
decide it, and no tool refuses a call because of the state of the account.
"""

from erlbench import ToolContext, tool


class _Lookup:
    """Plain record lookups shared by the tools below (not a tool)."""

    @staticmethod
    def owner_of(ctx: ToolContext, autopay_id: str) -> str:
        rows = ctx.find("autopay_enrollments", autopay_id=autopay_id)
        return rows[0].get("customer_id") if rows else ""


@tool(owner="user", rw="write")
def approve_unit_returned_draft_catchup_31270510(ctx: ToolContext, autopay_id: str, notice_type: str, related_due_date: str,
                                                 approved_amount: float) -> str:
    """The tenant, in person, approves a one-time catch-up draft on a storage unit AutoPay authorization
    for a rent due date whose bank-account draft came back unpaid. One call records, on that
    authorization's notice history, a new varying-amount notice dated today that carries the due date the
    catch-up concerns and the exact dollar amount the tenant approves to be drafted from the bank account
    on file. Nothing else on the authorization or on the rental agreement changes. On success the
    tenant receives a confirmation reference and can see the approved amount and due date on the
    authorization's notice history.

    Args:
        autopay_id: Id class — the AutoPay authorization number of the storage unit authorization the
            catch-up is drafted under, as shown in the AutoPay authorization lookup.
        notice_type: Enum class — the kind of notice record written, one of: "varying_amount_notice" — the
            record states an amount to be drafted or charged for one due date, which is the kind this action
            records; "card_expiry_reminder" — a reminder that the card on file is about to expire, carrying no
            amount; "draft_failure_notice" — word that a draft for a due date failed, carrying no amount;
            "suspension_notice" — word that the authorization has been suspended, carrying no amount.
        related_due_date: Fixed-format class — the rent due date whose returned draft the catch-up
            concerns, written YYYY-MM-DD as a calendar date (no time, no time zone).
        approved_amount: Fixed-format class — the catch-up amount the tenant approves, in US dollars as a
            positive decimal number with exactly 2 decimal places (for example 123.45); the value is
            stored rounded half-to-even to the cent by Python round(x, 2).

    Returns:
        A text receipt of the form "Catch-up approval <reference> recorded on AutoPay <autopay_id>:
        <approved_amount> USD for due date <related_due_date>, approved <date>." where <reference> is the
        new notice reference (a string starting with apn_), <approved_amount> is the stored amount with 2
        decimals, <related_due_date> is the due date as YYYY-MM-DD and <date> is today's date as
        YYYY-MM-DD. A receipt in this form means the approval is on record.
    """
    rid = ctx.make_id("apn_", autopay_id, notice_type, related_due_date, approved_amount, "unit_catchup")
    amount = round(float(approved_amount), 2)
    today = ctx.now()[:10]
    ctx.create("autopay_notices", rid, autopay_notice_id=rid, autopay_id=autopay_id,
               customer_id=_Lookup.owner_of(ctx, autopay_id), event_type="autopay_notice",
               notice_type=notice_type, notice_date=today,
               related_due_date=related_due_date, notified_amount=amount)
    return (f"Catch-up approval {rid} recorded on AutoPay {autopay_id}: {amount:.2f} USD for due date "
            f"{related_due_date}, approved {today}.")


@tool(owner="user", rw="write")
def approve_card_catchup_charge_edda4662(ctx: ToolContext, autopay_id: str, notice_type: str, related_due_date: str,
                                         approved_amount: float) -> str:
    """The tenant, in person, approves a one-time catch-up charge to the card on file of a card AutoPay
    authorization, for a rent due date whose card draft was declined for insufficient funds or an expired
    card, whether or not its retries are used. One call
    records, on that authorization's notice history, a new varying-amount notice dated today that carries
    the due date the charge concerns and the exact dollar amount the tenant approves to be charged to the
    card. Nothing else on the authorization or on the rental agreement changes. On success the tenant
    receives a confirmation reference and can see the approved charge and due date on the
    authorization's notice history.

    Args:
        autopay_id: Id class — the AutoPay authorization number of the card authorization to be charged,
            as shown in the AutoPay authorization lookup.
        notice_type: Enum class — the kind of notice record written, one of: "varying_amount_notice" — the
            record states an amount to be drafted or charged for one due date, which is the kind this action
            records; "card_expiry_reminder" — a reminder that the card on file is about to expire, carrying no
            amount; "draft_failure_notice" — word that a draft for a due date failed, carrying no amount;
            "suspension_notice" — word that the authorization has been suspended, carrying no amount.
        related_due_date: Fixed-format class — the rent due date whose declined card draft the charge
            concerns, written YYYY-MM-DD as a calendar date (no time, no time zone).
        approved_amount: Fixed-format class — the charge the tenant approves, in US dollars as a positive
            decimal number with exactly 2 decimal places (for example 123.45); the value is stored rounded
            half-to-even to the cent by Python round(x, 2).

    Returns:
        A text receipt of the form "Card catch-up charge <reference> approved on AutoPay <autopay_id>:
        <approved_amount> USD for due date <related_due_date>, approved <date>." where <reference> is the
        new notice reference (a string starting with apn_), <approved_amount> is the stored amount with 2
        decimals, <related_due_date> is the due date as YYYY-MM-DD and <date> is today's date as
        YYYY-MM-DD. A receipt in this form means the approval is on record.
    """
    rid = ctx.make_id("apn_", autopay_id, notice_type, related_due_date, approved_amount, "card_catchup")
    amount = round(float(approved_amount), 2)
    today = ctx.now()[:10]
    ctx.create("autopay_notices", rid, autopay_notice_id=rid, autopay_id=autopay_id,
               customer_id=_Lookup.owner_of(ctx, autopay_id), event_type="autopay_notice",
               notice_type=notice_type, notice_date=today,
               related_due_date=related_due_date, notified_amount=amount)
    return (f"Card catch-up charge {rid} approved on AutoPay {autopay_id}: {amount:.2f} USD for due date "
            f"{related_due_date}, approved {today}.")


@tool(owner="agent", rw="write")
def send_unit_varying_amount_notice_30e2b3fb(ctx: ToolContext, autopay_id: str, notice_type: str, related_due_date: str,
                                             notified_amount: float) -> str:
    """The care center sends the tenant a varying-amount notice for a storage unit AutoPay authorization,
    telling the tenant the amount that will be drafted for one coming rent due date. One call records,
    on that authorization's notice history, a new varying-amount notice dated today with the due date and
    the dollar amount stated to the tenant, and the notice goes to the tenant by email. Nothing else on
    the authorization or on the rental agreement changes. On success the tenant can see the notice, its
    date, due date and amount on the authorization's notice history.

    Args:
        autopay_id: Id class — the AutoPay authorization number of the storage unit authorization the
            notice is sent under, as shown in the AutoPay authorization lookup.
        notice_type: Enum class — the kind of notice record written, one of: "varying_amount_notice" — the
            record states an amount to be drafted or charged for one due date, which is the kind this action
            records; "card_expiry_reminder" — a reminder that the card on file is about to expire, carrying no
            amount; "draft_failure_notice" — word that a draft for a due date failed, carrying no amount;
            "suspension_notice" — word that the authorization has been suspended, carrying no amount.
        related_due_date: Fixed-format class — the rent due date whose draft the notice announces, written
            YYYY-MM-DD as a calendar date (no time, no time zone).
        notified_amount: Fixed-format class — the amount the notice tells the tenant will be drafted, in US
            dollars as a positive decimal number with exactly 2 decimal places (for example 123.45); the
            value is stored rounded half-to-even to the cent by Python round(x, 2).

    Returns:
        A text receipt of the form "Varying-amount notice <reference> sent on AutoPay <autopay_id>:
        <notified_amount> USD for due date <related_due_date>, sent <date>." where <reference> is the new
        notice reference (a string starting with apn_), <notified_amount> is the stored amount with 2
        decimals, <related_due_date> is the due date as YYYY-MM-DD and <date> is today's date as
        YYYY-MM-DD. A receipt in this form means the notice has been sent and recorded.
    """
    rid = ctx.make_id("apn_", autopay_id, notice_type, related_due_date, notified_amount, "unit_notice")
    amount = round(float(notified_amount), 2)
    today = ctx.now()[:10]
    ctx.create("autopay_notices", rid, autopay_notice_id=rid, autopay_id=autopay_id,
               customer_id=_Lookup.owner_of(ctx, autopay_id), event_type="autopay_notice",
               notice_type=notice_type, notice_date=today,
               related_due_date=related_due_date, notified_amount=amount)
    return (f"Varying-amount notice {rid} sent on AutoPay {autopay_id}: {amount:.2f} USD for due date "
            f"{related_due_date}, sent {today}.")


@tool(owner="user", rw="write")
def approve_parking_returned_draft_catchup_8c80cda9(ctx: ToolContext, autopay_id: str, notice_type: str, related_due_date: str,
                                                    approved_amount: float) -> str:
    """The tenant, in person, approves a one-time catch-up draft on a vehicle, RV or boat parking AutoPay
    authorization for a rent due date whose bank-account draft came back unpaid. One call records, on that
    authorization's notice history, a new notice dated today that carries the due date the catch-up concerns
    and the exact dollar amount the tenant approves to be drafted from the bank account on file. Nothing
    else on the authorization or on the parking agreement changes. On success the tenant receives a
    confirmation reference and can see the approved amount and due date on the authorization's notice
    history.

    Args:
        autopay_id: Id class — the AutoPay authorization number of the parking authorization the catch-up
            is drafted under, as shown in the AutoPay authorization lookup.
        notice_type: Enum class — the kind of notice record written, one of: "varying_amount_notice" — the
            record states an amount to be drafted or charged for one due date, which is the kind this action
            records; "card_expiry_reminder" — a reminder that the card on file is about to expire, carrying no
            amount; "draft_failure_notice" — word that a draft for a due date failed, carrying no amount;
            "suspension_notice" — word that the authorization has been suspended, carrying no amount.
        related_due_date: Fixed-format class — the rent due date whose returned draft the catch-up
            concerns, written YYYY-MM-DD as a calendar date (no time, no time zone).
        approved_amount: Fixed-format class — the catch-up amount the tenant approves, in US dollars as a
            positive decimal number with exactly 2 decimal places (for example 123.45); the value is
            stored rounded half-to-even to the cent by Python round(x, 2).

    Returns:
        A text receipt of the form "Parking catch-up approval <reference> recorded on AutoPay <autopay_id>:
        <approved_amount> USD for due date <related_due_date>, approved <date>." where <reference> is the
        new notice reference (a string starting with apn_), <approved_amount> is the stored amount with 2
        decimals, <related_due_date> is the due date as YYYY-MM-DD and <date> is today's date as
        YYYY-MM-DD. A receipt in this form means the approval is on record.
    """
    rid = ctx.make_id("apn_", autopay_id, notice_type, related_due_date, approved_amount, "parking_catchup")
    amount = round(float(approved_amount), 2)
    today = ctx.now()[:10]
    ctx.create("autopay_notices", rid, autopay_notice_id=rid, autopay_id=autopay_id,
               customer_id=_Lookup.owner_of(ctx, autopay_id), event_type="autopay_notice",
               notice_type=notice_type, notice_date=today,
               related_due_date=related_due_date, notified_amount=amount)
    return (f"Parking catch-up approval {rid} recorded on AutoPay {autopay_id}: {amount:.2f} USD for due date "
            f"{related_due_date}, approved {today}.")


@tool(owner="agent", rw="write")
def send_parking_varying_amount_notice_109228c2(ctx: ToolContext, autopay_id: str, notice_type: str,
                                                related_due_date: str, notified_amount: float) -> str:
    """The care center sends the tenant a notice for a vehicle, RV or boat parking AutoPay authorization,
    telling the tenant the amount that will be drafted for one coming rent due date. One call records, on
    that authorization's notice history, a new notice dated today with the due date and the dollar amount
    stated to the tenant, and the notice goes to the tenant by email. Nothing else on the authorization or
    on the parking agreement changes. On success the tenant can see the notice, its date, due date and
    amount on the authorization's notice history.

    Args:
        autopay_id: Id class — the AutoPay authorization number of the parking authorization the notice is
            sent under, as shown in the AutoPay authorization lookup.
        notice_type: Enum class — the kind of notice record written, one of: "varying_amount_notice" — the
            record states an amount to be drafted or charged for one due date, which is the kind this action
            records; "card_expiry_reminder" — a reminder that the card on file is about to expire, carrying no
            amount; "draft_failure_notice" — word that a draft for a due date failed, carrying no amount;
            "suspension_notice" — word that the authorization has been suspended, carrying no amount.
        related_due_date: Fixed-format class — the rent due date whose draft the notice announces, written
            YYYY-MM-DD as a calendar date (no time, no time zone).
        notified_amount: Fixed-format class — the amount the notice tells the tenant will be drafted, in US
            dollars as a positive decimal number with exactly 2 decimal places (for example 123.45); the
            value is stored rounded half-to-even to the cent by Python round(x, 2).

    Returns:
        A text receipt of the form "Parking notice <reference> sent on AutoPay <autopay_id>: <notified_amount>
        USD for due date <related_due_date>, sent <date>." where <reference> is the new notice reference (a
        string starting with apn_), <notified_amount> is the stored amount with 2 decimals,
        <related_due_date> is the due date as YYYY-MM-DD and <date> is today's date as YYYY-MM-DD. A receipt
        in this form means the notice has been sent and recorded.
    """
    rid = ctx.make_id("apn_", autopay_id, notice_type, related_due_date, notified_amount, "parking_notice")
    amount = round(float(notified_amount), 2)
    today = ctx.now()[:10]
    ctx.create("autopay_notices", rid, autopay_notice_id=rid, autopay_id=autopay_id,
               customer_id=_Lookup.owner_of(ctx, autopay_id), event_type="autopay_notice",
               notice_type=notice_type, notice_date=today,
               related_due_date=related_due_date, notified_amount=amount)
    return (f"Parking notice {rid} sent on AutoPay {autopay_id}: {amount:.2f} USD for due date "
            f"{related_due_date}, sent {today}.")

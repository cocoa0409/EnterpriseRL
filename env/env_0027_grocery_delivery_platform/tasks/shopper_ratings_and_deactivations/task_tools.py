"""Hidden task tools for env_0027_grocery_delivery_platform / shopper_ratings_and_deactivations (category: shopper).

Each tool performs exactly one atomic business write on a shopper contractor account and takes the figure the
agent (or the shopper) has already worked out from the charter as a fixed-format argument. No tool checks a policy
precondition, computes a derived value or refuses on business grounds; those judgements belong to the caller.
The names are registered only in shopper.extended.yaml (extended_policies[].target_tool) and are reached through
unlock_* -> call_*.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def record_dropped_batch_violation_61b8c422(ctx: ToolContext, shopper_account_id: str, batch_id: str, points: int) -> str:
    """Book a dropped-batch violation on a shopper contractor account for one batch the shopper accepted and then
    dropped. One call adds one violation entry of type batch_dropped, dated today and tied to that batch, carrying the
    violation points given, and raises the account's active violation points by the same number. Afterwards the new
    violation shows on the account's list of violations with its points and the account's active points total is
    higher by that figure; the receipt below confirms the booking.

    Args:
        shopper_account_id: Id class — the shopper contractor account number the violation is booked on, as returned
            by the shopper account lookup for the verified caller.
        batch_id: Id class — the batch number of the dropped batch the violation concerns, as returned by the batch
            lookup for that shopper (the batch whose status shows it was dropped).
        points: Fixed-format class — the violation points the entry carries, a whole non-negative integer number of
            points (no decimals, no sign); the account's active points rise by exactly this integer.

    Returns:
        A dictionary rendered as text with: status ("recorded" when the booking succeeded), violation_entry_id (the
        reference number of the new violation entry, text), violation_type (always "batch_dropped"), batch_id (the
        batch number echoed back), points (the integer points booked), violation_points_balance (the account's active
        violation points after the booking, integer) and event_date (the booking date, YYYY-MM-DD).
    """
    account = ctx.find("shopper_accounts", shopper_account_id=shopper_account_id)[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("sev_", shopper_account_id, batch_id, points)
    ctx.create("shopper_events", rid, shopper_event_id=rid, shopper_account_id=shopper_account_id,
               customer_id=account.get("customer_id"), event_type="shopper_violation_recorded",
               violation_type="batch_dropped", batch_id=batch_id, order_id=None, points=int(points),
               event_date=today)
    balance = int(account.get("violation_points_balance") or 0) + int(points)
    ctx.update("shopper_accounts", shopper_account_id, violation_points_balance=balance)
    return str({"status": "recorded", "violation_entry_id": rid, "violation_type": "batch_dropped",
                "batch_id": batch_id, "points": int(points), "violation_points_balance": balance,
                "event_date": today})


@tool(owner="agent", rw="write")
def record_wrong_address_violation_db63d782(ctx: ToolContext, shopper_account_id: str, batch_id: str, points: int) -> str:
    """Book a wrong-address violation on a shopper contractor account for a batch on which an order was handed to the
    wrong address and the batch pay for it was taken back. One call adds one violation entry of type wrong_address,
    dated today and tied to that batch, carrying the violation points given, and raises the account's active
    violation points by the same number. Afterwards the violation shows on the account's list of violations with its
    points and the active points total is higher by that figure; the receipt below confirms the booking.

    Args:
        shopper_account_id: Id class — the shopper contractor account number the violation is booked on, as returned
            by the shopper account lookup for the verified caller.
        batch_id: Id class — the batch number of the batch that carried the order, as shown on the batch earnings entry
            that took the pay back (batch earnings lookup) and in the batch lookup.
        points: Fixed-format class — the violation points the entry carries, a whole non-negative integer number of
            points (no decimals, no sign); the account's active points rise by exactly this integer.

    Returns:
        A dictionary rendered as text with: status ("recorded" when the booking succeeded), violation_entry_id (the
        reference number of the new violation entry, text), violation_type (always "wrong_address"), batch_id (echoed
        back), points (the integer points booked), violation_points_balance (the account's active violation points after
        the booking, integer) and event_date (the booking date, YYYY-MM-DD).
    """
    account = ctx.find("shopper_accounts", shopper_account_id=shopper_account_id)[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("sev_", shopper_account_id, batch_id, points, "wrong_address")
    ctx.create("shopper_events", rid, shopper_event_id=rid, shopper_account_id=shopper_account_id,
               customer_id=account.get("customer_id"), event_type="shopper_violation_recorded",
               violation_type="wrong_address", order_id=None, batch_id=batch_id, points=int(points),
               event_date=today)
    balance = int(account.get("violation_points_balance") or 0) + int(points)
    ctx.update("shopper_accounts", shopper_account_id, violation_points_balance=balance)
    return str({"status": "recorded", "violation_entry_id": rid, "violation_type": "wrong_address",
                "batch_id": batch_id, "points": int(points), "violation_points_balance": balance,
                "event_date": today})


@tool(owner="agent", rw="write")
def decide_missing_items_dispute_36c35ef8(ctx: ToolContext, shopper_account_id: str, shopper_appeal_id: str,
                                          source_event_id: str, points: int) -> str:
    """Decide a shopper's submitted dispute of a missing-items violation in the shopper's favour and take the given
    number of violation points off that violation. One call books one cleared entry against the disputed violation
    with removal reason dispute_upheld and the points removed, lowers the account's active violation points by the same
    number, and marks the dispute as upheld. Afterwards the dispute shows as upheld, the violation shows a clearing of
    that many points and the account's active points total is lower by that figure; the receipt below confirms it.

    Args:
        shopper_account_id: Id class — the shopper contractor account number the dispute belongs to, as returned by
            the shopper account lookup for the verified caller.
        shopper_appeal_id: Id class — the reference number of the submitted violation dispute being decided, as
            returned by the shopper appeals lookup.
        source_event_id: Id class — the reference number of the disputed missing-items violation entry, as shown on the
            dispute and in the shopper account entries lookup.
        points: Fixed-format class — the violation points taken off the disputed violation, a whole non-negative
            integer number of points (no decimals, no sign); the account's active points fall by exactly this integer.

    Returns:
        A dictionary rendered as text with: status ("dispute_upheld" when the decision was booked), clearing_entry_id
        (the reference number of the new cleared entry, text), shopper_appeal_id and source_event_id (echoed back),
        points_removed (the integer points taken off), violation_points_balance (the account's active violation points
        after the decision, integer) and event_date (the decision date, YYYY-MM-DD).
    """
    account = ctx.find("shopper_accounts", shopper_account_id=shopper_account_id)[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("scl_", shopper_account_id, shopper_appeal_id, source_event_id, points)
    ctx.create("shopper_events", rid, shopper_event_id=rid, shopper_account_id=shopper_account_id,
               customer_id=account.get("customer_id"), event_type="shopper_violation_cleared",
               source_event_id=source_event_id, removal_reason="dispute_upheld", points=int(points),
               event_date=today)
    ctx.update("shopper_appeals", shopper_appeal_id, appeal_status="upheld")
    balance = int(account.get("violation_points_balance") or 0) - int(points)
    ctx.update("shopper_accounts", shopper_account_id, violation_points_balance=balance)
    return str({"status": "dispute_upheld", "clearing_entry_id": rid, "shopper_appeal_id": shopper_appeal_id,
                "source_event_id": source_event_id, "points_removed": int(points),
                "violation_points_balance": balance, "event_date": today})


@tool(owner="user", rw="write")
def dispute_conduct_complaint_violation_2203c191(ctx: ToolContext, shopper_account_id: str, source_event_id: str,
                                                 points: int) -> str:
    """The shopper's own in-app dispute of a conduct-complaint violation on their contractor account, settled on the spot:
    the shopper files the dispute and takes the stated number of violation points off that violation. One call files
    one violation dispute marked upheld, books one cleared entry against the violation with removal reason
    dispute_upheld and the points removed, and lowers the account's active violation points by the same number. The
    shopper then sees the dispute as upheld and the lower points total in the app; the receipt below confirms it.

    Args:
        shopper_account_id: Id class — the shopper's own contractor account number, as the agent reads it from the
            shopper account lookup and passes it to the shopper.
        source_event_id: Id class — the reference number of the conduct-complaint violation entry being disputed, as
            shown in the shopper account entries lookup and passed to the shopper by the agent.
        points: Fixed-format class — the violation points taken off the disputed violation, a whole non-negative
            integer number of points (no decimals, no sign), as the agent tells the shopper; the account's active points
            fall by exactly this integer.

    Returns:
        A dictionary rendered as text with: status ("dispute_upheld" when the dispute was filed and settled),
        shopper_appeal_id (the reference number of the new dispute, text), clearing_entry_id (the reference number of
        the new cleared entry, text), source_event_id (echoed back), points_removed (the integer points taken off),
        violation_points_balance (the account's active violation points afterwards, integer) and event_date (the date of
        the dispute, YYYY-MM-DD).
    """
    account = ctx.find("shopper_accounts", shopper_account_id=shopper_account_id)[0]
    today = ctx.now()[:10]
    appeal_id = ctx.make_id("sap_", shopper_account_id, source_event_id, points)
    ctx.create("shopper_appeals", appeal_id, shopper_appeal_id=appeal_id, customer_id=account.get("customer_id"),
               shopper_account_id=shopper_account_id, appeal_type="violation_dispute",
               source_event_id=source_event_id, appeal_status="upheld", created_at=ctx.now())
    rid = ctx.make_id("scl_", shopper_account_id, source_event_id, points)
    ctx.create("shopper_events", rid, shopper_event_id=rid, shopper_account_id=shopper_account_id,
               customer_id=account.get("customer_id"), event_type="shopper_violation_cleared",
               source_event_id=source_event_id, removal_reason="dispute_upheld", points=int(points),
               event_date=today)
    balance = int(account.get("violation_points_balance") or 0) - int(points)
    ctx.update("shopper_accounts", shopper_account_id, violation_points_balance=balance)
    return str({"status": "dispute_upheld", "shopper_appeal_id": appeal_id, "clearing_entry_id": rid,
                "source_event_id": source_event_id, "points_removed": int(points),
                "violation_points_balance": balance, "event_date": today})


@tool(owner="agent", rw="write")
def decide_wrong_address_dispute_4037a75e(ctx: ToolContext, shopper_account_id: str, shopper_appeal_id: str,
        source_event_id: str, points: int) -> str:
    """Decide a shopper's submitted dispute of a wrong-address violation in the shopper's favour and take the given
    number of violation points off that violation. One call books one cleared entry against the disputed violation
    with removal reason dispute_upheld and the points removed, lowers the account's active violation points by the same
    number, and marks the dispute as upheld. Afterwards the dispute shows as upheld, the violation shows a clearing of
    that many points and the account's active points total is lower by that figure; the receipt below confirms it.

    Args:
        shopper_account_id: Id class — the shopper contractor account number the dispute belongs to, as returned by
            the shopper account lookup for the verified caller.
        shopper_appeal_id: Id class — the reference number of the submitted violation dispute being decided, as
            returned by the shopper appeals lookup.
        source_event_id: Id class — the reference number of the disputed wrong-address violation entry, as shown on the
            dispute and in the shopper account entries lookup.
        points: Fixed-format class — the violation points taken off the disputed violation, a whole non-negative
            integer number of points (no decimals, no sign); the account's active points fall by exactly this integer.

    Returns:
        A dictionary rendered as text with: status ("dispute_upheld" when the decision was booked), clearing_entry_id
        (the reference number of the new cleared entry, text), shopper_appeal_id and source_event_id (echoed back),
        points_removed (the integer points taken off), violation_points_balance (the account's active violation points
        after the decision, integer) and event_date (the decision date, YYYY-MM-DD).
    """
    account = ctx.find("shopper_accounts", shopper_account_id=shopper_account_id)[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("scl_", shopper_account_id, shopper_appeal_id, source_event_id, points)
    ctx.create("shopper_events", rid, shopper_event_id=rid, shopper_account_id=shopper_account_id,
               customer_id=account.get("customer_id"), event_type="shopper_violation_cleared",
               source_event_id=source_event_id, removal_reason="dispute_upheld", points=int(points),
               event_date=today)
    ctx.update("shopper_appeals", shopper_appeal_id, appeal_status="upheld")
    balance = int(account.get("violation_points_balance") or 0) - int(points)
    ctx.update("shopper_accounts", shopper_account_id, violation_points_balance=balance)
    return str({"status": "dispute_upheld", "clearing_entry_id": rid, "shopper_appeal_id": shopper_appeal_id,
                "source_event_id": source_event_id, "points_removed": int(points),
                "violation_points_balance": balance, "event_date": today})


@tool(owner="agent", rw="write")
def decide_alcohol_procedure_dispute_63dedfc1(ctx: ToolContext, shopper_account_id: str, shopper_appeal_id: str,
        source_event_id: str, points: int) -> str:
    """Decide a shopper's submitted dispute of a alcohol-procedure violation in the shopper's favour and take the given
    number of violation points off that violation. One call books one cleared entry against the disputed violation
    with removal reason dispute_upheld and the points removed, lowers the account's active violation points by the same
    number, and marks the dispute as upheld. Afterwards the dispute shows as upheld, the violation shows a clearing of
    that many points and the account's active points total is lower by that figure; the receipt below confirms it.

    Args:
        shopper_account_id: Id class — the shopper contractor account number the dispute belongs to, as returned by
            the shopper account lookup for the verified caller.
        shopper_appeal_id: Id class — the reference number of the submitted violation dispute being decided, as
            returned by the shopper appeals lookup.
        source_event_id: Id class — the reference number of the disputed alcohol-procedure violation entry, as shown on the
            dispute and in the shopper account entries lookup.
        points: Fixed-format class — the violation points taken off the disputed violation, a whole non-negative
            integer number of points (no decimals, no sign); the account's active points fall by exactly this integer.

    Returns:
        A dictionary rendered as text with: status ("dispute_upheld" when the decision was booked), clearing_entry_id
        (the reference number of the new cleared entry, text), shopper_appeal_id and source_event_id (echoed back),
        points_removed (the integer points taken off), violation_points_balance (the account's active violation points
        after the decision, integer) and event_date (the decision date, YYYY-MM-DD).
    """
    account = ctx.find("shopper_accounts", shopper_account_id=shopper_account_id)[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("scl_", shopper_account_id, shopper_appeal_id, source_event_id, points)
    ctx.create("shopper_events", rid, shopper_event_id=rid, shopper_account_id=shopper_account_id,
               customer_id=account.get("customer_id"), event_type="shopper_violation_cleared",
               source_event_id=source_event_id, removal_reason="dispute_upheld", points=int(points),
               event_date=today)
    ctx.update("shopper_appeals", shopper_appeal_id, appeal_status="upheld")
    balance = int(account.get("violation_points_balance") or 0) - int(points)
    ctx.update("shopper_accounts", shopper_account_id, violation_points_balance=balance)
    return str({"status": "dispute_upheld", "clearing_entry_id": rid, "shopper_appeal_id": shopper_appeal_id,
                "source_event_id": source_event_id, "points_removed": int(points),
                "violation_points_balance": balance, "event_date": today})


@tool(owner="agent", rw="write")
def decide_late_delivery_dispute_3251c6fd(ctx: ToolContext, shopper_account_id: str, shopper_appeal_id: str,
        source_event_id: str, points: int) -> str:
    """Decide a shopper's submitted dispute of a late-delivery violation, taking the given number of violation
    points off that violation. One call books one cleared entry against the disputed violation with removal reason
    dispute_upheld and the points removed, lowers the account's active violation points by the same number, and marks
    the dispute upheld when the number is above zero or denied when it is zero. Afterwards the dispute shows its
    decision, the violation shows the clearing and the account's active points total is lower by that figure; the
    receipt below confirms it.

    Args:
        shopper_account_id: Id class — the shopper contractor account number the dispute belongs to, as returned by
            the shopper account lookup for the verified caller.
        shopper_appeal_id: Id class — the reference number of the submitted violation dispute being decided, as
            returned by the shopper appeals lookup.
        source_event_id: Id class — the reference number of the disputed late-delivery violation entry, as shown on the
            dispute and in the shopper account entries lookup.
        points: Fixed-format class — the violation points taken off the disputed violation, a whole non-negative
            integer number of points (no decimals, no sign); the account's active points fall by exactly this integer.

    Returns:
        A dictionary rendered as text with: status ("upheld" when points were removed, "denied" when the figure was zero; either means the decision was booked), clearing_entry_id
        (the reference number of the new cleared entry, text), shopper_appeal_id and source_event_id (echoed back),
        points_removed (the integer points taken off), violation_points_balance (the account's active violation points
        after the decision, integer) and event_date (the decision date, YYYY-MM-DD).
    """
    account = ctx.find("shopper_accounts", shopper_account_id=shopper_account_id)[0]
    today = ctx.now()[:10]
    rid = ctx.make_id("scl_", shopper_account_id, shopper_appeal_id, source_event_id, points)
    ctx.create("shopper_events", rid, shopper_event_id=rid, shopper_account_id=shopper_account_id,
               customer_id=account.get("customer_id"), event_type="shopper_violation_cleared",
               source_event_id=source_event_id, removal_reason="dispute_upheld", points=int(points),
               event_date=today)
    decision = "upheld" if int(points) > 0 else "denied"
    ctx.update("shopper_appeals", shopper_appeal_id, appeal_status=decision)
    balance = int(account.get("violation_points_balance") or 0) - int(points)
    ctx.update("shopper_accounts", shopper_account_id, violation_points_balance=balance)
    return str({"status": decision, "clearing_entry_id": rid, "shopper_appeal_id": shopper_appeal_id,
                "source_event_id": source_event_id, "points_removed": int(points),
                "violation_points_balance": balance, "event_date": today})


@tool(owner="user", rw="write")
def dispute_dropped_batch_violation_598e80dc(ctx: ToolContext, shopper_account_id: str, source_event_id: str,
        points: int) -> str:
    """The shopper's own in-app dispute of a dropped-batch violation on their contractor account, settled on the spot:
    the shopper files the dispute and takes the stated number of violation points off that violation. One call files
    one violation dispute marked upheld, books one cleared entry against the violation with removal reason
    dispute_upheld and the points removed, and lowers the account's active violation points by the same number. The
    shopper then sees the dispute as upheld and the lower points total in the app; the receipt below confirms it.

    Args:
        shopper_account_id: Id class — the shopper's own contractor account number, as the agent reads it from the
            shopper account lookup and passes it to the shopper.
        source_event_id: Id class — the reference number of the dropped-batch violation entry being disputed, as
            shown in the shopper account entries lookup and passed to the shopper by the agent.
        points: Fixed-format class — the violation points taken off the disputed violation, a whole non-negative
            integer number of points (no decimals, no sign), as the agent tells the shopper; the account's active points
            fall by exactly this integer.

    Returns:
        A dictionary rendered as text with: status ("dispute_upheld" when the dispute was filed and settled),
        shopper_appeal_id (the reference number of the new dispute, text), clearing_entry_id (the reference number of
        the new cleared entry, text), source_event_id (echoed back), points_removed (the integer points taken off),
        violation_points_balance (the account's active violation points afterwards, integer) and event_date (the date of
        the dispute, YYYY-MM-DD).
    """
    account = ctx.find("shopper_accounts", shopper_account_id=shopper_account_id)[0]
    today = ctx.now()[:10]
    appeal_id = ctx.make_id("sap_", shopper_account_id, source_event_id, points)
    ctx.create("shopper_appeals", appeal_id, shopper_appeal_id=appeal_id, customer_id=account.get("customer_id"),
               shopper_account_id=shopper_account_id, appeal_type="violation_dispute",
               source_event_id=source_event_id, appeal_status="upheld", created_at=ctx.now())
    rid = ctx.make_id("scl_", shopper_account_id, source_event_id, points)
    ctx.create("shopper_events", rid, shopper_event_id=rid, shopper_account_id=shopper_account_id,
               customer_id=account.get("customer_id"), event_type="shopper_violation_cleared",
               source_event_id=source_event_id, removal_reason="dispute_upheld", points=int(points),
               event_date=today)
    balance = int(account.get("violation_points_balance") or 0) - int(points)
    ctx.update("shopper_accounts", shopper_account_id, violation_points_balance=balance)
    return str({"status": "dispute_upheld", "shopper_appeal_id": appeal_id, "clearing_entry_id": rid,
                "source_event_id": source_event_id, "points_removed": int(points),
                "violation_points_balance": balance, "event_date": today})

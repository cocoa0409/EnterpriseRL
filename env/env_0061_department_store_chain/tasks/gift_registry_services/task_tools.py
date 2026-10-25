"""Hidden task tools of the gift_registry_services difficulty (Marlowe & Finch Gift Registry).

Each tool performs one atomic write on the registry category and is reached only through the
unlock/call meta-tools; every value it records is worked out by the agent beforehand.
"""

from erlbench import ToolContext, tool


@tool(owner="user", rw="write")
def redeem_completion_discount_f7189a88(ctx: ToolContext, registry_id: str, status: str, purchase_id: str, sku: str,
                                        discount_amount: float) -> str:
    """The registrant redeems the registry completion discount on her or his own order line of a registry item.
    One call records a completion purchase entry on the registry for that order line, carrying the item number and
    the completion discount taken on the unit; the registry's completion discounts used grow by that amount and the
    entry is visible afterwards among the registry's entries. A receipt with a redemption reference confirms that the
    redemption was recorded.

    Args:
        registry_id: Id class — the reference number of the gift registry record the discount is redeemed on, as
            returned by the registry lookup for the registrant.
        status: Enum class — the registry's lifecycle status exactly as the registry lookup shows it at the moment of
            redemption, one of: active (the registry is open and its completion period has not opened yet);
            completion (the registry's completion period is open); closed (the completion period has ended and the
            registry is closed); cancelled (the registrant cancelled the registry).
        purchase_id: Id class — the reference number of the registrant's purchase record (the order line) the
            discount is redeemed on, as returned by the purchase lookup.
        sku: Fixed-format class — the Marlowe & Finch item number of the order line, 8 digits, copied from the
            purchase record.
        discount_amount: Fixed-format class — the completion discount taken on the unit, stated as USD, 2 decimal places, positive (a
            positive number to 2 decimal places, already rounded half up to the cent).

    Returns:
        A dictionary rendered as text with: redemption_id (string, the reference of the completion purchase entry),
        registry_id (string, the registry redeemed on), registry_status (string, the registry status stated with the
        redemption), purchase_id (string, the order line), sku (string, 8-digit
        item number), discount_amount (number, USD to 2 decimals, the completion discount recorded), entry_date
        (string, YYYY-MM-DD, the date of the redemption) and status (string, "recorded" when the redemption
        succeeded).
    """
    rid = ctx.make_id("rcp_", registry_id, status, purchase_id, sku, discount_amount)
    owner = ctx.find("registries", registry_id=registry_id)
    customer_id = owner[0].get("customer_id") if owner else ""
    entry_date = ctx.now()[:10]
    ctx.create("registry_events", rid, registry_event_id=rid, registry_id=registry_id, customer_id=customer_id,
               event_type="registry_completion_purchase", entry_date=entry_date, sku=str(sku),
               requested_quantity="", purchase_id=purchase_id, return_id="",
               amount=round(float(discount_amount), 2), completion_discount_pct="")
    return str({"redemption_id": rid, "registry_id": registry_id, "registry_status": status,
                "purchase_id": purchase_id, "sku": str(sku),
                "discount_amount": round(float(discount_amount), 2), "entry_date": entry_date,
                "status": "recorded"})


@tool(owner="agent", rw="write")
def book_rewards_accrual_4ec6fd92(ctx: ToolContext, registry_id: str, purchase_id: str,
                                  rewards_amount: float) -> str:
    """Customer care books the registry rewards accrued on one guest gift of a gift registry. One call records a
    registry rewards accrual entry for the guest's purchase record and adds the amount to the registry's rewards
    balance, which the registrant then sees as accrued rewards not yet paid out. A receipt with the accrual
    reference and the new rewards balance confirms the booking.

    Args:
        registry_id: Id class — the reference number of the gift registry record the rewards accrue on, as returned
            by the registry lookup.
        purchase_id: Id class — the reference number of the guest's purchase record the rewards are earned on, as
            shown on the registry's guest gift entry.
        rewards_amount: Fixed-format class — the registry rewards accrued on the gift, stated as USD, 2 decimal places, positive
            (a positive number to 2 decimal places, already rounded half up to the cent).

    Returns:
        A dictionary rendered as text with: accrual_id (string, the reference of the accrual entry), registry_id
        (string), purchase_id (string), rewards_amount (number, USD to 2 decimals, the amount accrued),
        registry_rewards_balance (number, USD to 2 decimals, the registry's rewards balance after the booking),
        entry_date (string, YYYY-MM-DD) and status (string, "booked" when the accrual succeeded).
    """
    rid = ctx.make_id("rac_", registry_id, purchase_id, rewards_amount)
    reg = ctx.find("registries", registry_id=registry_id)
    customer_id = reg[0].get("customer_id") if reg else ""
    balance = round(float((reg[0].get("registry_rewards_balance") if reg else 0) or 0) + round(float(rewards_amount), 2), 2)
    entry_date = ctx.now()[:10]
    ctx.create("registry_events", rid, registry_event_id=rid, registry_id=registry_id, customer_id=customer_id,
               event_type="registry_rewards_accrual", entry_date=entry_date, sku="", requested_quantity="",
               purchase_id=purchase_id, return_id="", amount=round(float(rewards_amount), 2),
               completion_discount_pct="")
    ctx.update("registries", registry_id, registry_rewards_balance=balance)
    return str({"accrual_id": rid, "registry_id": registry_id, "purchase_id": purchase_id,
                "rewards_amount": round(float(rewards_amount), 2), "registry_rewards_balance": balance,
                "entry_date": entry_date, "status": "booked"})


@tool(owner="agent", rw="write")
def book_return_credit_c9fb6682(ctx: ToolContext, registry_id: str, return_id: str, purchase_id: str,
                                credit_amount: float) -> str:
    """Customer care books the registry credit for a registry gift the registrant returned. One call records a
    registry credit entry for the return record and the guest's purchase record of the gift and adds the amount to
    the registry's credit balance, which the registrant can then spend on Marlowe & Finch purchases. A receipt with
    the credit reference and the new registry credit balance confirms the booking.

    Args:
        registry_id: Id class — the reference number of the gift registry record the credit is booked on, as
            returned by the registry lookup.
        return_id: Id class — the reference number of the registrant's return record of the gift, as returned by the
            returns lookup.
        purchase_id: Id class — the reference number of the guest's purchase record of the returned gift, as shown on
            the return record and on the registry's guest gift entry.
        credit_amount: Fixed-format class — the registry credit booked for the returned gift, stated as USD, 2
            decimal places, positive (a positive number to 2 decimal places, already rounded half up to the cent).

    Returns:
        A dictionary rendered as text with: credit_id (string, the reference of the registry credit entry),
        registry_id (string), return_id (string), purchase_id (string), credit_amount (number, USD to 2 decimals, the
        credit booked), registry_credit_balance (number, USD to 2 decimals, the registry credit balance after the
        booking), entry_date (string, YYYY-MM-DD) and status (string, "credited" when the booking succeeded).
    """
    rid = ctx.make_id("rrc_", registry_id, return_id, purchase_id, credit_amount)
    reg = ctx.find("registries", registry_id=registry_id)
    customer_id = reg[0].get("customer_id") if reg else ""
    balance = round(float((reg[0].get("registry_credit_balance") if reg else 0) or 0) + round(float(credit_amount), 2), 2)
    entry_date = ctx.now()[:10]
    ctx.create("registry_events", rid, registry_event_id=rid, registry_id=registry_id, customer_id=customer_id,
               event_type="registry_return_credit", entry_date=entry_date, sku="", requested_quantity="",
               purchase_id=purchase_id, return_id=return_id, amount=round(float(credit_amount), 2),
               completion_discount_pct="")
    ctx.update("registries", registry_id, registry_credit_balance=balance)
    return str({"credit_id": rid, "registry_id": registry_id, "return_id": return_id, "purchase_id": purchase_id,
                "credit_amount": round(float(credit_amount), 2), "registry_credit_balance": balance,
                "entry_date": entry_date, "status": "credited"})


@tool(owner="user", rw="write")
def apply_registry_credit_10dfa5f2(ctx: ToolContext, registry_id: str, purchase_id: str, credit_amount: float) -> str:
    """The registrant applies registry credit from her or his gift registry to her or his own order line. One call
    records a registry credit use entry for that purchase record and takes the amount off the registry's credit
    balance; the registrant sees the credit applied to the order and the lower credit balance. A receipt with the
    credit use reference and the remaining registry credit balance confirms the payment.

    Args:
        registry_id: Id class — the reference number of the gift registry record whose credit is spent, as returned
            by the registry lookup.
        purchase_id: Id class — the reference number of the registrant's purchase record (the order line) the credit
            pays, as returned by the purchase lookup.
        credit_amount: Fixed-format class — the registry credit drawn from the registry for the line, stated as USD, 2
            decimal places, positive (a positive number to 2 decimal places, already rounded half up to the cent).

    Returns:
        A dictionary rendered as text with: credit_use_id (string, the reference of the credit use entry),
        registry_id (string), purchase_id (string), credit_amount (number, USD to 2 decimals, the registry credit
        drawn), registry_credit_balance (number, USD to 2 decimals, the registry credit left after the payment),
        entry_date (string, YYYY-MM-DD) and status (string, "applied" when the payment succeeded).
    """
    rid = ctx.make_id("rcu_", registry_id, purchase_id, credit_amount)
    reg = ctx.find("registries", registry_id=registry_id)
    customer_id = reg[0].get("customer_id") if reg else ""
    balance = round(float((reg[0].get("registry_credit_balance") if reg else 0) or 0) - round(float(credit_amount), 2), 2)
    entry_date = ctx.now()[:10]
    ctx.create("registry_events", rid, registry_event_id=rid, registry_id=registry_id, customer_id=customer_id,
               event_type="registry_credit_use", entry_date=entry_date, sku="", requested_quantity="",
               purchase_id=purchase_id, return_id="", amount=round(float(credit_amount), 2),
               completion_discount_pct="")
    ctx.update("registries", registry_id, registry_credit_balance=balance)
    return str({"credit_use_id": rid, "registry_id": registry_id, "purchase_id": purchase_id,
                "credit_amount": round(float(credit_amount), 2), "registry_credit_balance": balance,
                "entry_date": entry_date, "status": "applied"})

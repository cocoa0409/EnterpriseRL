"""Hidden task tools of the tool_rental_servicing difficulty (Ridgeline Tool Rental).

Each tool lands exactly one ledger line on one rental agreement and moves the agreement's
amount owed by that line; none of them checks a policy condition, aggregates history or
works out an amount — the amounts are passed in already decided.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_probuild_rental_discount_391bfaed(ctx: ToolContext, rental_agreement_id: str,
                                           discount_amount: float) -> str:
    """Post the ProBuild Rewards rental discount on one Ridgeline Tool Rental agreement. One call
    books a single discount line, dated today, against the rental time of that agreement and lowers
    the amount the renter owes on the agreement by exactly the amount posted; the renter sees the
    discount as its own line on the agreement and a lower balance. The receipt returns the new
    ledger line reference and the agreement's resulting balance.

    Args:
        rental_agreement_id: Id class — the reference number of the rental agreement (one equipment
            item) the discount is posted on, as returned by the rental agreement lookup.
        discount_amount: Fixed-format class — the discount to post in USD, 2 decimal places, as a
            positive number (for example 214.50); the value is stored by standard rounding to
            2 decimal places, with no currency sign.

    Returns:
        A dictionary rendered as text with: status ("posted" when the discount line was booked);
        rental_charge_id (the reference of the new discount line); rental_agreement_id (the agreement
        it was booked on); amount (the discount posted, USD with 2 decimal places); balance_due (the
        amount now owed on the agreement, USD with 2 decimal places, negative when the
        agreement is overpaid).
    """
    amount = round(float(discount_amount), 2)
    rows = ctx.find("rental_agreements", rental_agreement_id=rental_agreement_id)
    agreement = rows[0] if rows else {}
    rid = ctx.make_id("rdc_", rental_agreement_id, amount)
    ctx.create("rental_charges", rid, rental_charge_id=rid, rental_agreement_id=rental_agreement_id,
               customer_id=agreement.get("customer_id", ""), event_type="rental_pro_discount_applied",
               agreement_number=agreement.get("agreement_number", ""), charge_date=ctx.now()[:10],
               amount=amount, rate_period="not_applicable", periods_count=0, fee_type="not_applicable",
               payment_method="not_applicable", deposit_kind="not_applicable", deposit_method="not_applicable",
               refund_method="not_applicable", inspection_outcome="not_applicable", damage_cause="not_applicable",
               repair_cost=0.0, accessories_missing=0)
    balance = round(float(agreement.get("balance_due") or 0) - amount, 2)
    ctx.update("rental_agreements", rental_agreement_id, balance_due=balance)
    return str({"status": "posted", "rental_charge_id": rid, "rental_agreement_id": rental_agreement_id, "amount": amount, "balance_due": balance})


@tool(owner="agent", rw="write")
def bill_engine_overtime_13bb4269(ctx: ToolContext, rental_agreement_id: str,
                                  overtime_amount: float) -> str:
    """Bill the engine overtime charge on one returned Ridgeline Tool Rental agreement for metered
    equipment. One call books a single overtime fee line, dated today, on that agreement and raises
    the amount the renter owes on the agreement by exactly the amount billed; the renter sees the
    overtime charge as its own fee line and a higher balance. The receipt returns the new fee line
    reference and the agreement's resulting balance.

    Args:
        rental_agreement_id: Id class — the reference number of the rental agreement (one equipment
            item) the overtime is billed on, as returned by the rental agreement lookup.
        overtime_amount: Fixed-format class — the overtime charge in USD, 2 decimal places, as a
            positive number (for example 312.40); the value is stored by standard rounding to
            2 decimal places, with no currency sign.

    Returns:
        A dictionary rendered as text with: status ("billed" when the overtime fee line was booked);
        rental_charge_id (the reference of the new fee line); rental_agreement_id (the agreement it
        was booked on); fee_type (always "overtime_hours"); amount (the charge billed, USD with
        2 decimal places); balance_due (the amount now owed on the agreement, USD with
        2 decimal places).
    """
    amount = round(float(overtime_amount), 2)
    rows = ctx.find("rental_agreements", rental_agreement_id=rental_agreement_id)
    agreement = rows[0] if rows else {}
    rid = ctx.make_id("rot_", rental_agreement_id, amount)
    ctx.create("rental_charges", rid, rental_charge_id=rid, rental_agreement_id=rental_agreement_id,
               customer_id=agreement.get("customer_id", ""), event_type="rental_fee_charged",
               agreement_number=agreement.get("agreement_number", ""), charge_date=ctx.now()[:10],
               amount=amount, rate_period="not_applicable", periods_count=0, fee_type="overtime_hours",
               payment_method="not_applicable", deposit_kind="not_applicable", deposit_method="not_applicable",
               refund_method="not_applicable", inspection_outcome="not_applicable", damage_cause="not_applicable",
               repair_cost=0.0, accessories_missing=0)
    balance = round(float(agreement.get("balance_due") or 0) + amount, 2)
    ctx.update("rental_agreements", rental_agreement_id, balance_due=balance)
    return str({"status": "billed", "rental_charge_id": rid, "rental_agreement_id": rental_agreement_id, "fee_type": "overtime_hours", "amount": amount, "balance_due": balance})


@tool(owner="user", rw="write")
def accept_downtime_credit_2dc14db7(ctx: ToolContext, rental_agreement_id: str, rental_request_id: str,
                                    credit_amount: float) -> str:
    """The renter accepts the downtime credit offered for a breakdown of rented equipment as the remedy
    on one Ridgeline Tool Rental agreement. One call books a single malfunction credit line, dated
    today, tied to the renter's malfunction report, and lowers the amount the renter owes on the
    agreement by exactly the credit accepted; the renter sees the credit as its own line on the
    agreement and a lower balance. The receipt returns the new credit line reference and the
    agreement's resulting balance.

    Args:
        rental_agreement_id: Id class — the reference number of the rental agreement (one equipment
            item) the credit is booked on, as given to the renter by the Customer Care agent from
            the rental agreement lookup.
        rental_request_id: Id class — the reference number of the renter's malfunction report the
            credit settles, as given to the renter by the Customer Care agent from the rental
            request lookup.
        credit_amount: Fixed-format class — the credit accepted in USD, 2 decimal places, as a
            positive number (for example 640.25), exactly as the agent stated it; the value is stored
            by standard rounding to 2 decimal places, with no currency sign.

    Returns:
        A dictionary rendered as text with: status ("credited" when the credit line was booked);
        rental_charge_id (the reference of the new credit line); rental_agreement_id (the agreement it
        was booked on); rental_request_id (the malfunction report it settles); amount (the credit, USD
        with 2 decimal places); balance_due (the amount now owed on the agreement, USD
        with 2 decimal places, negative when the agreement is overpaid).
    """
    amount = round(float(credit_amount), 2)
    rows = ctx.find("rental_agreements", rental_agreement_id=rental_agreement_id)
    agreement = rows[0] if rows else {}
    rid = ctx.make_id("rmc_", rental_agreement_id, rental_request_id, amount)
    ctx.create("rental_charges", rid, rental_charge_id=rid, rental_agreement_id=rental_agreement_id,
               customer_id=agreement.get("customer_id", ""), event_type="rental_malfunction_credit_issued",
               agreement_number=agreement.get("agreement_number", ""), charge_date=ctx.now()[:10],
               amount=amount, rate_period="not_applicable", periods_count=0, fee_type="not_applicable",
               payment_method="not_applicable", deposit_kind="not_applicable", deposit_method="not_applicable",
               refund_method="not_applicable", inspection_outcome="not_applicable", damage_cause="not_applicable",
               repair_cost=0.0, accessories_missing=0, rental_request_id=rental_request_id)
    balance = round(float(agreement.get("balance_due") or 0) - amount, 2)
    ctx.update("rental_agreements", rental_agreement_id, balance_due=balance)
    return str({"status": "credited", "rental_charge_id": rid, "rental_agreement_id": rental_agreement_id, "rental_request_id": rental_request_id, "amount": amount, "balance_due": balance})


@tool(owner="agent", rw="write")
def bill_damage_deductible_c7701c46(ctx: ToolContext, rental_agreement_id: str,
                                    deductible_amount: float) -> str:
    """Bill the damage protection deductible for a damage incident on one returned Ridgeline Tool
    Rental agreement. One call books a single deductible fee line, dated today, on that agreement and
    raises the amount the renter owes on the agreement by exactly the amount billed; the renter sees
    the deductible as its own fee line and a higher balance. The receipt returns the new fee line
    reference and the agreement's resulting balance.

    Args:
        rental_agreement_id: Id class — the reference number of the rental agreement (one equipment
            item) the deductible is billed on, as returned by the rental agreement lookup.
        deductible_amount: Fixed-format class — the deductible in USD, 2 decimal places, as a
            positive number (for example 375.20); the value is stored by standard rounding to
            2 decimal places, with no currency sign.

    Returns:
        A dictionary rendered as text with: status ("billed" when the deductible line was booked);
        rental_charge_id (the reference of the new fee line); rental_agreement_id (the agreement it
        was booked on); fee_type (always "damage_deductible"); amount (the deductible billed, USD
        with 2 decimal places); balance_due (the amount now owed on the agreement, USD with
        2 decimal places).
    """
    amount = round(float(deductible_amount), 2)
    rows = ctx.find("rental_agreements", rental_agreement_id=rental_agreement_id)
    agreement = rows[0] if rows else {}
    rid = ctx.make_id("rdd_", rental_agreement_id, amount)
    ctx.create("rental_charges", rid, rental_charge_id=rid, rental_agreement_id=rental_agreement_id,
               customer_id=agreement.get("customer_id", ""), event_type="rental_fee_charged",
               agreement_number=agreement.get("agreement_number", ""), charge_date=ctx.now()[:10],
               amount=amount, rate_period="not_applicable", periods_count=0, fee_type="damage_deductible",
               payment_method="not_applicable", deposit_kind="not_applicable", deposit_method="not_applicable",
               refund_method="not_applicable", inspection_outcome="not_applicable", damage_cause="not_applicable",
               repair_cost=0.0, accessories_missing=0)
    balance = round(float(agreement.get("balance_due") or 0) + amount, 2)
    ctx.update("rental_agreements", rental_agreement_id, balance_due=balance)
    return str({"status": "billed", "rental_charge_id": rid, "rental_agreement_id": rental_agreement_id, "fee_type": "damage_deductible", "amount": amount, "balance_due": balance})


@tool(owner="agent", rw="write")
def bill_missing_accessories_12fefdd6(ctx: ToolContext, rental_agreement_id: str,
                                      accessory_amount: float) -> str:
    """Bill the charge for accessories not returned with the unit on one returned Ridgeline Tool
    Rental agreement. One call books a single missing-accessory fee line, dated today, on that
    agreement and raises the amount the renter owes on the agreement by exactly the amount billed;
    the renter sees the charge as its own fee line and a higher balance. The receipt returns the new
    fee line reference and the agreement's resulting balance.

    Args:
        rental_agreement_id: Id class — the reference number of the rental agreement (one equipment
            item) the charge is billed on, as returned by the rental agreement lookup.
        accessory_amount: Fixed-format class — the missing-accessory charge in USD, 2 decimal places,
            as a positive number (for example 45.00); the value is stored by standard rounding to
            2 decimal places, with no currency sign.

    Returns:
        A dictionary rendered as text with: status ("billed" when the fee line was booked);
        rental_charge_id (the reference of the new fee line); rental_agreement_id (the agreement it
        was booked on); fee_type (always "missing_accessory"); amount (the charge billed, USD with
        2 decimal places); balance_due (the amount now owed on the agreement, USD with
        2 decimal places).
    """
    amount = round(float(accessory_amount), 2)
    rows = ctx.find("rental_agreements", rental_agreement_id=rental_agreement_id)
    agreement = rows[0] if rows else {}
    rid = ctx.make_id("rma_", rental_agreement_id, amount)
    ctx.create("rental_charges", rid, rental_charge_id=rid, rental_agreement_id=rental_agreement_id,
               customer_id=agreement.get("customer_id", ""), event_type="rental_fee_charged",
               agreement_number=agreement.get("agreement_number", ""), charge_date=ctx.now()[:10],
               amount=amount, rate_period="not_applicable", periods_count=0, fee_type="missing_accessory",
               payment_method="not_applicable", deposit_kind="not_applicable", deposit_method="not_applicable",
               refund_method="not_applicable", inspection_outcome="not_applicable", damage_cause="not_applicable",
               repair_cost=0.0, accessories_missing=0)
    balance = round(float(agreement.get("balance_due") or 0) + amount, 2)
    ctx.update("rental_agreements", rental_agreement_id, balance_due=balance)
    return str({"status": "billed", "rental_charge_id": rid, "rental_agreement_id": rental_agreement_id, "fee_type": "missing_accessory", "amount": amount, "balance_due": balance})


@tool(owner="agent", rw="write")
def bill_refuelling_charge_2bf37336(ctx: ToolContext, rental_agreement_id: str,
                                    fuel_amount: float) -> str:
    """Bill the refuelling charge for equipment returned with less fuel than at checkout on one
    returned Ridgeline Tool Rental agreement. One call books a single refuelling fee line, dated
    today, on that agreement and raises the amount the renter owes on the agreement by exactly the
    amount billed; the renter sees the refuelling as its own fee line and a higher balance. The
    receipt returns the new fee line reference and the agreement's resulting balance.

    Args:
        rental_agreement_id: Id class — the reference number of the rental agreement (one equipment
            item) the refuelling is billed on, as returned by the rental agreement lookup.
        fuel_amount: Fixed-format class — the refuelling charge in USD, 2 decimal places, as a
            positive number (for example 96.30); the value is stored by standard rounding to
            2 decimal places, with no currency sign.

    Returns:
        A dictionary rendered as text with: status ("billed" when the fee line was booked);
        rental_charge_id (the reference of the new fee line); rental_agreement_id (the agreement it
        was booked on); fee_type (always "fuel_charge"); amount (the charge billed, USD with
        2 decimal places); balance_due (the amount now owed on the agreement, USD with
        2 decimal places).
    """
    amount = round(float(fuel_amount), 2)
    rows = ctx.find("rental_agreements", rental_agreement_id=rental_agreement_id)
    agreement = rows[0] if rows else {}
    rid = ctx.make_id("rfc_", rental_agreement_id, amount)
    ctx.create("rental_charges", rid, rental_charge_id=rid, rental_agreement_id=rental_agreement_id,
               customer_id=agreement.get("customer_id", ""), event_type="rental_fee_charged",
               agreement_number=agreement.get("agreement_number", ""), charge_date=ctx.now()[:10],
               amount=amount, rate_period="not_applicable", periods_count=0, fee_type="fuel_charge",
               payment_method="not_applicable", deposit_kind="not_applicable", deposit_method="not_applicable",
               refund_method="not_applicable", inspection_outcome="not_applicable", damage_cause="not_applicable",
               repair_cost=0.0, accessories_missing=0)
    balance = round(float(agreement.get("balance_due") or 0) + amount, 2)
    ctx.update("rental_agreements", rental_agreement_id, balance_due=balance)
    return str({"status": "billed", "rental_charge_id": rid, "rental_agreement_id": rental_agreement_id, "fee_type": "fuel_charge", "amount": amount, "balance_due": balance})


@tool(owner="user", rw="write")
def accept_damage_adjustment_c3a91d5f(ctx: ToolContext, rental_agreement_id: str, rental_request_id: str,
                                      original_charge_id: str, adjustment_amount: float) -> str:
    """The renter accepts the adjustment offered on a disputed damage repair charge as the remedy for
    their damage dispute on one Ridgeline Tool Rental agreement. One call books a single charge
    adjustment line, dated today, tied to the disputed charge and to the renter's dispute, and lowers
    the amount the renter owes on the agreement by exactly the adjustment accepted; the renter sees
    the adjustment as its own line on the agreement and a lower balance. The receipt returns the new
    adjustment line reference and the agreement's resulting balance.

    Args:
        rental_agreement_id: Id class — the reference number of the rental agreement (one equipment
            item) the adjustment is booked on, as given to the renter by the Customer Care agent from
            the rental agreement lookup.
        rental_request_id: Id class — the reference number of the renter's damage dispute the
            adjustment settles, as given to the renter by the Customer Care agent from the rental
            request lookup.
        original_charge_id: Id class — the reference number of the disputed damage repair charge line
            being adjusted, as given to the renter by the Customer Care agent from the rental charge
            lookup.
        adjustment_amount: Fixed-format class — the adjustment accepted in USD, 2 decimal places, as a
            positive number (for example 1250.00), exactly as the agent stated it; the value is stored
            by standard rounding to 2 decimal places, with no currency sign.

    Returns:
        A dictionary rendered as text with: status ("adjusted" when the adjustment line was booked);
        rental_charge_id (the reference of the new adjustment line); rental_agreement_id (the agreement
        it was booked on); original_charge_id (the disputed charge adjusted); rental_request_id (the
        dispute it settles); amount (the adjustment, USD with 2 decimal places); balance_due (the
        amount now owed on the agreement, USD with 2 decimal places, negative when
        the agreement is overpaid).
    """
    amount = round(float(adjustment_amount), 2)
    rows = ctx.find("rental_agreements", rental_agreement_id=rental_agreement_id)
    agreement = rows[0] if rows else {}
    rid = ctx.make_id("rca_", rental_agreement_id, rental_request_id, original_charge_id, amount)
    ctx.create("rental_charges", rid, rental_charge_id=rid, rental_agreement_id=rental_agreement_id,
               customer_id=agreement.get("customer_id", ""), event_type="rental_charge_adjusted",
               agreement_number=agreement.get("agreement_number", ""), charge_date=ctx.now()[:10],
               amount=amount, rate_period="not_applicable", periods_count=0, fee_type="not_applicable",
               payment_method="not_applicable", deposit_kind="not_applicable", deposit_method="not_applicable",
               refund_method="not_applicable", inspection_outcome="not_applicable", damage_cause="not_applicable",
               repair_cost=0.0, accessories_missing=0, rental_request_id=rental_request_id, original_charge_id=original_charge_id)
    balance = round(float(agreement.get("balance_due") or 0) - amount, 2)
    ctx.update("rental_agreements", rental_agreement_id, balance_due=balance)
    return str({"status": "adjusted", "rental_charge_id": rid, "rental_agreement_id": rental_agreement_id, "original_charge_id": original_charge_id, "rental_request_id": rental_request_id, "amount": amount, "balance_due": balance})

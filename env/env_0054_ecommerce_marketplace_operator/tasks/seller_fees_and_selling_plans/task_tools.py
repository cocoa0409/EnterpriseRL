"""Hidden task tools of the seller_fees_and_selling_plans difficulty (Selling Plans).

Each tool performs one atomic write on the seller's selling plan records with the values it is
given; it judges no eligibility and computes no amount.
"""

from erlbench import ToolContext, tool


class _Cal:
    """Pure-Python calendar arithmetic used to record whole-month spans."""

    @staticmethod
    def whole_months(d1: str, d2: str) -> int:
        y1, m1, a1 = (int(x) for x in str(d1)[:10].split("-"))
        y2, m2, a2 = (int(x) for x in str(d2)[:10].split("-"))
        months = (y2 - y1) * 12 + (m2 - m1)
        if a2 < a1:
            months -= 1
        return max(months, 0)

    @staticmethod
    def fee_record(ctx: ToolContext, fee_event_ref: str) -> dict:
        rows = ctx.find("selling_fees", selling_event_id=fee_event_ref)
        return rows[0] if rows else {}


@tool(owner="agent", rw="write")
def uphold_fee_dispute_credit_4fd06f6c(ctx: ToolContext, dispute_id: str, fee_event_ref: str,
                                       credit_reason: str, credit_amount: float) -> str:
    """Uphold a seller's fee dispute and book its credit. The agent marks the seller's fee dispute
    as upheld and books one seller fee credit, with the credit reason given, against the disputed
    fee record on the seller's selling plan. The credit lowers the net seller fees
    billed on the plan by the amount given; no refund administration fee is withheld from it, so
    the gross credit equals the amount booked. The seller sees the dispute shown as upheld and the
    credit listed among the plan's fee credits, dated today.

    Args:
        dispute_id: Id class — the reference number of the seller's fee dispute being upheld, as
            returned by the seller fee dispute lookup.
        fee_event_ref: Id class — the fee reference number of the disputed fee record the credit is
            booked against, as shown on the dispute and in the seller fee lookup.
        credit_reason: Enum class — why the credit is given, exactly one of: order_refund — the
            credit follows money taken back from the seller for the order, by a seller-funded refund
            or by a chargeback; order_cancellation — the credit follows an order the seller
            cancelled while it was unshipped; fee_dispute_upheld — the credit follows a seller fee
            dispute decided in the seller's favour.
        credit_amount: Fixed-format class — the credit booked on the disputed fee record, in USD,
            a positive amount to 2 decimal places (rounded to the nearest cent).

    Returns:
        A dictionary receipt: credit_id (string, the fee reference of the new credit record),
        dispute_id (string, the dispute now marked upheld), dispute_status (string, always
        "upheld"), fee_event_ref (string, the credited fee record), credit_reason (string, the reason
        recorded), credit_amount (number, USD to 2 decimal places, the credit booked) and event_date (string, YYYY-MM-DD, the booking date).
        A receipt carrying a credit_id means the credit is booked and the dispute is upheld.
    """
    fee = _Cal.fee_record(ctx, fee_event_ref)
    amount = round(float(credit_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("sfe_", dispute_id, fee_event_ref, credit_reason, amount)
    ctx.create("selling_fees", rid, selling_event_id=rid, selling_plan_id=fee.get("selling_plan_id", ""),
               customer_id=fee.get("customer_id", ""), event_type="selling_fee_credit", event_date=today,
               amount=amount, billing_period=today[:7], order_id=fee.get("order_id", ""),
               fee_event_ref=fee_event_ref, credit_reason=credit_reason, gross_credit_amount=amount,
               refund_admin_fee_amount=0.0)
    ctx.update("selling_fee_disputes", dispute_id, dispute_status="upheld")
    return str({"credit_id": rid, "dispute_id": dispute_id, "dispute_status": "upheld",
                "fee_event_ref": fee_event_ref, "credit_reason": credit_reason, "credit_amount": amount,
                "event_date": today})


@tool(owner="agent", rw="write")
def book_chargeback_fee_credit_32d8a153(ctx: ToolContext, fee_event_ref: str, credit_reason: str,
                                        gross_credit_amount: float,
                                        refund_admin_fee_amount: float, credit_amount: float) -> str:
    """Book a chargeback credit on a final value fee record. The agent books one seller fee credit,
    with the credit reason order_refund, against the variable final value fee record of an order
    whose buyer charged the payment back. The record carries the credit before any administration
    fee, the administration fee withheld and the credit actually given; the plan's net seller fees
    billed fall by the credit given. The seller sees the credit listed against that order's fee,
    dated today.

    Args:
        fee_event_ref: Id class — the fee reference number of the order's variable final value fee
            record being credited, as shown in the seller fee lookup.
        credit_reason: Enum class — why the credit is given, exactly one of: order_refund — the
            credit follows money taken back from the seller for the order, by a seller-funded refund
            or by a chargeback; order_cancellation — the credit follows an order the seller
            cancelled while it was unshipped; fee_dispute_upheld — the credit follows a seller fee
            dispute decided in the seller's favour.
        gross_credit_amount: Fixed-format class — the credit before the administration fee, in
            USD, a non-negative amount to 2 decimal places (rounded to the nearest cent).
        refund_admin_fee_amount: Fixed-format class — the administration fee withheld from the
            credit, in USD, to 2 decimal places (rounded to the nearest cent); 0.00 when none.
        credit_amount: Fixed-format class — the credit actually given to the seller, in USD, to 2
            decimal places (rounded to the nearest cent).

    Returns:
        A dictionary receipt: credit_id (string, the fee reference of the new credit record),
        fee_event_ref (string, the credited fee record), order_id (string, the order of that fee
        record), credit_reason (string, the reason recorded), gross_credit_amount,
        refund_admin_fee_amount and credit_amount (numbers, USD to 2 decimal places) and event_date
        (string, YYYY-MM-DD, the booking date). A receipt carrying a credit_id means the credit is
        booked.
    """
    fee = _Cal.fee_record(ctx, fee_event_ref)
    gross = round(float(gross_credit_amount), 2)
    admin = round(float(refund_admin_fee_amount), 2)
    amount = round(float(credit_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("sfe_", fee_event_ref, credit_reason, gross, admin, amount)
    ctx.create("selling_fees", rid, selling_event_id=rid, selling_plan_id=fee.get("selling_plan_id", ""),
               customer_id=fee.get("customer_id", ""), event_type="selling_fee_credit", event_date=today,
               amount=amount, billing_period=today[:7], order_id=fee.get("order_id", ""),
               fee_event_ref=fee_event_ref, credit_reason=credit_reason, gross_credit_amount=gross,
               refund_admin_fee_amount=admin)
    return str({"credit_id": rid, "fee_event_ref": fee_event_ref, "order_id": fee.get("order_id", ""),
                "credit_reason": credit_reason, "gross_credit_amount": gross,
                "refund_admin_fee_amount": admin, "credit_amount": amount, "event_date": today})


@tool(owner="agent", rw="write")
def book_cancellation_fee_credit_79bf63bc(ctx: ToolContext, fee_event_ref: str, credit_reason: str,
                                          gross_credit_amount: float,
                                          refund_admin_fee_amount: float, credit_amount: float) -> str:
    """Book a cancellation credit on a final value fee record. The agent books one seller fee
    credit, with the credit reason given, against the variable final value fee record of an order
    the seller cancelled while it was unshipped. The record carries the credit before
    any administration fee, the administration fee withheld and the credit actually given; the
    plan's net seller fees billed fall by the credit given. The seller sees the credit listed
    against that order's fee, dated today.

    Args:
        fee_event_ref: Id class — the fee reference number of the cancelled order's variable final
            value fee record being credited, as shown in the seller fee lookup.
        credit_reason: Enum class — why the credit is given, exactly one of: order_refund — the
            credit follows money taken back from the seller for the order, by a seller-funded refund
            or by a chargeback; order_cancellation — the credit follows an order the seller
            cancelled while it was unshipped; fee_dispute_upheld — the credit follows a seller fee
            dispute decided in the seller's favour.
        gross_credit_amount: Fixed-format class — the credit before the administration fee, in
            USD, a non-negative amount to 2 decimal places (rounded to the nearest cent).
        refund_admin_fee_amount: Fixed-format class — the administration fee withheld from the
            credit, in USD, to 2 decimal places (rounded to the nearest cent); 0.00 when none.
        credit_amount: Fixed-format class — the credit actually given to the seller, in USD, to 2
            decimal places (rounded to the nearest cent).

    Returns:
        A dictionary receipt: credit_id (string, the fee reference of the new credit record),
        fee_event_ref (string, the credited fee record), order_id (string, the order of that fee
        record), credit_reason (string, the reason recorded), gross_credit_amount,
        refund_admin_fee_amount and credit_amount (numbers, USD to 2 decimal places) and event_date
        (string, YYYY-MM-DD, the booking date). A receipt carrying a credit_id means the credit is
        booked.
    """
    fee = _Cal.fee_record(ctx, fee_event_ref)
    gross = round(float(gross_credit_amount), 2)
    admin = round(float(refund_admin_fee_amount), 2)
    amount = round(float(credit_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("sfe_", fee_event_ref, credit_reason, gross, admin, amount)
    ctx.create("selling_fees", rid, selling_event_id=rid, selling_plan_id=fee.get("selling_plan_id", ""),
               customer_id=fee.get("customer_id", ""), event_type="selling_fee_credit", event_date=today,
               amount=amount, billing_period=today[:7], order_id=fee.get("order_id", ""),
               fee_event_ref=fee_event_ref, credit_reason=credit_reason, gross_credit_amount=gross,
               refund_admin_fee_amount=admin)
    return str({"credit_id": rid, "fee_event_ref": fee_event_ref, "order_id": fee.get("order_id", ""),
                "credit_reason": credit_reason, "gross_credit_amount": gross,
                "refund_admin_fee_amount": admin, "credit_amount": amount, "event_date": today})


@tool(owner="user", rw="write")
def switch_store_to_monthly_term_ae40bf8f(ctx: ToolContext, selling_plan_id: str, term_change_fee: float) -> str:
    """Move a store from the annual billing term to the monthly billing term of the same plan. The
    seller confirms the move on their own selling plan: the plan's billing term becomes monthly,
    the monthly term is recorded as starting on the plan's next billing date (the annual term end
    date is cleared), and one term change fee is billed on the plan as an early termination fee
    record carrying the number of billing dates that were still to come in the annual term. The seller
    sees the plan on the monthly term and the fee listed among the plan's fees, dated today.

    Args:
        selling_plan_id: Id class — the reference number of the seller's own selling plan, as
            returned by the selling plan lookup.
        term_change_fee: Fixed-format class — the term change fee billed on the move, in USD, a
            non-negative amount to 2 decimal places (rounded to the nearest cent).

    Returns:
        A dictionary receipt: fee_id (string, the fee reference of the new fee record),
        selling_plan_id (string), billing_term (string, always "monthly"), term_start_date (string,
        YYYY-MM-DD, the date the monthly term starts), remaining_term_months (integer, the
        billing dates that were still to come in the annual term), term_change_fee (number, USD to 2
        decimal places) and event_date (string, YYYY-MM-DD, the billing date). A receipt carrying a
        fee_id means the move is recorded and the fee is billed.
    """
    rows = ctx.find("selling_plans", selling_plan_id=selling_plan_id)
    plan = rows[0] if rows else {}
    fee = round(float(term_change_fee), 2)
    today = ctx.now()[:10]
    start = plan.get("next_billing_date", "")
    left = _Cal.whole_months(start, plan.get("term_end_date", "")) + 1 if start and plan.get("term_end_date") else 0
    rid = ctx.make_id("sfe_", selling_plan_id, "term_change", fee)
    ctx.create("selling_fees", rid, selling_event_id=rid, selling_plan_id=selling_plan_id,
               customer_id=plan.get("customer_id", ""), event_type="selling_early_termination_fee",
               event_date=today, amount=fee, billing_period=today[:7], billing_term="annual",
               remaining_term_months=left)
    ctx.update("selling_plans", selling_plan_id, billing_term="monthly", term_start_date=start, term_end_date="")
    return str({"fee_id": rid, "selling_plan_id": selling_plan_id, "billing_term": "monthly",
                "term_start_date": start, "remaining_term_months": left, "term_change_fee": fee,
                "event_date": today})


@tool(owner="agent", rw="write")
def book_refund_fee_credit_a1b0f084(ctx: ToolContext, fee_event_ref: str, credit_reason: str,
                                    gross_credit_amount: float, refund_admin_fee_amount: float,
                                    credit_amount: float) -> str:
    """Book a refund credit on a final value fee record. The agent books one seller fee credit,
    with the credit reason given, against the variable final value fee record of an order the
    seller refunded to the buyer out of the payments balance. The record carries the credit before
    any administration fee, the administration fee withheld and the credit actually given; the
    plan's net seller fees billed fall by the credit given. The seller sees the credit listed
    against that order's fee, dated today.

    Args:
        fee_event_ref: Id class — the fee reference number of the refunded order's variable final
            value fee record being credited, as shown in the seller fee lookup.
        credit_reason: Enum class — why the credit is given, exactly one of: order_refund — the
            credit follows money taken back from the seller for the order, by a seller-funded refund
            or by a chargeback; order_cancellation — the credit follows an order the seller
            cancelled while it was unshipped; fee_dispute_upheld — the credit follows a seller fee
            dispute decided in the seller's favour.
        gross_credit_amount: Fixed-format class — the credit before the administration fee, in
            USD, a non-negative amount to 2 decimal places (rounded to the nearest cent).
        refund_admin_fee_amount: Fixed-format class — the administration fee withheld from the
            credit, in USD, to 2 decimal places (rounded to the nearest cent); 0.00 when none.
        credit_amount: Fixed-format class — the credit actually given to the seller, in USD, to 2
            decimal places (rounded to the nearest cent).

    Returns:
        A dictionary receipt: credit_id (string, the fee reference of the new credit record),
        fee_event_ref (string, the credited fee record), order_id (string, the order of that fee
        record), credit_reason (string, the reason recorded), gross_credit_amount,
        refund_admin_fee_amount and credit_amount (numbers, USD to 2 decimal places) and event_date
        (string, YYYY-MM-DD, the booking date). A receipt carrying a credit_id means the credit is
        booked.
    """
    fee = _Cal.fee_record(ctx, fee_event_ref)
    gross = round(float(gross_credit_amount), 2)
    admin = round(float(refund_admin_fee_amount), 2)
    amount = round(float(credit_amount), 2)
    today = ctx.now()[:10]
    rid = ctx.make_id("sfe_", fee_event_ref, credit_reason, "refund", gross, admin, amount)
    ctx.create("selling_fees", rid, selling_event_id=rid, selling_plan_id=fee.get("selling_plan_id", ""),
               customer_id=fee.get("customer_id", ""), event_type="selling_fee_credit", event_date=today,
               amount=amount, billing_period=today[:7], order_id=fee.get("order_id", ""),
               fee_event_ref=fee_event_ref, credit_reason=credit_reason, gross_credit_amount=gross,
               refund_admin_fee_amount=admin)
    return str({"credit_id": rid, "fee_event_ref": fee_event_ref, "order_id": fee.get("order_id", ""),
                "credit_reason": credit_reason, "gross_credit_amount": gross,
                "refund_admin_fee_amount": admin, "credit_amount": amount, "event_date": today})


@tool(owner="user", rw="write")
def end_store_term_early_0def8036(ctx: ToolContext, selling_plan_id: str, early_termination_fee: float) -> str:
    """End a store's annual term at once and close the selling plan. The seller confirms, on their
    own selling plan, that the annual term ends today: the plan is closed with today's date as its
    closing date, and one early termination fee is billed on the plan, recorded with the number of
    billing dates that were still to come in the term. The seller sees the plan shown as closed and
    the fee listed among the plan's fees, dated today.

    Args:
        selling_plan_id: Id class — the reference number of the seller's own selling plan, as
            returned by the selling plan lookup.
        early_termination_fee: Fixed-format class — the early termination fee billed, in USD, a
            non-negative amount to 2 decimal places (rounded to the nearest cent).

    Returns:
        A dictionary receipt: fee_id (string, the fee reference of the new fee record),
        selling_plan_id (string), status (string, always "closed"), closed_date (string,
        YYYY-MM-DD), remaining_term_months (integer, the billing dates that were still to come
        in the term), early_termination_fee (number, USD to 2 decimal places) and event_date (string,
        YYYY-MM-DD, the billing date). A receipt carrying a fee_id means the term is ended, the plan
        is closed and the fee is billed.
    """
    rows = ctx.find("selling_plans", selling_plan_id=selling_plan_id)
    plan = rows[0] if rows else {}
    fee = round(float(early_termination_fee), 2)
    today = ctx.now()[:10]
    start = plan.get("next_billing_date", "")
    left = _Cal.whole_months(start, plan.get("term_end_date", "")) + 1 if start and plan.get("term_end_date") else 0
    rid = ctx.make_id("sfe_", selling_plan_id, "early_termination", fee)
    ctx.create("selling_fees", rid, selling_event_id=rid, selling_plan_id=selling_plan_id,
               customer_id=plan.get("customer_id", ""), event_type="selling_early_termination_fee",
               event_date=today, amount=fee, billing_period=today[:7], billing_term="annual",
               remaining_term_months=left)
    ctx.update("selling_plans", selling_plan_id, status="closed", closed_date=today)
    return str({"fee_id": rid, "selling_plan_id": selling_plan_id, "status": "closed", "closed_date": today,
                "remaining_term_months": left, "early_termination_fee": fee, "event_date": today})

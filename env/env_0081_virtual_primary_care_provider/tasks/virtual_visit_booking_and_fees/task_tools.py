"""Hidden task tools for the virtual_visit_booking_and_fees difficulty (Larkspur Health virtual visits).

Each tool performs one atomic write on one visit appointment's billing records. Tools never judge
eligibility, prerequisites or amounts: the caller works the amount out from the published rules and
passes it in.
"""
from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _Money:
    """Exact money handling shared by the tools."""

    @staticmethod
    def cents(value) -> float:
        """Round a dollar amount half up to the cent with exact decimal arithmetic."""
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def is_cent_exact(value) -> bool:
        """True when the amount already carries no more than two decimal places."""
        d = Decimal(str(value))
        return d == d.quantize(Decimal("0.01"))


@tool(owner="agent", rw="write")
def issue_good_faith_estimate_d8f09896(ctx: ToolContext, visit_id: str, estimate_amount: float) -> str:
    """Deliver a Good Faith Estimate of the expected self-pay charges for one scheduled virtual visit,
    prepared for the start time the visit currently holds. On success a new estimate record is stored
    against the visit, dated today and carrying the visit's current scheduled start, and it becomes the
    latest estimate the patient can see for that visit; the visit itself and its billing lines are not
    changed.

    Args:
        visit_id: Id class — the reference number of the visit appointment the estimate covers, as
            returned by the visit appointment lookup for the verified patient.
        estimate_amount: Fixed-format class — the total expected self-pay charges stated on the
            estimate, USD, 2 decimal places, a positive amount rounded half up to the cent before
            it is passed in.

    Returns:
        A confirmation sentence naming the new estimate reference (a text identifier beginning with
        "gfe_"), the visit reference, the scheduled start it was prepared for (YYYY-MM-DD HH:MM, US
        Eastern Time) and the estimate amount in dollars with two decimals; receiving this sentence
        means the estimate was issued. If the visit reference is unknown, a sentence beginning
        "Error:" is returned and nothing is stored.
    """
    rows = ctx.find("visit_appointments", visit_id=visit_id)
    if not rows:
        return f"Error: no visit appointment {visit_id}."
    if float(estimate_amount) <= 0 or not _Money.is_cent_exact(estimate_amount):
        return "Error: estimate_amount must be a positive dollar amount with two decimal places."
    visit = rows[0]
    amount = _Money.cents(estimate_amount)
    rid = ctx.make_id("gfe_", visit_id, amount)
    ctx.create("visit_estimates", rid, gfe_id=rid, visit_id=visit_id, customer_id=visit["customer_id"],
               event_type="visit_gfe_issued", estimate_amount=amount, issued_date=ctx.now()[:10],
               scheduled_start=visit["scheduled_start"])
    return (f"Good Faith Estimate {rid} issued for visit {visit_id} (scheduled start "
            f"{visit['scheduled_start']}): {amount:.2f} USD.")

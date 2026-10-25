"""Task tools for difficulty account_credit_and_recovery (env_0076, Harborline Hosting & Domains).

Hidden atomic writes on the customer's Harborline account credit. Each tool lands exactly one credit entry and
keeps the account's credit balance equal to the sum of its credit entries, as the account charter requires for
every credit entry. Money is handled to the cent with half-up rounding.
"""

from decimal import Decimal, ROUND_HALF_UP

from erlbench import ToolContext, tool


class _Cents:
    """Pure-Python money and reference helpers (half-up to the cent; reference formats)."""

    @staticmethod
    def half_up(x) -> float:
        return float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def is_order_number(ref) -> bool:
        ref = str(ref or "")
        return len(ref) == 11 and ref.startswith("HL-") and ref[3:].isdigit()

    @staticmethod
    def is_reference(ref) -> bool:
        ref = str(ref or "")
        return bool(ref) and ref == ref.strip() and " " not in ref


@tool(owner="user", rw="write")
def make_prefund_deposit_8453f2b2(ctx: ToolContext, account_id: str, funding_method: str, amount: float) -> str:
    """The account holder pays money into their own Harborline account credit from one of their own payment methods,
    ahead of auto-renew charges. One call records one deposit: the payment is taken from the holder's card, PayPal
    account or bank transfer, the account credit balance goes up by the amount deposited, and the deposit is recorded
    on the account's credit history with its funding method. The holder can see the deposit and the higher balance on
    the account at once, and the credit is available for any Harborline charge, including auto-renewals that try
    account credit.

    Args:
        account_id: Id class — the reference number of the holder's Harborline account, as shown on the account
            record the agent opened for this customer.
        funding_method: Enum class — how the holder pays the deposit: card — the deposit is charged to the holder's
            payment card; paypal — the deposit is paid from the holder's PayPal account; bank_transfer — the deposit
            arrives by the holder's bank transfer; none — not a funding method for a deposit and never the right value
            for this call.
        amount: Fixed-format class — the amount deposited, in USD, 2 decimal places, a positive figure; any further
            decimals are rounded half up to the cent.

    Returns:
        A confirmation line stating the reference number of the new deposit entry (a text reference), the amount
        deposited in US dollars with two decimals, the funding method used and the account's new credit balance in US
        dollars with two decimals; a line beginning "Deposit recorded" means the call completed.
    """
    amt = _Cents.half_up(amount)
    if amt <= 0:
        return "Error: amount must be a positive US dollar figure."
    if funding_method not in ("card", "paypal", "bank_transfer"):
        return "Error: funding_method must be card, paypal or bank_transfer."
    acc = (ctx.find("account_holdings", account_id=account_id) or [{}])[0]
    rid = ctx.make_id("acp_", account_id, funding_method, amt)
    ctx.create("account_credit_ledger", rid, credit_entry_id=rid, account_id=account_id,
               customer_id=acc.get("customer_id"), event_type="account_credit_deposit", amount=amt,
               entry_date=ctx.now()[:10], credit_origin="deposit", funding_method=funding_method,
               source_category="none", source_charge_ref="", original_credit_entry_id=None)
    new_bal = _Cents.half_up(float(acc.get("credit_balance") or 0) + amt)
    ctx.update("account_holdings", account_id, credit_balance=new_bal)
    return (f"Deposit recorded: entry {rid}, {amt:.2f} USD by {funding_method}; "
            f"new credit balance {new_bal:.2f} USD.")


@tool(owner="agent", rw="write")
def grant_provisioning_goodwill_e1bd747b(ctx: ToolContext, account_id: str, source_charge_ref: str, amount: float) -> str:
    """Credits goodwill to a customer's Harborline account credit for a hosting plan that Harborline provisioned late. One call records one goodwill credit
    against the order number of the plan's initial-term charge, with hosting as the affected product: the account credit balance goes up by the goodwill amount and the goodwill
    appears on the account's credit history at once, spendable on any Harborline product and never withdrawable.

    Args:
        account_id: Id class — the reference number of the customer's Harborline account, as shown on the account
            record the agent opened for this customer.
        source_charge_ref: Fixed-format class — the reference number exactly as shown on the product charge or
            holding, or empty string: here the order number of the hosting plan's initial-term charge, HL- followed by
            8 digits, as shown on the hosting billing history; the empty string is not used.
        amount: Fixed-format class — the goodwill credited, in USD, 2 decimal places, a positive figure; any further
            decimals are rounded half up to the cent.

    Returns:
        A confirmation line stating the reference number of the new goodwill entry (a text reference), the amount
        credited in US dollars with two decimals, the reference it was posted against and the account's new credit
        balance in US dollars with two decimals; a line beginning "Goodwill credited" means the call completed.
    """
    amt = _Cents.half_up(amount)
    if amt <= 0:
        return "Error: amount must be a positive US dollar figure."
    if not _Cents.is_order_number(source_charge_ref):
        return "Error: source_charge_ref must be an order number, HL- followed by 8 digits."
    acc = (ctx.find("account_holdings", account_id=account_id) or [{}])[0]
    rid = ctx.make_id("agw_", account_id, source_charge_ref, amt)
    ctx.create("account_credit_ledger", rid, credit_entry_id=rid, account_id=account_id,
               customer_id=acc.get("customer_id"), event_type="account_goodwill_credit", amount=amt,
               entry_date=ctx.now()[:10], credit_origin="goodwill", funding_method="none",
               source_category="hosting", source_charge_ref=source_charge_ref, original_credit_entry_id=None)
    new_bal = _Cents.half_up(float(acc.get("credit_balance") or 0) + amt)
    ctx.update("account_holdings", account_id, credit_balance=new_bal)
    return (f"Goodwill credited: entry {rid}, {amt:.2f} USD against {source_charge_ref}; "
            f"new credit balance {new_bal:.2f} USD.")


@tool(owner="agent", rw="write")
def grant_recovery_delay_goodwill_1cc515a4(ctx: ToolContext, account_id: str, source_charge_ref: str, amount: float) -> str:
    """Credits goodwill to a customer's Harborline account credit for an account recovery request that Trust and Safety decided late. One call records one goodwill credit
    against the recovery request's reference number, with no product category: the account credit balance goes up by the goodwill amount and the goodwill
    appears on the account's credit history at once, spendable on any Harborline product and never withdrawable.

    Args:
        account_id: Id class — the reference number of the customer's Harborline account, as shown on the account
            record the agent opened for this customer.
        source_charge_ref: Fixed-format class — the reference number exactly as shown on the product charge or
            holding, or empty string: here the reference number of the recovery request, character for character, as
            shown on the account's recovery request record; the empty string is not used.
        amount: Fixed-format class — the goodwill credited, in USD, 2 decimal places, a positive figure; any further
            decimals are rounded half up to the cent.

    Returns:
        A confirmation line stating the reference number of the new goodwill entry (a text reference), the amount
        credited in US dollars with two decimals, the reference it was posted against and the account's new credit
        balance in US dollars with two decimals; a line beginning "Goodwill credited" means the call completed.
    """
    amt = _Cents.half_up(amount)
    if amt <= 0:
        return "Error: amount must be a positive US dollar figure."
    if not _Cents.is_reference(source_charge_ref):
        return "Error: source_charge_ref must be the recovery request reference, unchanged."
    acc = (ctx.find("account_holdings", account_id=account_id) or [{}])[0]
    rid = ctx.make_id("agr_", account_id, source_charge_ref, amt)
    ctx.create("account_credit_ledger", rid, credit_entry_id=rid, account_id=account_id,
               customer_id=acc.get("customer_id"), event_type="account_goodwill_credit", amount=amt,
               entry_date=ctx.now()[:10], credit_origin="goodwill", funding_method="none",
               source_category="none", source_charge_ref=source_charge_ref, original_credit_entry_id=None)
    new_bal = _Cents.half_up(float(acc.get("credit_balance") or 0) + amt)
    ctx.update("account_holdings", account_id, credit_balance=new_bal)
    return (f"Goodwill credited: entry {rid}, {amt:.2f} USD against {source_charge_ref}; "
            f"new credit balance {new_bal:.2f} USD.")


@tool(owner="agent", rw="write")
def grant_duplicate_charge_goodwill_d451e88f(ctx: ToolContext, account_id: str, source_charge_ref: str, amount: float) -> str:
    """Credits goodwill to a customer's Harborline account credit for a domain auto-renew charge that Harborline billed twice on the same day. One call records one goodwill credit
    against the order number of the duplicate charge, with domain as the affected product: the account credit balance goes up by the goodwill amount and the goodwill
    appears on the account's credit history at once, spendable on any Harborline product and never withdrawable.

    Args:
        account_id: Id class — the reference number of the customer's Harborline account, as shown on the account
            record the agent opened for this customer.
        source_charge_ref: Fixed-format class — the reference number exactly as shown on the product charge or
            holding, or empty string: here the order number of the duplicate domain auto-renew charge, HL- followed by
            8 digits, as shown on the domain billing history; the empty string is not used.
        amount: Fixed-format class — the goodwill credited, in USD, 2 decimal places, a positive figure; any further
            decimals are rounded half up to the cent.

    Returns:
        A confirmation line stating the reference number of the new goodwill entry (a text reference), the amount
        credited in US dollars with two decimals, the reference it was posted against and the account's new credit
        balance in US dollars with two decimals; a line beginning "Goodwill credited" means the call completed.
    """
    amt = _Cents.half_up(amount)
    if amt <= 0:
        return "Error: amount must be a positive US dollar figure."
    if not _Cents.is_order_number(source_charge_ref):
        return "Error: source_charge_ref must be an order number, HL- followed by 8 digits."
    acc = (ctx.find("account_holdings", account_id=account_id) or [{}])[0]
    rid = ctx.make_id("agd_", account_id, source_charge_ref, amt)
    ctx.create("account_credit_ledger", rid, credit_entry_id=rid, account_id=account_id,
               customer_id=acc.get("customer_id"), event_type="account_goodwill_credit", amount=amt,
               entry_date=ctx.now()[:10], credit_origin="goodwill", funding_method="none",
               source_category="domain", source_charge_ref=source_charge_ref, original_credit_entry_id=None)
    new_bal = _Cents.half_up(float(acc.get("credit_balance") or 0) + amt)
    ctx.update("account_holdings", account_id, credit_balance=new_bal)
    return (f"Goodwill credited: entry {rid}, {amt:.2f} USD against {source_charge_ref}; "
            f"new credit balance {new_bal:.2f} USD.")


@tool(owner="user", rw="write")
def make_topup_deposit_c7a3772f(ctx: ToolContext, account_id: str, funding_method: str, amount: float) -> str:
    """The account holder pays money into their own Harborline account credit from one of their own payment methods.
    One call records one deposit: the payment is taken from the holder's card, PayPal account or bank transfer, the
    account credit balance goes up by the amount deposited, and the deposit is recorded on the account's credit history
    with its funding method. The holder can see the deposit and the higher balance on the account at once, and the
    credit is available for any Harborline charge, including auto-renewals that try account credit.

    Args:
        account_id: Id class — the reference number of the holder's Harborline account, as shown on the account
            record the agent opened for this customer.
        funding_method: Enum class — how the holder pays the deposit: card — the deposit is charged to the holder's
            payment card; paypal — the deposit is paid from the holder's PayPal account; bank_transfer — the deposit
            arrives by the holder's bank transfer; none — not a funding method for a deposit and never the right value
            for this call.
        amount: Fixed-format class — the amount deposited, in USD, 2 decimal places, a positive figure; any further
            decimals are rounded half up to the cent.

    Returns:
        A confirmation line stating the reference number of the new deposit entry (a text reference), the amount
        deposited in US dollars with two decimals, the funding method used and the account's new credit balance in US
        dollars with two decimals; a line beginning "Deposit recorded" means the call completed.
    """
    amt = _Cents.half_up(amount)
    if amt <= 0:
        return "Error: amount must be a positive US dollar figure."
    if funding_method not in ("card", "paypal", "bank_transfer"):
        return "Error: funding_method must be card, paypal or bank_transfer."
    acc = (ctx.find("account_holdings", account_id=account_id) or [{}])[0]
    rid = ctx.make_id("acd_", account_id, funding_method, amt)
    ctx.create("account_credit_ledger", rid, credit_entry_id=rid, account_id=account_id,
               customer_id=acc.get("customer_id"), event_type="account_credit_deposit", amount=amt,
               entry_date=ctx.now()[:10], credit_origin="deposit", funding_method=funding_method,
               source_category="none", source_charge_ref="", original_credit_entry_id=None)
    new_bal = _Cents.half_up(float(acc.get("credit_balance") or 0) + amt)
    ctx.update("account_holdings", account_id, credit_balance=new_bal)
    return (f"Deposit recorded: entry {rid}, {amt:.2f} USD by {funding_method}; "
            f"new credit balance {new_bal:.2f} USD.")


@tool(owner="agent", rw="write")
def grant_certificate_delay_goodwill_7e1fd2ff(ctx: ToolContext, account_id: str, source_charge_ref: str, amount: float) -> str:
    """Credits goodwill to a customer's Harborline account credit for a certificate subscription whose certificate Harborline issued late. One call records one goodwill credit
    against the order number of the subscription's new-subscription charge, with ssl as the affected product: the account credit balance goes up by the goodwill amount and the goodwill
    appears on the account's credit history at once, spendable on any Harborline product and never withdrawable.

    Args:
        account_id: Id class — the reference number of the customer's Harborline account, as shown on the account
            record the agent opened for this customer.
        source_charge_ref: Fixed-format class — the reference number exactly as shown on the product charge or
            holding, or empty string: here the order number of the certificate subscription's new-subscription charge,
            HL- followed by 8 digits, as shown on the certificate billing history; the empty string is not used.
        amount: Fixed-format class — the goodwill credited, in USD, 2 decimal places, a positive figure; any further
            decimals are rounded half up to the cent.

    Returns:
        A confirmation line stating the reference number of the new goodwill entry (a text reference), the amount
        credited in US dollars with two decimals, the reference it was posted against and the account's new credit
        balance in US dollars with two decimals; a line beginning "Goodwill credited" means the call completed.
    """
    amt = _Cents.half_up(amount)
    if amt <= 0:
        return "Error: amount must be a positive US dollar figure."
    if not _Cents.is_order_number(source_charge_ref):
        return "Error: source_charge_ref must be an order number, HL- followed by 8 digits."
    acc = (ctx.find("account_holdings", account_id=account_id) or [{}])[0]
    rid = ctx.make_id("agc_", account_id, source_charge_ref, amt)
    ctx.create("account_credit_ledger", rid, credit_entry_id=rid, account_id=account_id,
               customer_id=acc.get("customer_id"), event_type="account_goodwill_credit", amount=amt,
               entry_date=ctx.now()[:10], credit_origin="goodwill", funding_method="none",
               source_category="ssl", source_charge_ref=source_charge_ref, original_credit_entry_id=None)
    new_bal = _Cents.half_up(float(acc.get("credit_balance") or 0) + amt)
    ctx.update("account_holdings", account_id, credit_balance=new_bal)
    return (f"Goodwill credited: entry {rid}, {amt:.2f} USD against {source_charge_ref}; "
            f"new credit balance {new_bal:.2f} USD.")


@tool(owner="agent", rw="write")
def grant_reset_delay_goodwill_979fb2c3(ctx: ToolContext, account_id: str, source_charge_ref: str, amount: float) -> str:
    """Credits goodwill to a customer's Harborline account credit for an approved account recovery whose reset Harborline applied late. One call records one goodwill credit
    against the reference of the account's security-change notice that applied the reset, with no product category: the account credit balance goes up by the goodwill amount and the goodwill
    appears on the account's credit history at once, spendable on any Harborline product and never withdrawable.

    Args:
        account_id: Id class — the reference number of the customer's Harborline account, as shown on the account
            record the agent opened for this customer.
        source_charge_ref: Fixed-format class — the reference number exactly as shown on the product charge or
            holding, or empty string: here the reference of the security-change notice, character for character, as shown
            on the account's history; the empty string is not used.
        amount: Fixed-format class — the goodwill credited, in USD, 2 decimal places, a positive figure; any further
            decimals are rounded half up to the cent.

    Returns:
        A confirmation line stating the reference number of the new goodwill entry (a text reference), the amount
        credited in US dollars with two decimals, the reference it was posted against and the account's new credit
        balance in US dollars with two decimals; a line beginning "Goodwill credited" means the call completed.
    """
    amt = _Cents.half_up(amount)
    if amt <= 0:
        return "Error: amount must be a positive US dollar figure."
    if not _Cents.is_reference(source_charge_ref):
        return "Error: source_charge_ref must be the security-change notice reference, unchanged."
    acc = (ctx.find("account_holdings", account_id=account_id) or [{}])[0]
    rid = ctx.make_id("agt_", account_id, source_charge_ref, amt)
    ctx.create("account_credit_ledger", rid, credit_entry_id=rid, account_id=account_id,
               customer_id=acc.get("customer_id"), event_type="account_goodwill_credit", amount=amt,
               entry_date=ctx.now()[:10], credit_origin="goodwill", funding_method="none",
               source_category="none", source_charge_ref=source_charge_ref, original_credit_entry_id=None)
    new_bal = _Cents.half_up(float(acc.get("credit_balance") or 0) + amt)
    ctx.update("account_holdings", account_id, credit_balance=new_bal)
    return (f"Goodwill credited: entry {rid}, {amt:.2f} USD against {source_charge_ref}; "
            f"new credit balance {new_bal:.2f} USD.")


@tool(owner="agent", rw="write")
def grant_refund_posting_goodwill_cac8bb9c(ctx: ToolContext, account_id: str, source_charge_ref: str, amount: float) -> str:
    """Credits goodwill to a customer's Harborline account credit for a domain refund that Harborline posted to the account credit late. One call records one goodwill credit
    against the reference of the domain refund line, with domain as the affected product: the account credit balance goes up by the goodwill amount and the goodwill
    appears on the account's credit history at once, spendable on any Harborline product and never withdrawable.

    Args:
        account_id: Id class — the reference number of the customer's Harborline account, as shown on the account
            record the agent opened for this customer.
        source_charge_ref: Fixed-format class — the reference number exactly as shown on the product charge or
            holding, or empty string: here the reference of the domain refund line, character for character, as shown on
            the domain billing history; the empty string is not used.
        amount: Fixed-format class — the goodwill credited, in USD, 2 decimal places, a positive figure; any further
            decimals are rounded half up to the cent.

    Returns:
        A confirmation line stating the reference number of the new goodwill entry (a text reference), the amount
        credited in US dollars with two decimals, the reference it was posted against and the account's new credit
        balance in US dollars with two decimals; a line beginning "Goodwill credited" means the call completed.
    """
    amt = _Cents.half_up(amount)
    if amt <= 0:
        return "Error: amount must be a positive US dollar figure."
    if not _Cents.is_reference(source_charge_ref):
        return "Error: source_charge_ref must be the refund line reference, unchanged."
    acc = (ctx.find("account_holdings", account_id=account_id) or [{}])[0]
    rid = ctx.make_id("agp_", account_id, source_charge_ref, amt)
    ctx.create("account_credit_ledger", rid, credit_entry_id=rid, account_id=account_id,
               customer_id=acc.get("customer_id"), event_type="account_goodwill_credit", amount=amt,
               entry_date=ctx.now()[:10], credit_origin="goodwill", funding_method="none",
               source_category="domain", source_charge_ref=source_charge_ref, original_credit_entry_id=None)
    new_bal = _Cents.half_up(float(acc.get("credit_balance") or 0) + amt)
    ctx.update("account_holdings", account_id, credit_balance=new_bal)
    return (f"Goodwill credited: entry {rid}, {amt:.2f} USD against {source_charge_ref}; "
            f"new credit balance {new_bal:.2f} USD.")

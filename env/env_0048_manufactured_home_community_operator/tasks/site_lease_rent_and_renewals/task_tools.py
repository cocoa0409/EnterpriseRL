"""Hidden task tools for the site_lease_rent_and_renewals difficulty (Home-Site Lease).

Each tool performs one atomic write on a resident's home-site lease records with the values the
resident desk has already worked out; none of them checks eligibility, prerequisites or amounts.
They are reached only through the unlock/call meta tools, by the names the lease charter gives.
"""

from erlbench import ToolContext, tool


class _CalendarDays:
    """Pure calendar arithmetic on 'YYYY-MM-DD' strings (no clock, no library)."""

    @staticmethod
    def to_ordinal(day: str) -> int:
        y, m, d = (int(p) for p in str(day)[:10].split("-"))
        y -= 1 if m <= 2 else 0
        era = (y if y >= 0 else y - 399) // 400
        yoe = y - era * 400
        doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe

    @staticmethod
    def from_ordinal(n: int) -> str:
        era = (n if n >= 0 else n - 146096) // 146097
        doe = n - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        y = yoe + era * 400
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        d = doy - (153 * mp + 2) // 5 + 1
        m = mp + (3 if mp < 10 else -9)
        y += 1 if m <= 2 else 0
        return f"{y:04d}-{m:02d}-{d:02d}"

    @staticmethod
    def shift(day: str, days: int) -> str:
        return _CalendarDays.from_ordinal(_CalendarDays.to_ordinal(day) + int(days))


@tool(owner="agent", rw="write")
def issue_renewal_offer_ab5c4495(ctx: ToolContext, lease_id: str, offered_term_type: str, effective_date: str,
                                 response_deadline: str, new_monthly_site_rent: float) -> str:
    """Issue a written renewal offer for one term on a resident's fixed-term home-site lease, dated today.

    The resident desk records one offered renewal term: its term type, the first day of that term,
    the last day on which the resident may sign it, and the monthly site rent offered for it.
    Nothing is charged and the lease itself is not changed; afterwards the offered term, its rent
    and its deadline appear among the notices on the lease. Success is a receipt with the offer's
    reference number.

    Args:
        lease_id: Id class — the lease reference number of the home-site lease being offered renewal, as returned by the lease lookup for this resident.
        offered_term_type: Enum class — the term offered: twelve_month when offering a fixed twelve-month term; twenty_four_month when offering a fixed twenty-four-month term; month_to_month when offering a month-to-month term with no end date.
        effective_date: Fixed-format class — first day of the offered term (the day after the current term end date), written YYYY-MM-DD.
        response_deadline: Fixed-format class — last day on which the resident may sign the offered renewal, written YYYY-MM-DD.
        new_monthly_site_rent: Fixed-format class — monthly site rent offered for that term, in USD, 2 decimal places (cents), already rounded half up to the cent.

    Returns:
        A dict with: status ("issued" when the offered term is recorded); offer_id (reference number
        of the offered term); lease_id; notice_date (today, YYYY-MM-DD); offered_term_type;
        effective_date and response_deadline (YYYY-MM-DD); new_monthly_site_rent (USD, 2 decimal
        places).
    """
    holding = ctx.find("lease_holdings", lease_id=lease_id)
    customer_id = holding[0].get("customer_id") if holding else ""
    today = ctx.now()[:10]
    rent = round(float(new_monthly_site_rent), 2)
    rid = ctx.make_id("lno_", lease_id, offered_term_type, effective_date, response_deadline, rent)
    ctx.create("lease_notices", rid, lease_notice_id=rid, lease_id=lease_id, customer_id=customer_id,
               event_type="lease_renewal_offer", notice_date=today, effective_date=effective_date,
               response_deadline=response_deadline, offered_term_type=offered_term_type,
               new_monthly_site_rent=rent)
    return str({"status": "issued", "offer_id": rid, "lease_id": lease_id, "notice_date": today,
                "offered_term_type": offered_term_type, "effective_date": effective_date,
                "response_deadline": response_deadline, "new_monthly_site_rent": rent})


@tool(owner="user", rw="write")
def sign_lease_renewal_1699e1a4(ctx: ToolContext, lease_id: str, requested_term_type: str, term_start_date: str,
                                term_end_date: str, new_monthly_site_rent: float) -> str:
    """The resident signs a renewal of their own home-site lease for a new term.

    Signing records the resident's renewal election as accepted and writes the signed term onto
    the lease: the term type, the first and last day of the new term and the monthly site rent of
    that term. No payment is taken. Afterwards the lease shows the new term and rent, and the
    accepted renewal election appears among the resident's lease requests. Success is a receipt
    with the election reference and the signed rent.

    Args:
        lease_id: Id class — the lease reference number of the resident's own home-site lease, as the resident desk read it out from the lease lookup.
        requested_term_type: Enum class — the term the resident signs: twelve_month when signing a fixed twelve-month term; twenty_four_month when signing a fixed twenty-four-month term; month_to_month when choosing a month-to-month term with no end date; not_applicable is never used for a renewal signature.
        term_start_date: Fixed-format class — first day of the signed term, written YYYY-MM-DD.
        term_end_date: Fixed-format class — last day of the signed fixed term, written YYYY-MM-DD; an empty string for a month-to-month term.
        new_monthly_site_rent: Fixed-format class — monthly site rent of the signed term, in USD, 2 decimal places (cents), already rounded half up to the cent.

    Returns:
        A dict with: status ("signed" when the election is recorded and the lease updated);
        request_id (reference number of the accepted renewal election); lease_id; term_type (the
        signed term); term_start_date and term_end_date (YYYY-MM-DD, end empty for month to month);
        monthly_site_rent (USD, 2 decimal places).
    """
    holding = ctx.find("lease_holdings", lease_id=lease_id)
    customer_id = holding[0].get("customer_id") if holding else ""
    rent = round(float(new_monthly_site_rent), 2)
    rid = ctx.make_id("lrq_", lease_id, requested_term_type, term_start_date, term_end_date, rent)
    ctx.create("lease_requests", rid, lease_request_id=rid, customer_id=customer_id, lease_id=lease_id,
               request_type="renewal_election", requested_term_type=requested_term_type,
               requested_date=term_start_date, request_status="accepted", created_at=ctx.now())
    ctx.update("lease_holdings", lease_id, lease_term_type=requested_term_type, term_start_date=term_start_date,
               term_end_date=term_end_date, monthly_site_rent=rent)
    return str({"status": "signed", "request_id": rid, "lease_id": lease_id, "term_type": requested_term_type,
                "term_start_date": term_start_date, "term_end_date": term_end_date, "monthly_site_rent": rent})


@tool(owner="agent", rw="write")
def post_late_fee_cfe97caa(ctx: ToolContext, lease_id: str, billing_period: str, source_entry_id: str,
                           amount: float) -> str:
    """Post a late fee on one billing period of a home-site lease, dated today.

    The resident desk charges the late fee for the billing period named, tied to that period's rent
    charge by its ledger reference. The fee is added to the lease balance at once. Afterwards the
    fee shows on the lease's rent ledger and the lease balance is higher by the fee. Success is a
    receipt with the fee's ledger reference and the new balance.

    Args:
        lease_id: Id class — the lease reference number of the home-site lease charged, as returned by the lease lookup.
        billing_period: Fixed-format class — the calendar month whose rent was late, written YYYY-MM.
        source_entry_id: Id class — the ledger reference number of that billing period's rent charge, as listed on the lease's rent ledger.
        amount: Fixed-format class — the late fee charged, in USD, 2 decimal places (cents), positive, already rounded half up to the cent.

    Returns:
        A dict with: status ("posted" when the fee is on the ledger); entry_id (ledger reference of
        the fee); lease_id; billing_period (YYYY-MM); amount (USD, 2 decimal places); rent_balance
        (the lease balance after the fee, USD, 2 decimal places).
    """
    holding = ctx.find("lease_holdings", lease_id=lease_id)
    customer_id = holding[0].get("customer_id") if holding else ""
    balance = float(holding[0].get("rent_balance") or 0) if holding else 0.0
    fee = round(float(amount), 2)
    rid = ctx.make_id("lle_", lease_id, billing_period, source_entry_id, fee)
    ctx.create("lease_ledger", rid, lease_entry_id=rid, lease_id=lease_id, customer_id=customer_id,
               event_type="lease_late_fee", entry_date=ctx.now()[:10], billing_period=billing_period,
               source_entry_id=source_entry_id, amount=fee)
    new_balance = round(balance + fee, 2)
    ctx.update("lease_holdings", lease_id, rent_balance=new_balance)
    return str({"status": "posted", "entry_id": rid, "lease_id": lease_id, "billing_period": billing_period,
                "amount": fee, "rent_balance": new_balance})


@tool(owner="agent", rw="write")
def serve_nonpayment_notice_fb7be621(ctx: ToolContext, lease_id: str, amount_demanded: float, cure_days: int) -> str:
    """Serve a written nonpayment notice on a home-site lease, dated today.

    The resident desk records the notice demanding the past-due balance stated, with a cure
    deadline falling the given number of calendar days after today. The lease balance and status
    are not changed. Afterwards the notice, its amount demanded and its cure deadline show among the
    notices on the lease. Success is a receipt with the notice reference and the cure deadline.

    Args:
        lease_id: Id class — the lease reference number of the home-site lease noticed, as returned by the lease lookup.
        amount_demanded: Fixed-format class — the past-due balance the notice demands, in USD, 2 decimal places (cents).
        cure_days: Fixed-format class — length of the cure period as an integer number of calendar days counted from the day after today; the cure deadline is the last of those days.

    Returns:
        A dict with: status ("served" when the notice is recorded); notice_id (reference number of
        the notice); lease_id; notice_date (today, YYYY-MM-DD); amount_demanded (USD, 2 decimal
        places); response_deadline (the cure deadline, YYYY-MM-DD).
    """
    holding = ctx.find("lease_holdings", lease_id=lease_id)
    customer_id = holding[0].get("customer_id") if holding else ""
    today = ctx.now()[:10]
    demanded = round(float(amount_demanded), 2)
    deadline = _CalendarDays.shift(today, int(cure_days))
    rid = ctx.make_id("lno_", lease_id, today, demanded, int(cure_days))
    ctx.create("lease_notices", rid, lease_notice_id=rid, lease_id=lease_id, customer_id=customer_id,
               event_type="lease_nonpayment_notice", notice_date=today, response_deadline=deadline,
               amount_demanded=demanded)
    return str({"status": "served", "notice_id": rid, "lease_id": lease_id, "notice_date": today,
                "amount_demanded": demanded, "response_deadline": deadline})


@tool(owner="user", rw="write")
def make_lease_payment_8919b7b0(ctx: ToolContext, lease_id: str, amount: float, payment_channel: str) -> str:
    """The resident pays toward their own home-site lease balance today.

    The payment is received today through the channel the resident uses and posted to the lease's
    rent ledger with a processor confirmation number; the lease balance drops by the amount at once.
    Afterwards the payment, its channel and confirmation number show on the rent ledger and the
    balance is lower. Success is a receipt with the confirmation number and the new balance.

    Args:
        lease_id: Id class — the lease reference number of the resident's own home-site lease, as the resident desk read it out from the lease lookup.
        amount: Fixed-format class — the amount paid, in USD, 2 decimal places (cents), positive.
        payment_channel: Enum class — how the resident pays: ach_autopay is never chosen for a one-time payment; online_portal_ach when paying today from a bank account through the resident portal; online_portal_card when paying today by debit or credit card through the resident portal; office_money_order when handing a money order to the community office; office_cashiers_check when handing a cashier's check to the community office; office_personal_check when handing a personal check to the community office; sale_closing_proceeds is used only for proceeds of an in-place home sale and never for a resident's own payment.

    Returns:
        A dict with: status ("received" when the payment is posted); entry_id (ledger reference of
        the payment); confirmation_number (the processor confirmation number printed on the
        payment); lease_id; amount (USD, 2 decimal places); payment_channel; rent_balance (the lease
        balance after the payment, USD, 2 decimal places).
    """
    holding = ctx.find("lease_holdings", lease_id=lease_id)
    customer_id = holding[0].get("customer_id") if holding else ""
    balance = float(holding[0].get("rent_balance") or 0) if holding else 0.0
    paid = round(float(amount), 2)
    rid = ctx.make_id("lle_", lease_id, paid, payment_channel, ctx.now())
    confirmation = "HCP-" + rid[-8:].upper()
    ctx.create("lease_ledger", rid, lease_entry_id=rid, lease_id=lease_id, customer_id=customer_id,
               event_type="lease_payment", entry_date=ctx.now()[:10], amount=paid,
               payment_channel=payment_channel, payment_ref=confirmation)
    new_balance = round(balance - paid, 2)
    ctx.update("lease_holdings", lease_id, rent_balance=new_balance)
    return str({"status": "received", "entry_id": rid, "confirmation_number": confirmation, "lease_id": lease_id,
                "amount": paid, "payment_channel": payment_channel, "rent_balance": new_balance})


@tool(owner="user", rw="write")
def sign_repayment_agreement_730960e3(ctx: ToolContext, lease_id: str, amount_covered: float, installment_count: int,
                                      installment_amount: float, first_due_date: str) -> str:
    """The resident signs a repayment agreement on their own home-site lease, dated today.

    Signing records the resident's undertaking to repay the past-due balance it covers in the stated
    number of installments of the stated amount, the first falling due on the first due date. No
    payment is taken and the lease balance is not changed. Afterwards the agreement, its covered
    balance, installment count, installment amount and first due date show among the notices on
    the lease. Success is a receipt with the agreement reference.

    Args:
        lease_id: Id class — the lease reference number of the resident's own home-site lease, as the resident desk read it out from the lease lookup.
        amount_covered: Fixed-format class — the past-due balance the agreement covers, before the down payment, in USD, 2 decimal places (cents).
        installment_count: Fixed-format class — the number of installments, an integer.
        installment_amount: Fixed-format class — the amount of each installment, in USD, 2 decimal places (cents), already rounded half up to the cent.
        first_due_date: Fixed-format class — due date of the first installment, written YYYY-MM-DD.

    Returns:
        A dict with: status ("signed" when the agreement is recorded); agreement_id (reference
        number of the agreement); lease_id; amount_covered (USD, 2 decimal places);
        installment_count (integer); installment_amount (USD, 2 decimal places); first_due_date
        (YYYY-MM-DD).
    """
    holding = ctx.find("lease_holdings", lease_id=lease_id)
    customer_id = holding[0].get("customer_id") if holding else ""
    covered = round(float(amount_covered), 2)
    each = round(float(installment_amount), 2)
    rid = ctx.make_id("lno_", lease_id, ctx.now()[:10], covered, int(installment_count), each, first_due_date)
    ctx.create("lease_notices", rid, lease_notice_id=rid, lease_id=lease_id, customer_id=customer_id,
               event_type="lease_repayment_agreement", notice_date=ctx.now()[:10], amount_demanded=covered,
               installment_count=int(installment_count), installment_amount=each, effective_date=first_due_date)
    return str({"status": "signed", "agreement_id": rid, "lease_id": lease_id, "amount_covered": covered,
                "installment_count": int(installment_count), "installment_amount": each,
                "first_due_date": first_due_date})

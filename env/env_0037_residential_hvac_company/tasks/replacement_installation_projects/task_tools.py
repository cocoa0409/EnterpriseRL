"""Hidden task tools for the replacement_installation_projects difficulty of
env_0037_residential_hvac_company (Harbison Heating & Air, category install).

Each tool lands exactly one atomic write on an installation project and its ledger, with the
value the agent (or the homeowner) has already worked out from the published policy. No tool
aggregates history, judges eligibility, checks a prerequisite or refuses a call.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def bill_change_order_a6215d22(ctx: ToolContext, install_id: str, customer_id: str,
                               change_order_no: int, amount: float) -> str:
    """Charge one homeowner-approved change order to a replacement-installation project.

    The agent posts a single change-order charge on the project's ledger under the change-order
    number the homeowner approved, for the amount given. The charge is dated today, it raises
    the amount the homeowner owes on the project by exactly that amount, and from then on the
    project's money history shows it as a change-order charge carrying that number. Success is
    a receipt naming the new ledger entry and the project's updated balance owed.

    Args:
        install_id: Id class — the reference number of the installation project being charged,
            as shown by the installation project lookup for this homeowner.
        customer_id: Id class — the reference number of the homeowner who signed the contract,
            as shown by the customer profile lookup.
        change_order_no: Fixed-format class — the number of the approved change order this
            charge bills, written as an integer; the field takes integer >= 1 on change orders; 0 otherwise,
            and a change-order charge always carries the approved number (1 or higher), exactly
            as it appears on the homeowner's change-order approval.
        amount: Fixed-format class — the change-order charge in US dollars, as a number with no
            currency sign, expressed in USD, 2 decimal places, always positive; pass the final
            charge already rounded to the cent.

    Returns:
        A text rendering of a dictionary with these keys: install_entry_id (text, the reference
        number of the new change-order charge entry), install_id (text, the project charged),
        change_order_no (integer, the change-order number billed), amount (number in USD with
        2 decimal places, the amount charged), posted_date (text, YYYY-MM-DD, today's date) and
        project_balance (number in USD with 2 decimal places, the amount the homeowner owes on
        the project once this charge is included, or null when the project could not be read).
        A receipt carrying install_entry_id means the charge is on the project.
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("ile_", install_id, customer_id, "change_order", int(change_order_no), amt)
    today = ctx.now()[:10]
    ctx.create("install_ledger", rid, install_entry_id=rid, install_id=install_id,
               customer_id=customer_id, event_type="install_charge", line_type="change_order",
               change_order_no=int(change_order_no), accessory_code="", upgrade_variant_name="",
               amount=amt, posted_date=today, payment_method="", payment_reference="",
               finance_account_id="", source_entry_id="", claim_id="", equipment_serial="",
               registered_parts_years=0)
    rows = ctx.find("install_projects", install_id=install_id)
    balance = None
    if rows:
        balance = round(float(rows[0].get("project_balance") or 0.0) + amt, 2)
        ctx.update("install_projects", install_id, project_balance=balance)
    return str({"install_entry_id": rid, "install_id": install_id,
                "change_order_no": int(change_order_no), "amount": amt,
                "posted_date": today, "project_balance": balance})


@tool(owner="user", rw="write")
def pay_progress_installment_728e8d1f(ctx: ToolContext, install_id: str, customer_id: str,
                                      amount: float, payment_method: str) -> str:
    """The homeowner pays the progress installment on their own replacement-installation project.

    One call records a single progress payment from the homeowner on the project's ledger for
    the amount given, by the payment method the homeowner chooses, dated today, and lowers the
    amount the homeowner owes on the project by exactly that amount. The homeowner sees a
    payment confirmation reference generated for this payment. Success is a receipt carrying
    that confirmation reference and the project's updated balance owed.

    Args:
        install_id: Id class — the reference number of the installation project being paid,
            given to the homeowner by the agent from the installation project lookup.
        customer_id: Id class — the reference number of the homeowner's customer profile,
            given to the homeowner by the agent from the customer profile lookup.
        amount: Fixed-format class — the progress installment the homeowner pays, in US
            dollars as a number with no currency sign, expressed in USD, 2 decimal places, always
            positive; pass the amount already rounded to the cent.
        payment_method: Enum class — how the homeowner pays, one of: card — the homeowner pays
            with a debit or credit card; ach — the homeowner pays by electronic transfer from a
            checking or savings account; check — the homeowner pays by a paper check; financing
            — reserved for funding sent by a financing lender, never the homeowner's own payment.

    Returns:
        A text rendering of a dictionary with these keys: install_entry_id (text, the reference
        number of the new payment entry), install_id (text, the project paid), amount (number in
        USD with 2 decimal places, the amount paid), payment_method (text, the method used),
        payment_reference (text, the payment confirmation reference to give the homeowner),
        posted_date (text, YYYY-MM-DD, today's date) and project_balance (number in USD with 2
        decimal places, the amount still owed on the project once this payment is applied, or
        null when the project could not be read). A receipt carrying payment_reference means the
        payment is recorded.
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("ile_", install_id, customer_id, "progress_payment", amt, payment_method)
    ref = "HHA-PRG-" + ctx.make_id("", install_id, amt, payment_method, length=8).upper()
    today = ctx.now()[:10]
    ctx.create("install_ledger", rid, install_entry_id=rid, install_id=install_id,
               customer_id=customer_id, event_type="install_payment", line_type="progress_payment",
               change_order_no=0, accessory_code="", upgrade_variant_name="", amount=amt,
               posted_date=today, payment_method=payment_method, payment_reference=ref,
               finance_account_id="", source_entry_id="", claim_id="", equipment_serial="",
               registered_parts_years=0)
    rows = ctx.find("install_projects", install_id=install_id)
    balance = None
    if rows:
        balance = round(float(rows[0].get("project_balance") or 0.0) - amt, 2)
        ctx.update("install_projects", install_id, project_balance=balance)
    return str({"install_entry_id": rid, "install_id": install_id, "amount": amt,
                "payment_method": payment_method, "payment_reference": ref,
                "posted_date": today, "project_balance": balance})


@tool(owner="agent", rw="write")
def post_member_install_credit_c2d484b0(ctx: ToolContext, install_id: str, customer_id: str, agreement_id: str,
                                        source_entry_id: str, amount: float) -> str:
    """Post the Comfort Club member install credit on a replacement-installation contract.

    The agent records one member install credit on the project's ledger, naming the
    contract-price charge it reduces and the homeowner's Comfort Club agreement it is earned
    under, for the amount given and dated today. It lowers the amount the homeowner owes on the
    project by exactly that amount, and the project's money history then shows the member
    install credit. Success is a receipt naming the new credit entry and the updated balance.

    Args:
        install_id: Id class — the reference number of the installation project being credited,
            as shown by the installation project lookup for this homeowner.
        customer_id: Id class — the reference number of the homeowner's customer profile, as shown
            by the customer profile lookup.
        agreement_id: Id class — the reference number of the homeowner's Comfort Club agreement the
            credit is earned under, as shown by the Comfort Club agreement lookup.
        source_entry_id: Id class — the reference number of the project's contract-price charge
            entry that the credit reduces, as shown by the installation ledger lookup.
        amount: Fixed-format class — the member install credit in US dollars, as a number with no
            currency sign, expressed in USD, 2 decimal places, always positive; pass the amount
            already rounded to the cent.

    Returns:
        A text rendering of a dictionary with these keys: install_entry_id (text, the reference
        number of the new credit entry), install_id (text, the project credited), source_entry_id
        (text, the contract-price charge the credit names), amount (number in USD with 2 decimal
        places, the amount credited), posted_date (text, YYYY-MM-DD, today's date) and
        project_balance (number in USD with 2 decimal places, the amount the homeowner owes on the
        project once this credit is applied, or null when the project could not be read). A
        receipt carrying install_entry_id means the credit is on the project.
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("ile_", install_id, customer_id, agreement_id, "member_install_credit", source_entry_id, amt)
    today = ctx.now()[:10]
    ctx.create("install_ledger", rid, install_entry_id=rid, install_id=install_id,
               customer_id=customer_id, event_type="install_credit", line_type="member_install_credit",
               change_order_no=0, accessory_code="", upgrade_variant_name="", amount=amt,
               posted_date=today, payment_method="", payment_reference="", finance_account_id="",
               source_entry_id=source_entry_id, claim_id="", equipment_serial="", registered_parts_years=0)
    rows = ctx.find("install_projects", install_id=install_id)
    balance = None
    if rows:
        balance = round(float(rows[0].get("project_balance") or 0.0) - amt, 2)
        ctx.update("install_projects", install_id, project_balance=balance)
    return str({"install_entry_id": rid, "install_id": install_id, "source_entry_id": source_entry_id,
                "amount": amt, "posted_date": today, "project_balance": balance})


@tool(owner="agent", rw="write")
def post_accessory_member_discount_3312a288(ctx: ToolContext, install_id: str, customer_id: str,
                                            agreement_id: str, source_entry_id: str, accessory_code: str,
                                            amount: float) -> str:
    """Post the Comfort Club accessory member discount on an installation contract's accessories.

    The agent records one accessory member discount on the project's ledger, covering the
    accessories charged on the contract and naming the contract's highest-priced accessory charge,
    the accessory of that charge and the homeowner's Comfort Club agreement, for the amount given
    and dated today. It lowers the amount the homeowner owes on the project by exactly that
    amount, and the project's money history then shows the discount. Success is a receipt naming
    the new discount entry and the updated balance.

    Args:
        install_id: Id class — the reference number of the installation project being credited,
            as shown by the installation project lookup for this homeowner.
        customer_id: Id class — the reference number of the homeowner's customer profile, as shown
            by the customer profile lookup.
        agreement_id: Id class — the reference number of the homeowner's Comfort Club agreement the
            discount is earned under, as shown by the Comfort Club agreement lookup.
        source_entry_id: Id class — the reference number of the contract's highest-priced accessory
            charge entry, which the discount names, as shown by the installation ledger lookup.
        accessory_code: Enum class — the accessory of the named charge, exactly as written on that
            accessory charge, one of smart_thermostat_upgrade — the smart thermostat upgrade; whole_home_surge_protector
            — the whole-home surge protector; uv_germicidal_light — the UV germicidal light;
            media_air_cleaner — the media air cleaner; steam_humidifier — the steam humidifier;
            condensate_pump — the condensate pump added as an accessory.
        amount: Fixed-format class — the accessory member discount in US dollars, as a number with
            no currency sign, expressed in USD, 2 decimal places, always positive; pass the amount
            already rounded to the cent.

    Returns:
        A text rendering of a dictionary with these keys: install_entry_id (text, the reference
        number of the new discount entry), install_id (text, the project credited),
        source_entry_id (text, the accessory charge the discount names), accessory_code (text, the
        accessory), amount (number in USD with 2 decimal places, the amount credited), posted_date
        (text, YYYY-MM-DD, today's date) and project_balance (number in USD with 2 decimal places,
        the amount the homeowner owes on the project once this discount is applied, or null when
        the project could not be read). A receipt carrying install_entry_id means the discount is
        on the project.
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("ile_", install_id, customer_id, agreement_id, "accessory_member_discount",
                      source_entry_id, accessory_code, amt)
    today = ctx.now()[:10]
    ctx.create("install_ledger", rid, install_entry_id=rid, install_id=install_id,
               customer_id=customer_id, event_type="install_credit", line_type="accessory_member_discount",
               change_order_no=0, accessory_code=accessory_code, upgrade_variant_name="", amount=amt,
               posted_date=today, payment_method="", payment_reference="", finance_account_id="",
               source_entry_id=source_entry_id, claim_id="", equipment_serial="", registered_parts_years=0)
    rows = ctx.find("install_projects", install_id=install_id)
    balance = None
    if rows:
        balance = round(float(rows[0].get("project_balance") or 0.0) - amt, 2)
        ctx.update("install_projects", install_id, project_balance=balance)
    return str({"install_entry_id": rid, "install_id": install_id, "source_entry_id": source_entry_id,
                "accessory_code": accessory_code, "amount": amt, "posted_date": today,
                "project_balance": balance})


@tool(owner="user", rw="write")
def pay_contract_deposit_7afff78b(ctx: ToolContext, install_id: str, customer_id: str,
                                  amount: float, payment_method: str) -> str:
    """The homeowner pays the deposit on their own replacement-installation contract.

    One call records a single deposit payment from the homeowner on the project's ledger for
    the amount given, by the payment method the homeowner chooses, dated today, and lowers the
    amount the homeowner owes on the project by exactly that amount. The homeowner sees a
    payment confirmation reference generated for this payment. Success is a receipt carrying
    that confirmation reference and the project's updated balance owed.

    Args:
        install_id: Id class — the reference number of the installation project the deposit is
            for, given to the homeowner by the agent from the installation project lookup.
        customer_id: Id class — the reference number of the homeowner's customer profile, given to
            the homeowner by the agent from the customer profile lookup.
        amount: Fixed-format class — the deposit the homeowner pays, in US dollars as a number with
            no currency sign, expressed in USD, 2 decimal places, always positive; pass the amount
            already rounded to the cent.
        payment_method: Enum class — how the homeowner pays, one of: card — the homeowner pays with
            a debit or credit card; ach — the homeowner pays by electronic transfer from a checking
            or savings account; check — the homeowner pays by a paper check; financing — reserved
            for funding sent by a financing lender, never the homeowner's own payment.

    Returns:
        A text rendering of a dictionary with these keys: install_entry_id (text, the reference
        number of the new deposit entry), install_id (text, the project paid), amount (number in
        USD with 2 decimal places, the amount paid), payment_method (text, the method used),
        payment_reference (text, the payment confirmation reference to give the homeowner),
        posted_date (text, YYYY-MM-DD, today's date) and project_balance (number in USD with 2
        decimal places, the amount still owed on the project once this deposit is applied, or null
        when the project could not be read). A receipt carrying payment_reference means the deposit
        is recorded.
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("ile_", install_id, customer_id, "deposit", amt, payment_method)
    ref = "HHA-DEP-" + ctx.make_id("", install_id, amt, payment_method, length=8).upper()
    today = ctx.now()[:10]
    ctx.create("install_ledger", rid, install_entry_id=rid, install_id=install_id,
               customer_id=customer_id, event_type="install_payment", line_type="deposit",
               change_order_no=0, accessory_code="", upgrade_variant_name="", amount=amt,
               posted_date=today, payment_method=payment_method, payment_reference=ref,
               finance_account_id="", source_entry_id="", claim_id="", equipment_serial="",
               registered_parts_years=0)
    rows = ctx.find("install_projects", install_id=install_id)
    balance = None
    if rows:
        balance = round(float(rows[0].get("project_balance") or 0.0) - amt, 2)
        ctx.update("install_projects", install_id, project_balance=balance)
    return str({"install_entry_id": rid, "install_id": install_id, "amount": amt,
                "payment_method": payment_method, "payment_reference": ref,
                "posted_date": today, "project_balance": balance})

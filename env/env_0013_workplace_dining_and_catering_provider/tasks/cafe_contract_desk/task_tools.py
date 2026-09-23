"""Hidden task tools for the cafe_contract_desk difficulty of
env_0013_workplace_dining_and_catering_provider.

Each function is a hidden atomic write on a Workplace Cafe Management Program contract.
None of them aggregates history, judges eligibility or works out an amount: the caller
reads the contract, its ledger and the published policy, derives the figure itself and
passes it in as one fixed-format argument.
"""

from erlbench import ToolContext, tool

_CAFE_CONTRACTS = "cafe_contracts"
_CAFE_LEDGER = "cafe_ledger"


@tool(owner="user", rw="write")
def confirm_service_model_change_fa28a84a(ctx: ToolContext, cafe_contract_id: str,
                                          new_service_model: str,
                                          change_admin_fee_usd: float,
                                          service_period: str) -> str:
    """The client themselves puts a change of cafe service model into force on their own
    workplace cafe management contract and accepts the administration charge that goes with
    it. One call moves the contract onto the service model named, stamps that day as the day
    the new service model took effect, books the administration charge onto the contract's
    ledger as an administration fee for the billing period given, and raises the contract's
    unsettled balance by that charge. Afterwards the client sees the new service model on the
    contract, the day it took effect, and the administration charge standing on the ledger with
    its own printed invoice number. The confirmation text naming that invoice number is what
    shows the call completed.

    Args:
        cafe_contract_id: Id class — the reference number of the workplace cafe management
            contract whose service model is being put onto a new footing; it is returned by the
            cafe contract lookup for the client and is never typed from memory.
        new_service_model: Enum class — the service model the cafe runs under from this day on,
            written as the official full model name, one of exactly these six values.
            "Grab & Go Cafe Service" applies where the site takes an unstaffed grab and go
            counter with a single serving station and no client meal subsidy;
            "Limited Service Cafe" applies where the site takes a lightly staffed counter
            serving one meal period a day with a percentage meal subsidy;
            "Full Service Cafe" applies where the site takes a staffed kitchen serving two meal
            periods a day across several stations with mobile ordering;
            "Culinary Center Cafe" applies where the site takes a production kitchen serving
            three meal periods a day on a fixed amount per meal subsidy;
            "Executive Dining Service" applies where the site takes a small private dining room
            whose meals are met in full by the client;
            "Campus Dining Commons Service" applies where the site takes a seven day dining
            commons serving three meal periods a day across a campus.
        change_admin_fee_usd: Fixed-format class — the administration charge the client accepts
            for putting this change of service model into force, in USD, written as a decimal
            number to 2 decimal places; it is stored to 2 decimal places exactly as given and
            must be a positive amount.
        service_period: Fixed-format class — the billing period the administration charge is
            booked against, written as a calendar month in the form YYYY-MM with no day part.

    Returns:
        A single confirmation sentence in plain text. It names the contract reference the change
        was made on, the service model now in force, the day it took effect as YYYY-MM-DD, the
        administration charge booked in USD to 2 decimal places, the billing period it was booked
        against, and the printed invoice number of the new administration fee posting in the form
        INV-CF- followed by 6 digits. Receiving that sentence, with the invoice number in it, is
        what shows the change is in force and the charge is on the contract.
    """
    found = ctx.find(_CAFE_CONTRACTS, cafe_contract_id=cafe_contract_id)
    row = found[0] if found else {}
    today = ctx.now()[:10]
    amount = round(float(change_admin_fee_usd), 2)
    rid = ctx.make_id("cfl_", cafe_contract_id, new_service_model, amount, service_period)
    reference = "INV-CF-%06d" % (int(rid[-6:], 16) % 1000000)
    ctx.update(_CAFE_CONTRACTS, cafe_contract_id,
               variant_name=new_service_model,
               service_model_change_effective_date=today,
               receivable_balance_usd=round(float(row.get("receivable_balance_usd") or 0) + amount, 2))
    ctx.create(_CAFE_LEDGER, rid, cafe_ledger_id=rid, cafe_contract_id=cafe_contract_id,
               customer_id=row.get("customer_id"), event_type="cafe_management_fee_invoiced",
               charge_code="admin_fee", amount_usd=amount, posted_date=today,
               service_period=service_period, invoice_reference=reference,
               funding_lot_reference="", source_reference="", meal_period="all_day",
               payment_channel="not_applicable", site_code=row.get("site_code"))
    return (f"Contract {cafe_contract_id} now runs under {new_service_model}, effective {today}. "
            f"Administration charge of {amount:.2f} USD booked for {service_period} on invoice "
            f"{reference}.")


@tool(owner="agent", rw="write")
def raise_management_fee_invoice_00d6d0cf(ctx: ToolContext, cafe_contract_id: str,
                                          amount_usd: float, service_period: str) -> str:
    """Raise the management fee invoice on a workplace cafe management contract for one billing
    period. One call books a management fee posting of the amount given onto that contract's
    ledger against the billing period named, dates it the day of the call, gives it its own
    printed invoice number, and raises the contract's unsettled invoice balance by the same
    amount. The client afterwards sees a management fee charge for that period standing on the
    contract with an invoice number they can pay against. The confirmation sentence naming that
    invoice number is what shows the invoice was raised.

    Args:
        cafe_contract_id: Id class — the reference number of the workplace cafe management
            contract being invoiced; it is returned by the cafe contract lookup for the client.
        amount_usd: Fixed-format class — the management fee being charged for the billing period,
            in USD, written as a decimal number to 2 decimal places; it is stored to 2 decimal
            places exactly as given.
        service_period: Fixed-format class — the billing period the management fee covers,
            written as a calendar month in the form YYYY-MM with no day part.

    Returns:
        A single confirmation sentence in plain text naming the contract reference invoiced, the
        management fee amount in USD to 2 decimal places, the billing period covered, the posting
        day as YYYY-MM-DD, and the printed invoice number of the new posting in the form INV-CF-
        followed by 6 digits. That invoice number is the reference quoted on anything raised against
        this invoice, and receiving the sentence is what shows the invoice stands on
        the contract.
    """
    found = ctx.find(_CAFE_CONTRACTS, cafe_contract_id=cafe_contract_id)
    row = found[0] if found else {}
    today = ctx.now()[:10]
    amount = round(float(amount_usd), 2)
    rid = ctx.make_id("cfl_", cafe_contract_id, "management_fee", amount, service_period)
    reference = "INV-CF-%06d" % (int(rid[-6:], 16) % 1000000)
    ctx.update(_CAFE_CONTRACTS, cafe_contract_id,
               receivable_balance_usd=round(float(row.get("receivable_balance_usd") or 0) + amount, 2))
    ctx.create(_CAFE_LEDGER, rid, cafe_ledger_id=rid, cafe_contract_id=cafe_contract_id,
               customer_id=row.get("customer_id"), event_type="cafe_management_fee_invoiced",
               charge_code="management_fee", amount_usd=amount, posted_date=today,
               service_period=service_period, invoice_reference=reference,
               funding_lot_reference="", source_reference="", meal_period="all_day",
               payment_channel="not_applicable", site_code=row.get("site_code"))
    return (f"Management fee of {amount:.2f} USD invoiced on contract {cafe_contract_id} for "
            f"{service_period}, posted {today} under invoice {reference}.")


@tool(owner="agent", rw="write")
def issue_service_credit_9f99d1a6(ctx: ToolContext, cafe_contract_id: str,
                                  invoice_reference: str, credit_amount_usd: float,
                                  service_period: str) -> str:
    """Allow a service credit against one cafe invoice on a workplace cafe management contract.
    One call books a service credit posting of the amount given onto that contract's ledger,
    quoted against the invoice number named and the billing period given, dates it the day of the
    call, and reduces the contract's unsettled invoice balance by the same amount. The client
    afterwards sees the credit standing against that invoice and a smaller balance to settle. The
    confirmation sentence naming the credited invoice and the new balance is what shows the credit
    was allowed.

    Args:
        cafe_contract_id: Id class — the reference number of the workplace cafe management
            contract being credited; it is returned by the cafe contract lookup for the client.
        invoice_reference: Fixed-format class — the printed number of the cafe invoice the credit
            is allowed against, written as INV-CF- followed by 6 digits, taken exactly as it is
            printed on that invoice; an empty value is not accepted.
        credit_amount_usd: Fixed-format class — the credit being allowed against that invoice, in
            USD, written as a decimal number to 2 decimal places; it is stored to 2 decimal places
            exactly as given and must be a positive amount.
        service_period: Fixed-format class — the billing period the credit relates to, written as
            a calendar month in the form YYYY-MM with no day part.

    Returns:
        A single confirmation sentence in plain text naming the contract reference credited, the
        credit amount in USD to 2 decimal places, the invoice number it was allowed against, the
        billing period it relates to, the posting day as YYYY-MM-DD, and the contract's unsettled
        invoice balance in USD to 2 decimal places after the credit. Receiving that sentence is
        what shows the credit is on the contract.
    """
    found = ctx.find(_CAFE_CONTRACTS, cafe_contract_id=cafe_contract_id)
    row = found[0] if found else {}
    today = ctx.now()[:10]
    amount = round(float(credit_amount_usd), 2)
    balance = round(float(row.get("receivable_balance_usd") or 0) - amount, 2)
    rid = ctx.make_id("cfl_", cafe_contract_id, "service_credit", amount, invoice_reference)
    ctx.update(_CAFE_CONTRACTS, cafe_contract_id, receivable_balance_usd=balance)
    ctx.create(_CAFE_LEDGER, rid, cafe_ledger_id=rid, cafe_contract_id=cafe_contract_id,
               customer_id=row.get("customer_id"), event_type="cafe_service_credit_issued",
               charge_code="service_credit", amount_usd=amount, posted_date=today,
               service_period=service_period, invoice_reference=invoice_reference,
               funding_lot_reference="", source_reference="", meal_period="all_day",
               payment_channel="not_applicable", site_code=row.get("site_code"))
    return (f"Service credit of {amount:.2f} USD allowed on contract {cafe_contract_id} against "
            f"invoice {invoice_reference} for {service_period}, posted {today}. Unsettled balance "
            f"is now {balance:.2f} USD.")


@tool(owner="agent", rw="write")
def post_late_charge_719c9a63(ctx: ToolContext, cafe_contract_id: str, late_charge_usd: float,
                              service_period: str) -> str:
    """Raise a late charge on a workplace cafe management contract whose cafe invoicing has stood
    unpaid. One call books a contractual charge of the amount given onto that contract's ledger
    under the late charge subtype, dates it the day of the call, records it against the billing
    period named, gives it its own printed invoice number and raises the contract's unsettled
    invoice balance by the same amount. The client afterwards sees a late charge standing on the
    contract and a larger balance to settle. The confirmation sentence naming that charge and the
    new balance is what shows the charge was raised.

    Args:
        cafe_contract_id: Id class — the reference number of the workplace cafe management contract
            the late charge is raised on; it is returned by the cafe contract lookup for the client.
        late_charge_usd: Fixed-format class — the late charge being raised, in USD, written as a
            decimal number to 2 decimal places; it is stored to 2 decimal places exactly as given
            and must be a positive amount.
        service_period: Fixed-format class — the billing period the late charge is recorded
            against, written as a calendar month in the form YYYY-MM with no day part.

    Returns:
        A single confirmation sentence in plain text naming the contract reference charged, the late
        charge in USD to 2 decimal places, the billing period it was recorded against, the posting
        day as YYYY-MM-DD, the printed invoice number of the new posting in the form INV-CF-
        followed by 6 digits, and the contract's unsettled invoice balance in USD to 2 decimal
        places after the charge. Receiving that sentence is what shows the charge stands.
    """
    found = ctx.find(_CAFE_CONTRACTS, cafe_contract_id=cafe_contract_id)
    row = found[0] if found else {}
    today = ctx.now()[:10]
    amount = round(float(late_charge_usd), 2)
    balance = round(float(row.get("receivable_balance_usd") or 0) + amount, 2)
    rid = ctx.make_id("cfl_", cafe_contract_id, "late_fee", amount, service_period)
    reference = "INV-CF-%06d" % (int(rid[-6:], 16) % 1000000)
    ctx.update(_CAFE_CONTRACTS, cafe_contract_id, receivable_balance_usd=balance)
    ctx.create(_CAFE_LEDGER, rid, cafe_ledger_id=rid, cafe_contract_id=cafe_contract_id,
               customer_id=row.get("customer_id"), event_type="cafe_penalty_fee_posted",
               charge_code="late_fee", amount_usd=amount, posted_date=today,
               service_period=service_period, invoice_reference=reference,
               funding_lot_reference="", source_reference="", meal_period="not_applicable",
               payment_channel="not_applicable", site_code=row.get("site_code"))
    return (f"Late charge of {amount:.2f} USD raised on contract {cafe_contract_id} for "
            f"{service_period}, posted {today} under invoice {reference}. Unsettled balance is now "
            f"{balance:.2f} USD.")


@tool(owner="agent", rw="write")
def post_early_exit_charge_dadd74c6(ctx: ToolContext, cafe_contract_id: str, exit_charge_usd: float,
                                    service_period: str) -> str:
    """Raise the early exit charge on a workplace cafe management contract that is ending ahead of
    the last day of its contracted term. One call books a contractual charge of the amount given
    onto that contract's ledger under the early termination charge subtype, dates it the day of the
    call, records it against the billing period named, gives it its own printed invoice number and
    raises the contract's unsettled invoice balance by the same amount. The client afterwards sees
    the early exit charge standing on the contract and a larger balance to settle. The confirmation
    sentence naming that charge and the new balance is what shows it was raised.

    Args:
        cafe_contract_id: Id class — the reference number of the workplace cafe management contract
            the early exit charge is raised on; it is returned by the cafe contract lookup for the
            client.
        exit_charge_usd: Fixed-format class — the early exit charge being raised, in USD, written as
            a decimal number to 2 decimal places; it is stored to 2 decimal places exactly as given
            and must be a positive amount.
        service_period: Fixed-format class — the billing period the early exit charge is recorded
            against, written as a calendar month in the form YYYY-MM with no day part.

    Returns:
        A single confirmation sentence in plain text naming the contract reference charged, the
        early exit charge in USD to 2 decimal places, the billing period it was recorded against,
        the posting day as YYYY-MM-DD, the printed invoice number of the new posting in the form
        INV-CF- followed by 6 digits, and the contract's unsettled invoice balance in USD to 2
        decimal places after the charge. Receiving that sentence is what shows the charge stands.
    """
    found = ctx.find(_CAFE_CONTRACTS, cafe_contract_id=cafe_contract_id)
    row = found[0] if found else {}
    today = ctx.now()[:10]
    amount = round(float(exit_charge_usd), 2)
    balance = round(float(row.get("receivable_balance_usd") or 0) + amount, 2)
    rid = ctx.make_id("cfl_", cafe_contract_id, "early_termination_fee", amount, service_period)
    reference = "INV-CF-%06d" % (int(rid[-6:], 16) % 1000000)
    ctx.update(_CAFE_CONTRACTS, cafe_contract_id, receivable_balance_usd=balance)
    ctx.create(_CAFE_LEDGER, rid, cafe_ledger_id=rid, cafe_contract_id=cafe_contract_id,
               customer_id=row.get("customer_id"), event_type="cafe_penalty_fee_posted",
               charge_code="early_termination_fee", amount_usd=amount, posted_date=today,
               service_period=service_period, invoice_reference=reference,
               funding_lot_reference="", source_reference="", meal_period="not_applicable",
               payment_channel="not_applicable", site_code=row.get("site_code"))
    return (f"Early exit charge of {amount:.2f} USD raised on contract {cafe_contract_id} for "
            f"{service_period}, posted {today} under invoice {reference}. Unsettled balance is now "
            f"{balance:.2f} USD.")


@tool(owner="agent", rw="write")
def post_standby_charge_21704194(ctx: ToolContext, cafe_contract_id: str, standby_charge_usd: float,
                                 service_period: str) -> str:
    """Raise the standby charge on a workplace cafe management contract for a period in which
    counter service stood paused. One call books a contractual charge of the amount given onto that
    contract's ledger under the standby charge subtype, dates it the day of the call, records it
    against the billing period named, gives it its own printed invoice number and raises the
    contract's unsettled invoice balance by the same amount. The client afterwards sees the standby
    charge standing on the contract and a larger balance to settle. The confirmation sentence naming
    that charge and the new balance is what shows it was raised.

    Args:
        cafe_contract_id: Id class — the reference number of the workplace cafe management contract
            the standby charge is raised on; it is returned by the cafe contract lookup for the
            client.
        standby_charge_usd: Fixed-format class — the standby charge being raised for the paused
            service, in USD, written as a decimal number to 2 decimal places; it is stored to 2
            decimal places exactly as given and must be a positive amount.
        service_period: Fixed-format class — the billing period the standby charge is recorded
            against, written as a calendar month in the form YYYY-MM with no day part.

    Returns:
        A single confirmation sentence in plain text naming the contract reference charged, the
        standby charge in USD to 2 decimal places, the billing period it was recorded against, the
        posting day as YYYY-MM-DD, the printed invoice number of the new posting in the form INV-CF-
        followed by 6 digits, and the contract's unsettled invoice balance in USD to 2 decimal
        places after the charge. Receiving that sentence is what shows the charge stands.
    """
    found = ctx.find(_CAFE_CONTRACTS, cafe_contract_id=cafe_contract_id)
    row = found[0] if found else {}
    today = ctx.now()[:10]
    amount = round(float(standby_charge_usd), 2)
    balance = round(float(row.get("receivable_balance_usd") or 0) + amount, 2)
    rid = ctx.make_id("cfl_", cafe_contract_id, "standby_fee", amount, service_period)
    reference = "INV-CF-%06d" % (int(rid[-6:], 16) % 1000000)
    ctx.update(_CAFE_CONTRACTS, cafe_contract_id, receivable_balance_usd=balance)
    ctx.create(_CAFE_LEDGER, rid, cafe_ledger_id=rid, cafe_contract_id=cafe_contract_id,
               customer_id=row.get("customer_id"), event_type="cafe_penalty_fee_posted",
               charge_code="standby_fee", amount_usd=amount, posted_date=today,
               service_period=service_period, invoice_reference=reference,
               funding_lot_reference="", source_reference="", meal_period="not_applicable",
               payment_channel="not_applicable", site_code=row.get("site_code"))
    return (f"Standby charge of {amount:.2f} USD raised on contract {cafe_contract_id} for "
            f"{service_period}, posted {today} under invoice {reference}. Unsettled balance is now "
            f"{balance:.2f} USD.")


@tool(owner="user", rw="write")
def settle_contract_balance_f9be2425(ctx: ToolContext, cafe_contract_id: str,
                                     settlement_amount_usd: float, service_period: str,
                                     payment_channel: str) -> str:
    """The client themselves pays the closing settlement on their own workplace cafe management
    contract. One call books a payment of the amount given onto that contract's ledger, dates it the
    day of the call, records it against the billing period named with the tender the client used,
    and reduces the contract's unsettled invoice balance by the same amount. The client afterwards
    sees the payment standing on the contract and the balance brought down by it. The confirmation
    sentence naming the payment and the balance left is what shows the settlement went through.

    Args:
        cafe_contract_id: Id class — the reference number of the workplace cafe management contract
            being settled; it is returned by the cafe contract lookup for the client.
        settlement_amount_usd: Fixed-format class — the closing settlement the client pays, in USD,
            written as a decimal number to 2 decimal places; it is stored to 2 decimal places
            exactly as given and must be a positive amount.
        service_period: Fixed-format class — the billing period the settlement is recorded against,
            written as a calendar month in the form YYYY-MM with no day part.
        payment_channel: Enum class — how the client moved the money, one of exactly these five
            values. "ach" applies where the client pushes the money from their bank by automated
            clearing house transfer; "check" applies where the client posts a paper cheque;
            "corporate_card" applies where the client puts the amount on a company card;
            "internal_transfer" applies where the money moves between accounts already held with
            Larkspur Table rather than from the client's bank; "not_applicable" applies where the
            posting moves no money at all and is recorded for the record only.

    Returns:
        A single confirmation sentence in plain text naming the contract reference settled, the
        payment in USD to 2 decimal places, the billing period it was recorded against, the tender
        used, the posting day as YYYY-MM-DD, and the contract's unsettled invoice balance in USD to
        2 decimal places after the payment. Receiving that sentence is what shows the settlement is
        on the contract.
    """
    found = ctx.find(_CAFE_CONTRACTS, cafe_contract_id=cafe_contract_id)
    row = found[0] if found else {}
    today = ctx.now()[:10]
    amount = round(float(settlement_amount_usd), 2)
    balance = round(float(row.get("receivable_balance_usd") or 0) - amount, 2)
    rid = ctx.make_id("cfl_", cafe_contract_id, "invoice_payment", amount, service_period)
    ctx.update(_CAFE_CONTRACTS, cafe_contract_id, receivable_balance_usd=balance)
    ctx.create(_CAFE_LEDGER, rid, cafe_ledger_id=rid, cafe_contract_id=cafe_contract_id,
               customer_id=row.get("customer_id"), event_type="cafe_invoice_payment_posted",
               charge_code="invoice_payment", amount_usd=amount, posted_date=today,
               service_period=service_period, invoice_reference="",
               funding_lot_reference="", source_reference="", meal_period="not_applicable",
               payment_channel=payment_channel, site_code=row.get("site_code"))
    return (f"Closing settlement of {amount:.2f} USD paid on contract {cafe_contract_id} for "
            f"{service_period} by {payment_channel}, posted {today}. Unsettled balance is now "
            f"{balance:.2f} USD.")

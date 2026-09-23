"""Hidden task tools for the Northbeam ShieldCare protection claims desk.

Each tool lands exactly one atomic entry on a ShieldCare plan and keeps the plan's own
running figure in step with it. Nothing here judges cover, eligibility or order: the
amounts are worked out by the agent from the published rules and the plan's history and
are passed in already decided.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def bill_premium_late_fee_5ae6a6af(ctx: ToolContext, plan_id: str, late_fee_amount: float,
                                   period_start: str, channel: str) -> str:
    """Bill a late fee on a ShieldCare plan whose premium instalments have run past grace.

    One call books a single late-fee entry against the named plan for the unpaid premium
    period given, and raises the premium the customer still owes on that plan by the same
    amount, so the plan's outstanding premium figure and its history agree straight away.
    The customer sees the fee on the plan's premium history and on the next statement of
    what is owed. The confirmation line naming the new entry is what tells you the fee is
    on the plan.

    Args:
        plan_id: Id class — the reference number of the ShieldCare protection plan the fee is
            billed on, read from the plan record retrieved for this customer.
        late_fee_amount: Fixed-format class — the money amount of the fee being billed, in USD
            to 2 decimal places, rounded half to even at the cent when a longer figure is
            passed; there is no empty value, and a fee of nothing is not booked at all.
        period_start: Fixed-format class — the first day of the unpaid premium period the fee
            is billed against, written as YYYY-MM-DD in the retailer's own local calendar
            with no time part; there is no empty value.
        channel: Enum class — where this fee was raised from, one of: store — raised at a
            branch counter with the customer present; web — raised through the customer's
            online account pages; phone — raised by a care representative on a telephone
            call; mobile_app — raised from the retailer's mobile application; business_desk
            — raised by the business sales desk for a business profile.

    Returns:
        A single confirmation sentence in plain text. It names the reference of the new
        late-fee entry (a string beginning pfe_), the plan it was booked on, the amount
        billed in USD to two decimal places, and the premium now outstanding on the plan in
        USD to two decimal places. A sentence beginning "Late fee booked" means the entry
        was written and the plan's outstanding premium was raised.
    """
    rid = ctx.make_id("pfe_", plan_id, late_fee_amount, period_start, channel)
    plan = ctx.find("protection_plans", plan_id=plan_id)[0]
    amount = round(float(late_fee_amount), 2)
    ctx.create("protection_events", rid, protection_event_id=rid, plan_id=plan_id,
               customer_id=plan.get("customer_id"), event_type="protection_premium_charge",
               premium_kind="late_fee", premium_amount=amount, period_start=period_start,
               tier_at_event=plan.get("variant_name"),
               covered_item_serial=plan.get("covered_item_serial"),
               channel=channel, event_date=ctx.now()[:10])
    owed = round(float(plan.get("premium_outstanding") or 0) + amount, 2)
    ctx.update("protection_plans", plan_id, premium_outstanding=owed)
    return (f"Late fee booked as {rid} on plan {plan_id}: {amount:.2f} USD billed for the period "
            f"starting {period_start}; premium outstanding is now {owed:.2f} USD.")


@tool(owner="user", rw="write")
def settle_premium_arrears_c5640f60(ctx: ToolContext, plan_id: str, settlement_amount: float,
                                    period_start: str, payment_method: str) -> str:
    """Pay off the premium standing owed on your own ShieldCare plan.

    One call records a single premium payment you make against the named plan, applied from
    the oldest unpaid premium period given, and lowers the premium still owed on that plan
    by the amount paid, so the plan shows what is left owing straight away. You see the
    payment on the plan's premium history and the reduced balance on the plan itself. The
    confirmation line naming the new payment entry is what tells you the money has been
    taken.

    Args:
        plan_id: Id class — the reference number of the ShieldCare protection plan the payment
            is made against, as read out to you from the plan record.
        settlement_amount: Fixed-format class — the money amount you are paying, in USD to 2
            decimal places, rounded half to even at the cent when a longer figure is passed;
            there is no empty value.
        period_start: Fixed-format class — the first day of the oldest premium period the
            payment is applied from, written as YYYY-MM-DD in the retailer's own local
            calendar with no time part; there is no empty value.
        payment_method: Enum class — how you are paying, one of: card_on_file — the payment
            card already held on your profile is charged; store_credit — the balance of store
            credit on your profile is drawn down; bank_transfer — money is sent from your bank
            account; in_store_cash — cash or card handed over at a branch counter;
            business_invoice — the amount is put on the invoice account a business profile
            settles on terms.

    Returns:
        A single confirmation sentence in plain text. It names the reference of the new
        payment entry (a string beginning ppy_), the plan it was applied to, the amount paid
        in USD to two decimal places, and the premium still outstanding on the plan in USD to
        two decimal places. A sentence beginning "Premium payment received" means the money
        was taken and the plan's outstanding premium was reduced.
    """
    rid = ctx.make_id("ppy_", plan_id, settlement_amount, period_start, payment_method)
    plan = ctx.find("protection_plans", plan_id=plan_id)[0]
    amount = round(float(settlement_amount), 2)
    ctx.create("protection_events", rid, protection_event_id=rid, plan_id=plan_id,
               customer_id=plan.get("customer_id"), event_type="protection_premium_payment",
               premium_amount=amount, period_start=period_start, payment_method=payment_method,
               channel="phone", event_date=ctx.now()[:10])
    owed = round(float(plan.get("premium_outstanding") or 0) - amount, 2)
    ctx.update("protection_plans", plan_id, premium_outstanding=owed)
    return (f"Premium payment received as {rid} on plan {plan_id}: {amount:.2f} USD applied from "
            f"the period starting {period_start}; premium outstanding is now {owed:.2f} USD.")


@tool(owner="agent", rw="write")
def book_claim_payout_542e239c(ctx: ToolContext, plan_id: str, claim_reference: str,
                               covered_item_serial: str, payout_amount: float,
                               settlement_basis: str, payment_method: str,
                               service_provider: str, repair_authorization_number: str) -> str:
    """Pay an approved ShieldCare claim and draw the money from the plan's cover.

    One call books a single payout entry against the named claim on the named plan, in the
    form of settlement given, and takes the same amount off the cover still available on
    that plan, so the remaining cover and the plan's history agree straight away. The
    customer sees the settlement on the claim and the reduced cover on the plan. The
    confirmation line naming the new payout entry is what tells you the claim has been paid.

    Args:
        plan_id: Id class — the reference number of the ShieldCare protection plan the claim
            sits on, read from the plan record retrieved for this customer.
        claim_reference: Verbatim class — the claim reference the retailer issued when the
            incident was taken, copied character for character from the claim entry on the
            plan's history or from what the customer reads out, preserving the original
            wording, digits and punctuation, with no translation, normalisation,
            summarisation, addition or deletion (verbatim).
        covered_item_serial: Verbatim class — the serial number of the covered item the claim
            concerns, copied character for character from the plan record or from what the
            customer reads off the item, preserving the original wording, digits and
            punctuation, with no translation, normalisation, summarisation, addition or
            deletion (verbatim).
        payout_amount: Fixed-format class — the money amount the plan is paying on this
            settlement, in USD to 2 decimal places, rounded half to even at the cent when a
            longer figure is passed; there is no empty value.
        settlement_basis: Enum class — the form this settlement takes, one of: repair — the
            item is being put right and the repair is being paid for; replacement — a
            replacement item is being provided in place of the failed one; reimbursement —
            money is being paid to the customer instead of goods or work; buyout — the plan is
            being bought out and closed by a single payment; no_settlement — the claim is
            being closed with nothing paid on it.
        payment_method: Enum class — how the money is going out, one of: card_on_file — a
            credit is put back to the payment card held on the profile; store_credit — the
            amount is posted as store credit on the profile; bank_transfer — the money is sent
            to the customer's bank account; in_store_cash — the money is handed over at a
            branch counter; business_invoice — the amount is credited on the invoice account a
            business profile settles on terms.
        service_provider: Enum class — who carries out or carried out the work this payment settles,
            one of: in_store_bench — a bench technician at one of the retailer's own stores;
            authorized_depot — a repair depot the retailer authorises to take the item in;
            on_site_technician — a technician attending the address where the item stands;
            partner_network — an independent repairer in the retailer's partner network;
            customer_arranged — a repairer the customer found and engaged themselves.
        repair_authorization_number: Verbatim class — the authorisation number issued to the repairer
            for this claim, copied character for character from the adjudication entry on the plan's
            history, preserving the original wording, digits and punctuation, with no translation,
            normalisation, summarisation, addition or deletion (verbatim).

    Returns:
        A single confirmation sentence in plain text. It names the reference of the new payout
        entry (a string beginning pcp_), the claim and plan it was booked against, the amount
        paid in USD to two decimal places, the repairer the payment is made to, the authorisation
        number it is made against, and the cover still remaining on the plan in USD to two decimal
        places. A sentence beginning "Claim payout booked" means the money was paid and the plan's
        remaining cover was reduced.
    """
    rid = ctx.make_id("pcp_", plan_id, claim_reference, covered_item_serial, payout_amount,
                      settlement_basis, payment_method, service_provider,
                      repair_authorization_number)
    plan = ctx.find("protection_plans", plan_id=plan_id)[0]
    amount = round(float(payout_amount), 2)
    ctx.create("protection_events", rid, protection_event_id=rid, plan_id=plan_id,
               customer_id=plan.get("customer_id"), event_type="protection_claim_payout",
               claim_reference=claim_reference, payout_amount=amount,
               settlement_basis=settlement_basis, payment_method=payment_method,
               covered_item_serial=covered_item_serial, service_provider=service_provider,
               repair_authorization_number=repair_authorization_number,
               channel="phone", event_date=ctx.now()[:10])
    left = round(float(plan.get("coverage_remaining") or 0) - amount, 2)
    ctx.update("protection_plans", plan_id, coverage_remaining=left)
    return (f"Claim payout booked as {rid} for claim {claim_reference} on plan {plan_id}: "
            f"{amount:.2f} USD paid to {service_provider} against authorisation "
            f"{repair_authorization_number}; cover remaining is now {left:.2f} USD.")


@tool(owner="agent", rw="write")
def book_spoilage_allowance_79e3e314(ctx: ToolContext, plan_id: str, claim_reference: str,
                                     covered_item_serial: str, allowance_amount: float,
                                     payment_method: str) -> str:
    """Pay the food spoilage allowance owed on a ShieldCare appliance claim.

    One call books a single allowance entry against the named claim on the named plan, as
    money paid to the customer for food spoiled by the failed appliance, and takes the same
    amount off the cover still available on that plan, so the remaining cover and the plan's
    history agree straight away. The customer sees the allowance on the claim alongside any
    other settlement and the reduced cover on the plan. The confirmation line naming the new
    allowance entry is what tells you the allowance has been paid.

    Args:
        plan_id: Id class — the reference number of the ShieldCare protection plan the claim
            sits on, read from the plan record retrieved for this customer.
        claim_reference: Verbatim class — the claim reference the retailer issued when the
            incident was taken, copied character for character from the claim entry on the
            plan's history or from what the customer reads out, preserving the original
            wording, digits and punctuation, with no translation, normalisation,
            summarisation, addition or deletion (verbatim).
        covered_item_serial: Verbatim class — the serial number of the covered item the claim
            concerns, copied character for character from the plan record or from what the
            customer reads off the item, preserving the original wording, digits and
            punctuation, with no translation, normalisation, summarisation, addition or
            deletion (verbatim).
        allowance_amount: Fixed-format class — the money amount of the spoilage allowance being
            paid, in USD to 2 decimal places, rounded half to even at the cent when a longer
            figure is passed; there is no empty value.
        payment_method: Enum class — how the money is going out, one of: card_on_file — a
            credit is put back to the payment card held on the profile; store_credit — the
            amount is posted as store credit on the profile; bank_transfer — the money is sent
            to the customer's bank account; in_store_cash — the money is handed over at a
            branch counter; business_invoice — the amount is credited on the invoice account a
            business profile settles on terms.

    Returns:
        A single confirmation sentence in plain text. It names the reference of the new
        allowance entry (a string beginning pca_), the claim and plan it was booked against,
        the allowance paid in USD to two decimal places, and the cover still remaining on the
        plan in USD to two decimal places. A sentence beginning "Spoilage allowance booked"
        means the money was paid and the plan's remaining cover was reduced.
    """
    rid = ctx.make_id("pca_", plan_id, claim_reference, covered_item_serial, allowance_amount,
                      payment_method)
    plan = ctx.find("protection_plans", plan_id=plan_id)[0]
    amount = round(float(allowance_amount), 2)
    ctx.create("protection_events", rid, protection_event_id=rid, plan_id=plan_id,
               customer_id=plan.get("customer_id"), event_type="protection_claim_payout",
               claim_reference=claim_reference, payout_amount=amount,
               settlement_basis="reimbursement", payment_method=payment_method,
               covered_item_serial=covered_item_serial,
               channel="phone", event_date=ctx.now()[:10])
    left = round(float(plan.get("coverage_remaining") or 0) - amount, 2)
    ctx.update("protection_plans", plan_id, coverage_remaining=left)
    return (f"Spoilage allowance booked as {rid} for claim {claim_reference} on plan {plan_id}: "
            f"{amount:.2f} USD paid; cover remaining is now {left:.2f} USD.")


@tool(owner="agent", rw="write")
def bill_premium_instalment_3dd4c03b(ctx: ToolContext, plan_id: str, instalment_amount: float,
                                     period_start: str, period_end: str, channel: str) -> str:
    """Bill the premium instalment for one period on a ShieldCare plan held on instalments.

    One call books a single instalment entry against the named plan for the period given and
    raises the premium the customer still owes on that plan by the amount billed, so the plan's
    outstanding premium figure and its premium history agree straight away. The customer sees the
    instalment on the plan's premium history and on what the account owes. The confirmation line
    naming the new entry is what tells you the instalment is on the plan.

    Args:
        plan_id: Id class — the reference number of the ShieldCare protection plan the instalment is
            billed on, read from the plan record retrieved for this customer.
        instalment_amount: Fixed-format class — the money amount of the instalment being billed, in
            USD to 2 decimal places, rounded half to even at the cent when a longer figure is
            passed; there is no empty value.
        period_start: Fixed-format class — the first day of the premium period being billed, written
            as YYYY-MM-DD in the retailer's own local calendar with no time part; there is no empty
            value.
        period_end: Fixed-format class — the last day of that premium period, inclusive, written as
            YYYY-MM-DD in the retailer's own local calendar with no time part; there is no empty
            value.
        channel: Enum class — where this instalment was raised from, one of: store — raised at a
            branch counter with the customer present; web — raised through the customer's online
            account pages; phone — raised by a care representative on a telephone call; mobile_app
            — raised from the retailer's mobile application; business_desk — raised by the business
            sales desk for a business profile.

    Returns:
        A single confirmation sentence in plain text. It names the reference of the new instalment
        entry (a string beginning pin_), the plan and the period it was billed for, the amount
        billed in USD to two decimal places, and the premium now outstanding on the plan in USD to
        two decimal places. A sentence beginning "Instalment billed" means the entry was written and
        the plan's outstanding premium was raised.
    """
    rid = ctx.make_id("pin_", plan_id, instalment_amount, period_start, period_end, channel)
    plan = ctx.find("protection_plans", plan_id=plan_id)[0]
    amount = round(float(instalment_amount), 2)
    ctx.create("protection_events", rid, protection_event_id=rid, plan_id=plan_id,
               customer_id=plan.get("customer_id"), event_type="protection_premium_charge",
               premium_kind="monthly_instalment", premium_amount=amount,
               period_start=period_start, period_end=period_end,
               tier_at_event=plan.get("variant_name"),
               covered_item_serial=plan.get("covered_item_serial"),
               channel=channel, event_date=ctx.now()[:10])
    owed = round(float(plan.get("premium_outstanding") or 0) + amount, 2)
    ctx.update("protection_plans", plan_id, premium_outstanding=owed)
    return (f"Instalment billed as {rid} on plan {plan_id} for the period {period_start} to "
            f"{period_end}: {amount:.2f} USD; premium outstanding is now {owed:.2f} USD.")


@tool(owner="agent", rw="write")
def bill_claim_deductible_d5a520f4(ctx: ToolContext, plan_id: str, claim_reference: str,
                                   deductible_amount: float) -> str:
    """Bill the claim excess the customer owes on an approved ShieldCare claim.

    One call books a single excess entry against the named claim on the named plan and raises the
    claim excess the customer still owes on that plan by the same amount, so the plan's outstanding
    excess figure and its history agree straight away. The customer sees the excess against the
    claim and on what the account owes. The confirmation line naming the new entry is what tells you
    the excess is on the plan.

    Args:
        plan_id: Id class — the reference number of the ShieldCare protection plan the claim sits on,
            read from the plan record retrieved for this customer.
        claim_reference: Verbatim class — the claim reference the retailer issued when the incident
            was taken, copied character for character from the claim entry on the plan's history or
            from what the customer reads out, preserving the original wording, digits and
            punctuation, with no translation, normalisation, summarisation, addition or deletion
            (verbatim).
        deductible_amount: Fixed-format class — the money amount of the excess being billed, in USD
            to 2 decimal places, rounded half to even at the cent when a longer figure is passed;
            there is no empty value.

    Returns:
        A single confirmation sentence in plain text. It names the reference of the new excess entry
        (a string beginning pdc_), the claim and plan it was billed against, the amount billed in USD
        to two decimal places, and the claim excess now outstanding on the plan in USD to two
        decimal places. A sentence beginning "Claim excess billed" means the entry was written and
        the plan's outstanding excess was raised.
    """
    rid = ctx.make_id("pdc_", plan_id, claim_reference, deductible_amount)
    plan = ctx.find("protection_plans", plan_id=plan_id)[0]
    amount = round(float(deductible_amount), 2)
    ctx.create("protection_events", rid, protection_event_id=rid, plan_id=plan_id,
               customer_id=plan.get("customer_id"), event_type="protection_deductible_charge",
               claim_reference=claim_reference, deductible_amount=amount,
               tier_at_event=plan.get("variant_name"), event_date=ctx.now()[:10])
    owed = round(float(plan.get("deductible_outstanding") or 0) + amount, 2)
    ctx.update("protection_plans", plan_id, deductible_outstanding=owed)
    return (f"Claim excess billed as {rid} for claim {claim_reference} on plan {plan_id}: "
            f"{amount:.2f} USD; claim excess outstanding is now {owed:.2f} USD.")


@tool(owner="user", rw="write")
def settle_claim_deductible_46d57fef(ctx: ToolContext, plan_id: str, claim_reference: str,
                                     settlement_amount: float, payment_method: str) -> str:
    """Pay the claim excess standing against your own ShieldCare claim.

    One call records a single excess payment you make against the named claim on the named plan and
    lowers the claim excess still owed on that plan by the amount paid, so the plan shows what is
    left owing straight away. You see the payment against the claim and the reduced balance on the
    plan. The confirmation line naming the new payment entry is what tells you the money has been
    taken.

    Args:
        plan_id: Id class — the reference number of the ShieldCare protection plan the claim sits on,
            as read out to you from the plan record.
        claim_reference: Verbatim class — the claim reference the retailer issued when the incident
            was taken, copied character for character from the claim entry read out to you,
            preserving the original wording, digits and punctuation, with no translation,
            normalisation, summarisation, addition or deletion (verbatim).
        settlement_amount: Fixed-format class — the money amount you are paying toward the excess, in
            USD to 2 decimal places, rounded half to even at the cent when a longer figure is
            passed; there is no empty value.
        payment_method: Enum class — how you are paying, one of: card_on_file — the payment card
            already held on your profile is charged; store_credit — the balance of store credit on
            your profile is drawn down; bank_transfer — money is sent from your bank account;
            in_store_cash — cash or card handed over at a branch counter; business_invoice — the
            amount is put on the invoice account a business profile settles on terms.

    Returns:
        A single confirmation sentence in plain text. It names the reference of the new payment entry
        (a string beginning pdp_), the claim and plan it was applied to, the amount paid in USD to
        two decimal places, and the claim excess still outstanding on the plan in USD to two decimal
        places. A sentence beginning "Claim excess payment received" means the money was taken and
        the plan's outstanding excess was reduced.
    """
    rid = ctx.make_id("pdp_", plan_id, claim_reference, settlement_amount, payment_method)
    plan = ctx.find("protection_plans", plan_id=plan_id)[0]
    amount = round(float(settlement_amount), 2)
    ctx.create("protection_events", rid, protection_event_id=rid, plan_id=plan_id,
               customer_id=plan.get("customer_id"), event_type="protection_deductible_payment",
               claim_reference=claim_reference, deductible_amount=amount,
               payment_method=payment_method, channel="business_desk", event_date=ctx.now()[:10])
    owed = round(float(plan.get("deductible_outstanding") or 0) - amount, 2)
    ctx.update("protection_plans", plan_id, deductible_outstanding=owed)
    return (f"Claim excess payment received as {rid} for claim {claim_reference} on plan {plan_id}: "
            f"{amount:.2f} USD paid; claim excess outstanding is now {owed:.2f} USD.")


@tool(owner="user", rw="write")
def settle_fleet_invoice_2818623b(ctx: ToolContext, plan_id: str, settlement_amount: float,
                                  period_start: str, payment_method: str) -> str:
    """Settle the premium invoice standing on your own ShieldCare plan.

    One call records a single premium payment you make against the named plan, applied from the
    premium period given, and lowers the premium still owed on that plan by the amount paid, so the
    plan shows what is left owing straight away. You see the payment on the plan's premium history
    and the reduced balance on the plan. The confirmation line naming the new payment entry is what
    tells you the money has been taken.

    Args:
        plan_id: Id class — the reference number of the ShieldCare protection plan the invoice belongs
            to, as read out to you from the plan record.
        settlement_amount: Fixed-format class — the money amount you are settling, in USD to 2
            decimal places, rounded half to even at the cent when a longer figure is passed; there
            is no empty value.
        period_start: Fixed-format class — the first day of the premium period the payment is applied
            from, written as YYYY-MM-DD in the retailer's own local calendar with no time part;
            there is no empty value.
        payment_method: Enum class — how you are settling, one of: card_on_file — the payment card
            already held on your profile is charged; store_credit — the balance of store credit on
            your profile is drawn down; bank_transfer — money is sent from your bank account;
            in_store_cash — cash or card handed over at a branch counter; business_invoice — the
            amount is put on the invoice account a business profile settles on terms.

    Returns:
        A single confirmation sentence in plain text. It names the reference of the new payment entry
        (a string beginning pfi_), the plan it was applied to, the amount settled in USD to two
        decimal places, and the premium still outstanding on the plan in USD to two decimal places.
        A sentence beginning "Invoice settlement received" means the money was taken and the plan's
        outstanding premium was reduced.
    """
    rid = ctx.make_id("pfi_", plan_id, settlement_amount, period_start, payment_method)
    plan = ctx.find("protection_plans", plan_id=plan_id)[0]
    amount = round(float(settlement_amount), 2)
    ctx.create("protection_events", rid, protection_event_id=rid, plan_id=plan_id,
               customer_id=plan.get("customer_id"), event_type="protection_premium_payment",
               premium_amount=amount, period_start=period_start, payment_method=payment_method,
               channel="business_desk", event_date=ctx.now()[:10])
    owed = round(float(plan.get("premium_outstanding") or 0) - amount, 2)
    ctx.update("protection_plans", plan_id, premium_outstanding=owed)
    return (f"Invoice settlement received as {rid} on plan {plan_id}: {amount:.2f} USD applied from "
            f"the period starting {period_start}; premium outstanding is now {owed:.2f} USD.")

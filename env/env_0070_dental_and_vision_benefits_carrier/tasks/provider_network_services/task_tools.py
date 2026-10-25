"""Hidden task tools of the provider_network_services difficulty (Cascade Mutual Dental & Vision).

Each tool performs one atomic write on the provider payment ledger of one network participation
agreement. The tools judge nothing: every amount is worked out by the caller from the published
rules and passed in as a fixed-format value.
"""

from erlbench import ToolContext, tool


class _Ledger:
    """Value helpers shared by the tools below (no reads or writes of their own)."""

    @staticmethod
    def practice_of(rows):
        return rows[0].get("customer_id", "") if rows else ""

    @staticmethod
    def case_number_of(rows):
        return rows[0].get("overpayment_case_number", "") if rows else ""

    @staticmethod
    def receipt(**fields):
        return str(fields)


@tool(owner="agent", rw="write")
def book_capitation_withholding_57430a7a(ctx: ToolContext, provider_agreement_id: str, original_payment_event_id: str,
                                         remittance_number: str, withheld_amount: float) -> str:
    """Book a continuing withholding against a capitation payment of a DHMO primary care dentist agreement: Cascade keeps
    part of that capitation payment to recover an overpayment of the practice that is already being recovered. One call
    adds one withholding entry to the agreement's overpayment ledger, which lowers the open amount of that overpayment by
    the amount withheld and shows on the practice's capitation remittance advice as an amount withheld.

    Args:
        provider_agreement_id: Id class — the reference number of the network participation agreement whose capitation
            payment is withheld from, as returned by the agreement lookup for the practice.
        original_payment_event_id: Id class — the reference number of the overpayment notice entry being recovered, as
            returned by the provider payment and overpayment lookup for that agreement.
        remittance_number: Verbatim class — the remittance advice number of the capitation payment withheld from, copied
            character for character from the remittance entry returned by the provider payment and overpayment lookup,
            preserving every letter, digit and hyphen with no normalisation (verbatim).
        withheld_amount: Fixed-format class — the amount kept from the capitation payment, in USD, a positive number with 2
            decimal places, rounded half up to the cent by the caller.

    Returns:
        A text rendering of a dictionary confirming the booking, with these fields: status (the text "booked" when the
        withholding entry was added), entry_id (text reference number of the new withholding entry), provider_agreement_id
        (text, echoed), overpayment_case_number (text case number printed on the overpayment notice recovered),
        remittance_number (text, echoed), amount (number, USD with 2 decimal places, the amount withheld) and event_date
        (text date YYYY-MM-DD on which the withholding was booked).
    """
    amount = round(float(withheld_amount), 2)
    rid = ctx.make_id("ppe_", provider_agreement_id, original_payment_event_id, remittance_number, amount)
    practice = _Ledger.practice_of(ctx.find("provider_agreements", provider_agreement_id=provider_agreement_id))
    case_no = _Ledger.case_number_of(ctx.find("provider_payment_events", provider_payment_event_id=original_payment_event_id))
    day = ctx.now()[:10]
    ctx.create("provider_payment_events", rid, provider_payment_event_id=rid, provider_agreement_id=provider_agreement_id,
               customer_id=practice, event_type="provider_overpayment_recouped", remittance_number=remittance_number,
               remittance_component="not_applicable", overpayment_case_number=case_no, source_product="not_applicable",
               dental_claim_line_id=None, vision_claim_id=None, ortho_payment_id=None, original_payment_date="",
               amount=amount, event_date=day, original_payment_event_id=original_payment_event_id)
    return _Ledger.receipt(status="booked", entry_id=rid, provider_agreement_id=provider_agreement_id,
                    overpayment_case_number=case_no, remittance_number=remittance_number, amount=amount, event_date=day)


@tool(owner="agent", rw="write")
def pay_repayment_interest_bafa5446(ctx: ToolContext, provider_agreement_id: str, interest_amount: float) -> str:
    """Pay a practice the prompt-pay interest owed on money Cascade repaid to it because it had recovered more than an
    overpayment finally came to. One call issues one interest payment on its own remittance to the agreement's payee account, adds that
    interest payment to the agreement's payment ledger as a prompt-pay interest component, and gives it a new remittance
    advice number that the practice sees on its remittance advice.

    Args:
        provider_agreement_id: Id class — the reference number of the network participation agreement the interest is paid
            under, as returned by the agreement lookup for the practice.
        interest_amount: Fixed-format class — the interest paid, in USD, a non-negative number with 2 decimal places,
            rounded half up to the cent by the caller.

    Returns:
        A text rendering of a dictionary confirming the payment, with these fields: status (the text "paid" when the
        interest payment was issued), entry_id (text reference number of the new payment entry), provider_agreement_id
        (text, echoed), remittance_number (text remittance advice number generated for this interest payment),
        remittance_component (the text "prompt_pay_interest"), amount (number, USD with 2 decimal places) and event_date
        (text date YYYY-MM-DD of the payment).
    """
    amount = round(float(interest_amount), 2)
    rid = ctx.make_id("ppe_", provider_agreement_id, "prompt_pay_interest", amount)
    remit_no = "EFT75-INT-" + rid[-8:].upper()
    practice = _Ledger.practice_of(ctx.find("provider_agreements", provider_agreement_id=provider_agreement_id))
    day = ctx.now()[:10]
    ctx.create("provider_payment_events", rid, provider_payment_event_id=rid, provider_agreement_id=provider_agreement_id,
               customer_id=practice, event_type="provider_remittance_issued", remittance_number=remit_no,
               remittance_component="prompt_pay_interest", overpayment_case_number="", source_product="not_applicable",
               dental_claim_line_id=None, vision_claim_id=None, ortho_payment_id=None, original_payment_date="",
               amount=amount, event_date=day, original_payment_event_id=None)
    return _Ledger.receipt(status="paid", entry_id=rid, provider_agreement_id=provider_agreement_id, remittance_number=remit_no,
                    remittance_component="prompt_pay_interest", amount=amount, event_date=day)


@tool(owner="user", rw="write")
def pay_exit_settlement_0b962b39(ctx: ToolContext, provider_agreement_id: str, original_payment_event_id: str,
                                 settlement_amount: float) -> str:
    """The practice pays Cascade its exit settlement on a DHMO primary care dentist agreement that is ending: the practice
    authorises an electronic payment from its own account for the amount it has been told, and Cascade records it as a
    refund received on the practice's overpayment ledger against the overpayment named. The open amount of that overpayment
    falls by the amount paid, and the practice receives a payment confirmation.

    Args:
        provider_agreement_id: Id class — the reference number of the network participation agreement being settled, as
            read out to the practice by the representative from the agreement lookup.
        original_payment_event_id: Id class — the reference number of the overpayment notice entry the payment is recorded
            against, as read out to the practice by the representative from the provider payment and overpayment lookup.
        settlement_amount: Fixed-format class — the amount the practice pays, in USD, a positive number with 2 decimal
            places, as stated to the practice by the representative.

    Returns:
        A text rendering of a dictionary confirming the payment, with these fields: status (the text "received" when the
        payment was recorded), confirmation_id (text reference number of the refund-received entry), provider_agreement_id
        (text, echoed), overpayment_case_number (text case number of the overpayment the payment was recorded against),
        amount (number, USD with 2 decimal places) and event_date (text date YYYY-MM-DD of receipt).
    """
    amount = round(float(settlement_amount), 2)
    rid = ctx.make_id("ppe_", provider_agreement_id, original_payment_event_id, "exit_settlement", amount)
    practice = _Ledger.practice_of(ctx.find("provider_agreements", provider_agreement_id=provider_agreement_id))
    case_no = _Ledger.case_number_of(ctx.find("provider_payment_events", provider_payment_event_id=original_payment_event_id))
    day = ctx.now()[:10]
    ctx.create("provider_payment_events", rid, provider_payment_event_id=rid, provider_agreement_id=provider_agreement_id,
               customer_id=practice, event_type="provider_overpayment_refund_received", remittance_number="",
               remittance_component="not_applicable", overpayment_case_number=case_no, source_product="not_applicable",
               dental_claim_line_id=None, vision_claim_id=None, ortho_payment_id=None, original_payment_date="",
               amount=amount, event_date=day, original_payment_event_id=original_payment_event_id)
    return _Ledger.receipt(status="received", confirmation_id=rid, provider_agreement_id=provider_agreement_id,
                    overpayment_case_number=case_no, amount=amount, event_date=day)


@tool(owner="agent", rw="write")
def book_run_withholding_d2ce9ec8(ctx: ToolContext, provider_agreement_id: str, original_payment_event_id: str,
                                  remittance_number: str, withheld_amount: float) -> str:
    """Book a continuing withholding against a claim payment run of an agreement: Cascade keeps part of that run's claim
    payments to keep recovering an overpayment of the practice that is already being recovered. One call adds one
    withholding entry to the agreement's overpayment ledger, which lowers the open amount of that overpayment by the amount
    withheld and shows on the run's remittance advice as an amount withheld.

    Args:
        provider_agreement_id: Id class — the reference number of the network participation agreement whose claim payment
            run is withheld from, as returned by the agreement lookup for the practice.
        original_payment_event_id: Id class — the reference number of the overpayment notice entry being recovered, as
            returned by the provider payment and overpayment lookup for that agreement.
        remittance_number: Verbatim class — the remittance advice number of the claim payment run withheld from, copied
            character for character from the remittance entry returned by the provider payment and overpayment lookup,
            preserving every letter, digit and hyphen with no normalisation (verbatim).
        withheld_amount: Fixed-format class — the amount kept from the run, in USD, a positive number with 2 decimal places,
            rounded half up to the cent by the caller.

    Returns:
        A text rendering of a dictionary confirming the booking, with these fields: status (the text "booked" when the
        withholding entry was added), entry_id (text reference number of the new withholding entry), provider_agreement_id
        (text, echoed), overpayment_case_number (text case number printed on the overpayment notice recovered),
        remittance_number (text, echoed), amount (number, USD with 2 decimal places) and event_date (text date YYYY-MM-DD).
    """
    amount = round(float(withheld_amount), 2)
    rid = ctx.make_id("ppe_", provider_agreement_id, original_payment_event_id, remittance_number, amount, "run")
    practice = _Ledger.practice_of(ctx.find("provider_agreements", provider_agreement_id=provider_agreement_id))
    case_no = _Ledger.case_number_of(ctx.find("provider_payment_events", provider_payment_event_id=original_payment_event_id))
    day = ctx.now()[:10]
    ctx.create("provider_payment_events", rid, provider_payment_event_id=rid, provider_agreement_id=provider_agreement_id,
               customer_id=practice, event_type="provider_overpayment_recouped", remittance_number=remittance_number,
               remittance_component="not_applicable", overpayment_case_number=case_no, source_product="not_applicable",
               dental_claim_line_id=None, vision_claim_id=None, ortho_payment_id=None, original_payment_date="",
               amount=amount, event_date=day, original_payment_event_id=original_payment_event_id)
    return _Ledger.receipt(status="booked", entry_id=rid, provider_agreement_id=provider_agreement_id,
                           overpayment_case_number=case_no, remittance_number=remittance_number, amount=amount, event_date=day)


@tool(owner="agent", rw="write")
def book_decision_withholding_431b56e1(ctx: ToolContext, provider_agreement_id: str, original_payment_event_id: str,
                                       remittance_number: str, withheld_amount: float) -> str:
    """Book the withholding that resumes recovery of an overpayment whose dispute by the practice has been decided
    upholding or reducing it: Cascade keeps part of a claim payment run toward the amount that stands. One call adds one
    withholding entry to the agreement's overpayment ledger, which lowers the open amount of the decided overpayment by the
    amount withheld and shows on the run's remittance advice as an amount withheld.

    Args:
        provider_agreement_id: Id class — the reference number of the network participation agreement whose claim payment
            run is withheld from, as returned by the agreement lookup for the practice.
        original_payment_event_id: Id class — the reference number of the decided overpayment notice entry, as returned by
            the provider payment and overpayment lookup or the dispute lookup for that agreement.
        remittance_number: Verbatim class — the remittance advice number of the claim payment run withheld from, copied
            character for character from the remittance entry returned by the provider payment and overpayment lookup,
            preserving every letter, digit and hyphen with no normalisation (verbatim).
        withheld_amount: Fixed-format class — the amount kept from the run, in USD, a positive number with 2 decimal places,
            rounded half up to the cent by the caller.

    Returns:
        A text rendering of a dictionary confirming the booking, with these fields: status (the text "booked" when the
        withholding entry was added), entry_id (text reference number of the new withholding entry), provider_agreement_id
        (text, echoed), overpayment_case_number (text case number printed on the decided overpayment notice),
        remittance_number (text, echoed), amount (number, USD with 2 decimal places) and event_date (text date YYYY-MM-DD).
    """
    amount = round(float(withheld_amount), 2)
    rid = ctx.make_id("ppe_", provider_agreement_id, original_payment_event_id, remittance_number, amount, "decision")
    practice = _Ledger.practice_of(ctx.find("provider_agreements", provider_agreement_id=provider_agreement_id))
    case_no = _Ledger.case_number_of(ctx.find("provider_payment_events", provider_payment_event_id=original_payment_event_id))
    day = ctx.now()[:10]
    ctx.create("provider_payment_events", rid, provider_payment_event_id=rid, provider_agreement_id=provider_agreement_id,
               customer_id=practice, event_type="provider_overpayment_recouped", remittance_number=remittance_number,
               remittance_component="not_applicable", overpayment_case_number=case_no, source_product="not_applicable",
               dental_claim_line_id=None, vision_claim_id=None, ortho_payment_id=None, original_payment_date="",
               amount=amount, event_date=day, original_payment_event_id=original_payment_event_id)
    return _Ledger.receipt(status="booked", entry_id=rid, provider_agreement_id=provider_agreement_id,
                           overpayment_case_number=case_no, remittance_number=remittance_number, amount=amount, event_date=day)


@tool(owner="user", rw="write")
def pay_plan_down_payment_331c146f(ctx: ToolContext, provider_agreement_id: str, original_payment_event_id: str,
                                   down_payment_amount: float) -> str:
    """The practice pays Cascade part of its open overpayments on an agreement directly: the practice authorises an
    electronic payment from its own account for the amount it has been told, and Cascade records it as a refund received on
    the practice's overpayment ledger against the overpayment named. The open amount of that
    overpayment falls by the amount paid, and the practice receives a payment confirmation.

    Args:
        provider_agreement_id: Id class — the reference number of the network participation agreement the payment is
            made on, as read out to the practice by the representative from the agreement lookup.
        original_payment_event_id: Id class — the reference number of the overpayment notice entry the down payment is
            recorded against, as read out to the practice by the representative from the provider payment and overpayment
            lookup.
        down_payment_amount: Fixed-format class — the amount the practice pays, in USD, a positive number with 2 decimal
            places, as stated to the practice by the representative.

    Returns:
        A text rendering of a dictionary confirming the payment, with these fields: status (the text "received" when the
        payment was recorded), confirmation_id (text reference number of the refund-received entry), provider_agreement_id
        (text, echoed), overpayment_case_number (text case number of the overpayment the payment was recorded against),
        amount (number, USD with 2 decimal places) and event_date (text date YYYY-MM-DD of receipt).
    """
    amount = round(float(down_payment_amount), 2)
    rid = ctx.make_id("ppe_", provider_agreement_id, original_payment_event_id, "plan_down_payment", amount)
    practice = _Ledger.practice_of(ctx.find("provider_agreements", provider_agreement_id=provider_agreement_id))
    case_no = _Ledger.case_number_of(ctx.find("provider_payment_events", provider_payment_event_id=original_payment_event_id))
    day = ctx.now()[:10]
    ctx.create("provider_payment_events", rid, provider_payment_event_id=rid, provider_agreement_id=provider_agreement_id,
               customer_id=practice, event_type="provider_overpayment_refund_received", remittance_number="",
               remittance_component="not_applicable", overpayment_case_number=case_no, source_product="not_applicable",
               dental_claim_line_id=None, vision_claim_id=None, ortho_payment_id=None, original_payment_date="",
               amount=amount, event_date=day, original_payment_event_id=original_payment_event_id)
    return _Ledger.receipt(status="received", confirmation_id=rid, provider_agreement_id=provider_agreement_id,
                           overpayment_case_number=case_no, amount=amount, event_date=day)


@tool(owner="agent", rw="write")
def book_plan_installment_e88126b0(ctx: ToolContext, provider_agreement_id: str, original_payment_event_id: str,
                                   remittance_number: str, installment_amount: float) -> str:
    """Book an installment of a practice's repayment plan against a claim payment run of an agreement: Cascade keeps the
    installment from that run's claim payments. One call adds one
    installment withholding entry to the agreement's overpayment ledger, which lowers the open amount of the overpayment
    named by the installment and shows on the run's remittance advice as an amount withheld.

    Args:
        provider_agreement_id: Id class — the reference number of the network participation agreement whose claim payment
            run is withheld from, as returned by the agreement lookup for the practice.
        original_payment_event_id: Id class — the reference number of the overpayment notice entry the installment is
            booked against, as returned by the provider payment and overpayment lookup for that agreement.
        remittance_number: Verbatim class — the remittance advice number of the claim payment run withheld from, copied
            character for character from the remittance entry returned by the provider payment and overpayment lookup,
            preserving every letter, digit and hyphen with no normalisation (verbatim).
        installment_amount: Fixed-format class — the installment kept from the run, in USD, a positive number with 2
            decimal places, rounded half up to the cent by the caller.

    Returns:
        A text rendering of a dictionary confirming the booking, with these fields: status (the text "booked" when the
        installment entry was added), entry_id (text reference number of the new installment entry),
        provider_agreement_id (text, echoed), overpayment_case_number (text case number of the overpayment the installment
        was booked against), remittance_number (text, echoed), amount (number, USD with 2 decimal places) and event_date
        (text date YYYY-MM-DD).
    """
    amount = round(float(installment_amount), 2)
    rid = ctx.make_id("ppe_", provider_agreement_id, original_payment_event_id, remittance_number, amount, "plan")
    practice = _Ledger.practice_of(ctx.find("provider_agreements", provider_agreement_id=provider_agreement_id))
    case_no = _Ledger.case_number_of(ctx.find("provider_payment_events", provider_payment_event_id=original_payment_event_id))
    day = ctx.now()[:10]
    ctx.create("provider_payment_events", rid, provider_payment_event_id=rid, provider_agreement_id=provider_agreement_id,
               customer_id=practice, event_type="provider_overpayment_recouped", remittance_number=remittance_number,
               remittance_component="not_applicable", overpayment_case_number=case_no, source_product="not_applicable",
               dental_claim_line_id=None, vision_claim_id=None, ortho_payment_id=None, original_payment_date="",
               amount=amount, event_date=day, original_payment_event_id=original_payment_event_id)
    return _Ledger.receipt(status="booked", entry_id=rid, provider_agreement_id=provider_agreement_id,
                           overpayment_case_number=case_no, remittance_number=remittance_number, amount=amount, event_date=day)

"""Hidden task tools for the lease_end_servicing difficulty of env_0066_captive_auto_finance_company
(Kestrel Closed-End Consumer Lease, lease-end servicing). Reached only through unlock_* -> call_*."""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def post_wear_forgiveness_925a15e3(ctx: ToolContext, customer_id: str, lease_contract_id: str, waived_txn_id: str,
                                   amount: float, qualifying_account_number: str) -> str:
    """Record a wear forgiveness waiver against the excess wear charge billed when a Kestrel closed-end lease
    ended. One call books one waiver entry on the lease's posting history with waiver reason wear_forgiveness,
    linked to the excess wear charge it forgives, and lowers the lease's end-of-term balance by the amount
    waived. The lessee sees the forgiveness as a credit on the lease-end account and a smaller balance
    owed. The receipt confirms the waiver entry and states the end-of-term balance left.

    Args:
        customer_id: Id class — the customer reference number of the lessee, read from the customer profile
            lookup.
        lease_contract_id: Id class — the reference number of the lease record whose end-of-term account
            receives the waiver, read from the lease lookup.
        waived_txn_id: Id class — the reference number of the excess wear charge entry being forgiven, read
            from the lease posting history lookup.
        amount: Fixed-format class — the forgiveness amount in USD, a positive number with 2 decimal places,
            rounded to the cent.
        qualifying_account_number: Verbatim class — the qualifying account number the wear forgiveness rule
            names for this waiver, copied character for character from that contract's account number as returned
            by the contract lookup, or an empty string when the rule names none (verbatim).

    Returns:
        A dictionary receipt: waiver_id (string, reference number of the new waiver entry), customer_id
        (string, the lessee), lease_contract_id
        (string, the lease credited), waived_txn_id (string, the charge forgiven), amount (number, USD forgiven,
        2 decimal places), waiver_reason (string, always wear_forgiveness), end_of_term_balance (number, USD
        left owed on the lease-end account net of this waiver, 2 decimal places) and status (string, posted
        when the waiver is on the account).
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("lwv_", customer_id, lease_contract_id, waived_txn_id, amt, qualifying_account_number)
    lease = ctx.find("lease_contracts", lease_contract_id=lease_contract_id)
    ctx.create("lease_transactions", rid, lease_txn_id=rid, lease_contract_id=lease_contract_id,
               customer_id=customer_id, event_type="lease_end_charge_waiver", txn_date=ctx.now()[:10],
               amount=amt, waived_txn_id=waived_txn_id, waiver_reason="wear_forgiveness",
               qualifying_account_number=qualifying_account_number, payment_channel="not_applicable",
               payment_purpose="not_applicable", fee_type="excess_wear_charge")
    balance = round(float((lease[0].get("end_of_term_balance") if lease else 0) or 0) - amt, 2)
    ctx.update("lease_contracts", lease_contract_id, end_of_term_balance=balance)
    return str({"waiver_id": rid, "customer_id": customer_id, "lease_contract_id": lease_contract_id, "waived_txn_id": waived_txn_id,
                "amount": amt, "waiver_reason": "wear_forgiveness", "end_of_term_balance": balance,
                "status": "posted"})


@tool(owner="user", rw="write")
def pay_end_of_term_hold_a939b773(ctx: ToolContext, lease_contract_id: str, amount: float,
                                  funding_account_last4: str) -> str:
    """The lessee pays a hold payment on the unpaid end-of-term balance of their own Kestrel closed-end
    lease through the self-service payment line, drawn by ACH from the lessee's own bank account. One call
    posts one payment entry against end-of-term charges on the lease's posting history and lowers the lease's
    end-of-term balance by the amount paid. The lessee hears a confirmation with the payment reference and the
    balance still owed. The receipt confirms the posting.

    Args:
        lease_contract_id: Id class — the reference number of the lessee's lease record, as given to the
            lessee by the representative from the lease lookup.
        amount: Fixed-format class — the payment amount in USD, a positive number with 2 decimal places,
            rounded to the cent.
        funding_account_last4: Fixed-format class — the last four digits of the lessee's own bank account the
            payment is drawn from, format 4 digits, or empty when the lessee names no
            account; the lessee states them.

    Returns:
        A dictionary receipt: payment_id (string, reference number of the posted payment), lease_contract_id
        (string, the lease paid), amount (number, USD paid, 2 decimal places), payment_channel (string, always
        phone_ivr_ach), end_of_term_balance (number, USD left owed on the lease-end account net of the
        payment, 2 decimal places) and status (string, posted when the payment is on the account).
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("lep_", lease_contract_id, amt, funding_account_last4)
    lease = ctx.find("lease_contracts", lease_contract_id=lease_contract_id)
    customer_id = lease[0].get("customer_id") if lease else ""
    ctx.create("lease_transactions", rid, lease_txn_id=rid, lease_contract_id=lease_contract_id,
               customer_id=customer_id, event_type="lease_end_of_term_payment", txn_date=ctx.now()[:10],
               amount=amt, payment_channel="phone_ivr_ach", funding_account_last4=funding_account_last4,
               payment_purpose="end_of_term_charges")
    balance = round(float((lease[0].get("end_of_term_balance") if lease else 0) or 0) - amt, 2)
    ctx.update("lease_contracts", lease_contract_id, end_of_term_balance=balance)
    return str({"payment_id": rid, "lease_contract_id": lease_contract_id, "amount": amt,
                "payment_channel": "phone_ivr_ach", "end_of_term_balance": balance, "status": "posted"})


@tool(owner="agent", rw="write")
def bill_excess_mileage_a1b25aac(ctx: ToolContext, lease_contract_id: str, amount: float, miles_over: int) -> str:
    """Bill the excess mileage charge of a Kestrel closed-end lease whose vehicle has come back. One call books
    one end-of-term charge entry of kind excess_mileage_charge on the lease's posting history, carrying the miles
    charged, and raises the lease's end-of-term balance by the amount billed. The lessee sees the excess
    mileage charge on the lease-end account and a larger balance owed. The receipt confirms the charge entry and
    states the end-of-term balance.

    Args:
        lease_contract_id: Id class — the reference number of the lease record being billed, read from the lease
            lookup.
        amount: Fixed-format class — the excess mileage charge in USD, a positive number with 2 decimal places,
            rounded to the cent.
        miles_over: Fixed-format class — the miles charged above the mileage allowance, a non-negative integer
            count of miles.

    Returns:
        A dictionary receipt: charge_id (string, reference number of the new charge entry), lease_contract_id
        (string, the lease billed), amount (number, USD billed, 2 decimal places), miles_over (integer, miles
        charged), fee_type (string, always excess_mileage_charge), end_of_term_balance (number, USD owed on the
        lease-end account including this charge, 2 decimal places) and status (string, billed when the charge is
        on the account).
    """
    amt = round(float(amount), 2)
    miles = int(miles_over)
    rid = ctx.make_id("lmc_", lease_contract_id, amt, miles)
    lease = ctx.find("lease_contracts", lease_contract_id=lease_contract_id)
    customer_id = lease[0].get("customer_id") if lease else ""
    ctx.create("lease_transactions", rid, lease_txn_id=rid, lease_contract_id=lease_contract_id,
               customer_id=customer_id, event_type="lease_end_charge", txn_date=ctx.now()[:10], amount=amt,
               fee_type="excess_mileage_charge", miles_over=miles, payment_channel="not_applicable",
               payment_purpose="not_applicable", waiver_reason="not_applicable")
    balance = round(float((lease[0].get("end_of_term_balance") if lease else 0) or 0) + amt, 2)
    ctx.update("lease_contracts", lease_contract_id, end_of_term_balance=balance)
    return str({"charge_id": rid, "lease_contract_id": lease_contract_id, "amount": amt, "miles_over": miles,
                "fee_type": "excess_mileage_charge", "end_of_term_balance": balance, "status": "billed"})


@tool(owner="user", rw="write")
def start_lease_end_plan_44d05a38(ctx: ToolContext, lease_contract_id: str, amount: float,
                                  funding_account_last4: str) -> str:
    """The lessee pays the opening installment of a lease-end installment plan on the end-of-term balance of their
    own ended Kestrel closed-end lease through the self-service payment line, drawn by ACH from the lessee's own
    bank account. One call posts one payment entry against end-of-term charges on the lease's
    posting history and lowers the lease's end-of-term balance by the installment paid. The lessee hears a
    confirmation with the payment reference and the balance left for the remaining installments.

    Args:
        lease_contract_id: Id class — the reference number of the lessee's lease record, as given to the lessee by
            the representative from the lease lookup.
        amount: Fixed-format class — the opening installment in USD, a positive number with 2 decimal places, rounded
            to the cent.
        funding_account_last4: Fixed-format class — the last four digits of the lessee's own bank account the
            installment is drawn from, format 4 digits, or empty when the lessee names no account; the lessee
            states them.

    Returns:
        A dictionary receipt: payment_id (string, reference number of the posted installment), lease_contract_id
        (string, the lease), amount (number, USD paid, 2 decimal places), payment_channel (string, always
        phone_ivr_ach), end_of_term_balance (number, USD left owed on the lease-end account net of the
        installment, 2 decimal places), plan_status (string, enrolled when the opening installment is on the
        account).
    """
    amt = round(float(amount), 2)
    rid = ctx.make_id("lip_", lease_contract_id, amt, funding_account_last4)
    lease = ctx.find("lease_contracts", lease_contract_id=lease_contract_id)
    customer_id = lease[0].get("customer_id") if lease else ""
    ctx.create("lease_transactions", rid, lease_txn_id=rid, lease_contract_id=lease_contract_id,
               customer_id=customer_id, event_type="lease_end_of_term_payment", txn_date=ctx.now()[:10],
               amount=amt, payment_channel="phone_ivr_ach", funding_account_last4=funding_account_last4,
               payment_purpose="end_of_term_charges")
    balance = round(float((lease[0].get("end_of_term_balance") if lease else 0) or 0) - amt, 2)
    ctx.update("lease_contracts", lease_contract_id, end_of_term_balance=balance)
    return str({"payment_id": rid, "lease_contract_id": lease_contract_id, "amount": amt,
                "payment_channel": "phone_ivr_ach", "end_of_term_balance": balance, "plan_status": "enrolled"})

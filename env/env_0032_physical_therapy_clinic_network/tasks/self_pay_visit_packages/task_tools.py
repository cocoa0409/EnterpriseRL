"""Hidden task tools of the self_pay_visit_packages difficulty (Piedmont Motion Physical Therapy).

Each tool performs one atomic business write on a Self-Pay Visit Package, with the values the agent has
already worked out from the package policies; no tool checks eligibility, prerequisites or amounts.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def draft_package_installment_97c9f1d1(ctx: ToolContext, package_id: str, installment_number: int, amount: float,
                                       payment_method: str, visits_credited: int) -> str:
    """Collect one installment of a self-pay visit package that is paid in installments, on the call, and credit
    the visits that installment pays for.

    The agent records the installment payment against the package and, in the same transaction, adds the stated
    number of visits to the package's available visits. The package's amount paid rises by the amount collected
    and its visits remaining rise by the visits credited; the package history shows the installment payment
    and the visit credit tied to it. A receipt with status "installment_collected" confirms the payment is booked.

    Args:
        package_id: Id class — the visit package reference number of the package the installment belongs to, read from the visit package lookup.
        installment_number: Fixed-format class — the ordinal of the installment being collected, as a non-negative integer (count).
        amount: Fixed-format class — the money collected for this installment in USD, a positive amount with 2 decimal places, rounded to the cent.
        payment_method: Enum class — how the patient pays this installment; exactly one of: card (a credit or debit card, including the card kept on file for automatic drafts), cash (cash handed over at the clinic front desk), check (a paper check), hsa_fsa_card (a health savings or flexible spending account card).
        visits_credited: Fixed-format class — the package visits this installment adds, as a non-negative integer (visits).

    Returns:
        A dictionary rendered as text with: status ("installment_collected" on success), package_id (the package reference number), payment_event_id (reference number of the installment payment entry), credit_event_id (reference number of the visit credit entry), installment_number (integer ordinal), amount (USD, 2 decimals), visits_credited (integer visits added), amount_paid_total (the package's new amount paid in USD, 2 decimals) and visits_remaining (the package's new available visits, integer).
    """
    pkg = (ctx.find("visit_packages", package_id=package_id) or [{}])[0]
    today = ctx.now()[:10]
    pay_id = ctx.make_id("pke_", package_id, "installment", installment_number, amount, payment_method, visits_credited)
    ctx.create("package_events", pay_id, package_event_id=pay_id, package_id=package_id,
               customer_id=pkg.get("customer_id", ""), event_type="package_payment_received", event_date=today,
               payment_kind="installment", installment_number=int(installment_number),
               amount=round(float(amount), 2), payment_method=payment_method)
    cred_id = ctx.make_id("pke_", package_id, "credit", installment_number, amount, payment_method, visits_credited)
    ctx.create("package_events", cred_id, package_event_id=cred_id, package_id=package_id,
               customer_id=pkg.get("customer_id", ""), event_type="package_visits_credited", event_date=today,
               credit_kind="installment", installment_number=int(installment_number),
               visits=int(visits_credited), source_event_id=pay_id)
    paid = round(float(pkg.get("amount_paid_total") or 0) + round(float(amount), 2), 2)
    left = int(pkg.get("visits_remaining") or 0) + int(visits_credited)
    ctx.update("visit_packages", package_id, amount_paid_total=paid, visits_remaining=left)
    return str({"status": "installment_collected", "package_id": package_id, "payment_event_id": pay_id,
                "credit_event_id": cred_id, "installment_number": int(installment_number),
                "amount": round(float(amount), 2), "visits_credited": int(visits_credited),
                "amount_paid_total": paid, "visits_remaining": left})


@tool(owner="agent", rw="write")
def unfreeze_visit_package_d2f7d693(ctx: ToolContext, package_id: str, expiry_extension_days: int) -> str:
    """Lift the freeze on a frozen self-pay visit package and push its expiry date out by a stated number of days.

    The agent returns the package to active status, clears its documented freeze reason, and moves the package's
    expiry date later by exactly the number of calendar days given (zero leaves the date unchanged). The visits on
    the package can be used again at once and the patient sees the new expiry date on the package. A receipt with
    status "unfrozen" confirms the change.

    Args:
        package_id: Id class — the visit package reference number of the frozen package, read from the visit package lookup.
        expiry_extension_days: Fixed-format class — the number of calendar days the expiry date moves out, as a non-negative integer number of days.

    Returns:
        A dictionary rendered as text with: status ("unfrozen" on success), package_id (the package reference number), previous_expiry_date (YYYY-MM-DD), expiry_extension_days (integer days applied) and new_expiry_date (YYYY-MM-DD, the package's expiry date now on file).
    """
    pkg = (ctx.find("visit_packages", package_id=package_id) or [{}])[0]
    old = str(pkg.get("expiry_date") or ctx.now()[:10])[:10]
    # Calendar arithmetic on the ISO date (proleptic Gregorian day numbers), no clock involved.
    y, m, d = (int(x) for x in old.split("-"))
    y -= m <= 2
    era = (y if y >= 0 else y - 399) // 400
    yoe = y - era * 400
    doe = yoe * 365 + yoe // 4 - yoe // 100 + (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
    z = era * 146097 + doe + int(expiry_extension_days)
    era = (z if z >= 0 else z - 146096) // 146097
    doe = z - era * 146097
    yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
    doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
    mp = (5 * doy + 2) // 153
    d2 = doy - (153 * mp + 2) // 5 + 1
    m2 = mp + 3 if mp < 10 else mp - 9
    y2 = yoe + era * 400 + (m2 <= 2)
    new = f"{y2:04d}-{m2:02d}-{d2:02d}"
    ctx.update("visit_packages", package_id, status="active", expiry_date=new, freeze_reason="none")
    return str({"status": "unfrozen", "package_id": package_id, "previous_expiry_date": old,
                "expiry_extension_days": int(expiry_extension_days), "new_expiry_date": new})


@tool(owner="agent", rw="write")
def purchase_visit_package_a542d834(ctx: ToolContext, customer_id: str, variant_name: str, clinic_name: str,
                                    diagnosis_code: str, surgery_date: str, list_price: float, discount_kind: str,
                                    discount_percent: int, purchase_price: float, visits_purchased: int,
                                    expiry_date: str, payment_method: str) -> str:
    """Sell a new self-pay visit package to a patient and take its price in full at the sale.

    The agent opens the package in the patient's name, records the price terms and the Good Faith Estimate given at
    the sale (the estimate equals the purchase price), takes the full purchase price as a single payment, credits all
    of the package's visits and sets the package active with the stated expiry date. The patient holds an active
    package with all its visits available. A receipt with status "package_sold" confirms the sale.

    Args:
        customer_id: Id class — the patient reference number of the patient the package is bought for, read from the patient's records (profile lookup or a package history entry that names them).
        variant_name: Enum class — the package tier sold; exactly one of: Starter 4-Visit Package (the 4-visit tier), Recovery 6-Visit Package (the 6-visit tier), Core 8-Visit Package (the 8-visit tier), Complete 12-Visit Package (the 12-visit tier), Post-Surgical 18-Visit Package (the 18-visit tier for a patient with a surgery date and surgical protocol on file), Comprehensive 24-Visit Package (the 24-visit tier).
        clinic_name: Verbatim class — the clinic where the package is sold, copied exactly as the clinic name shown on the patient's own records, such as the patient's earlier visit package (verbatim).
        diagnosis_code: Verbatim class — the ICD-10-CM code of the condition the package is bought for, copied exactly as it appears on the patient's records for that condition (verbatim).
        surgery_date: Fixed-format class — the surgery date for a post-surgical package as YYYY-MM-DD; an empty string "" for any other tier.
        list_price: Fixed-format class — the tier's list price in USD with 2 decimal places.
        discount_kind: Enum class — the discount recorded on the package; exactly one of: none (no discount reduces the price), renewal (the renewal discount is the discount recorded), member (the Wellness Membership discount is the discount recorded).
        discount_percent: Fixed-format class — the total discount applied to the list price, in percent, integer 0-100.
        purchase_price: Fixed-format class — the price the patient pays in USD, with 2 decimal places, rounded to the cent.
        visits_purchased: Fixed-format class — the visits the tier includes, as a non-negative integer (visits).
        expiry_date: Fixed-format class — the last day the package's visits may be used, as YYYY-MM-DD.
        payment_method: Enum class — how the price is paid; exactly one of: card (a credit or debit card), cash (cash at the clinic front desk), check (a paper check), hsa_fsa_card (a health savings or flexible spending account card).

    Returns:
        A dictionary rendered as text with: status ("package_sold" on success), package_id (reference number of the new package), customer_id (the patient reference number), variant_name (tier sold), purchase_price (USD, 2 decimals), payment_event_id (reference number of the payment entry), credit_event_id (reference number of the visit credit entry), visits_remaining (integer visits available) and expiry_date (YYYY-MM-DD).
    """
    today = ctx.now()[:10]
    pkg_id = ctx.make_id("pkg_", customer_id, variant_name, clinic_name, diagnosis_code, surgery_date, list_price,
                         discount_kind, discount_percent, purchase_price, visits_purchased, expiry_date, payment_method)
    price = round(float(purchase_price), 2)
    ctx.create("visit_packages", pkg_id, package_id=pkg_id, customer_id=customer_id, variant_name=variant_name,
               status="active", opened_date=today, closed_date="", clinic_name=clinic_name,
               list_price=round(float(list_price), 2), discount_kind=discount_kind,
               discount_percent=int(discount_percent), purchase_price=price,
               visits_purchased=int(visits_purchased), installments_total=1, gfe_date=today, gfe_amount=price,
               diagnosis_code=diagnosis_code, surgery_date=surgery_date, activated_date=today,
               expiry_date=expiry_date, visits_remaining=int(visits_purchased), amount_paid_total=price,
               freeze_reason="none", freeze_start_date="", freezes_used=0, close_reason="none")
    pay_id = ctx.make_id("pke_", pkg_id, "payment")
    ctx.create("package_events", pay_id, package_event_id=pay_id, package_id=pkg_id, customer_id=customer_id,
               event_type="package_payment_received", event_date=today, payment_kind="installment",
               installment_number=1, amount=price, payment_method=payment_method)
    cred_id = ctx.make_id("pke_", pkg_id, "credit")
    ctx.create("package_events", cred_id, package_event_id=cred_id, package_id=pkg_id, customer_id=customer_id,
               event_type="package_visits_credited", event_date=today, credit_kind="installment",
               installment_number=1, visits=int(visits_purchased), source_event_id=pay_id)
    return str({"status": "package_sold", "package_id": pkg_id, "customer_id": customer_id,
                "variant_name": variant_name, "purchase_price": price, "payment_event_id": pay_id,
                "credit_event_id": cred_id, "visits_remaining": int(visits_purchased), "expiry_date": expiry_date})


@tool(owner="user", rw="write")
def transfer_package_visits_0bb17a94(ctx: ToolContext, package_id: str, recipient_customer_id: str,
                                     recipient_package_id: str, visits: int) -> str:
    """Give unused visits from your own self-pay visit package to a family or household member's package.

    The package holder moves the stated number of visits out of their package and onto the recipient's package in
    one transaction: the giving package's available visits fall by that number and the recipient's package gains
    the same number. Both package histories show the transfer, the receiving entry pointing back to the giving one.
    A receipt with status "visits_transferred" confirms the move.

    Args:
        package_id: Id class — the visit package reference number of the holder's own package the visits come from, as given by the agent.
        recipient_customer_id: Id class — the patient reference number of the family or household member receiving the visits, as given by the agent.
        recipient_package_id: Id class — the visit package reference number of the recipient's package that receives the visits, as given by the agent.
        visits: Fixed-format class — the number of visits moved, as a non-negative integer (visits).

    Returns:
        A dictionary rendered as text with: status ("visits_transferred" on success), transfer_event_id (reference number of the transfer entry on the giving package), receiving_event_id (reference number of the credit entry on the recipient's package), visits (integer visits moved), giver_visits_remaining (integer visits left on the giving package) and recipient_visits_remaining (integer visits now on the recipient's package).
    """
    giver = (ctx.find("visit_packages", package_id=package_id) or [{}])[0]
    recip = (ctx.find("visit_packages", package_id=recipient_package_id) or [{}])[0]
    today = ctx.now()[:10]
    out_id = ctx.make_id("pke_", package_id, "transfer", recipient_customer_id, recipient_package_id, visits)
    ctx.create("package_events", out_id, package_event_id=out_id, package_id=package_id,
               customer_id=giver.get("customer_id", ""), event_type="package_visits_transferred", event_date=today,
               visits=int(visits), recipient_customer_id=recipient_customer_id)
    in_id = ctx.make_id("pke_", recipient_package_id, "transfer_in", out_id)
    ctx.create("package_events", in_id, package_event_id=in_id, package_id=recipient_package_id,
               customer_id=recipient_customer_id, event_type="package_visits_credited", event_date=today,
               credit_kind="transfer_in", installment_number=0, visits=int(visits), source_event_id=out_id)
    g_left = int(giver.get("visits_remaining") or 0) - int(visits)
    r_left = int(recip.get("visits_remaining") or 0) + int(visits)
    ctx.update("visit_packages", package_id, visits_remaining=g_left)
    ctx.update("visit_packages", recipient_package_id, visits_remaining=r_left)
    return str({"status": "visits_transferred", "transfer_event_id": out_id, "receiving_event_id": in_id,
                "visits": int(visits), "giver_visits_remaining": g_left, "recipient_visits_remaining": r_left})


@tool(owner="agent", rw="write")
def reinstate_visit_package_76109996(ctx: ToolContext, package_id: str, reinstatement_fee: float, payment_method: str,
                                     visits_restored: int, new_expiry_date: str) -> str:
    """Reinstate an expired self-pay visit package against the reinstatement charge the patient pays on the call.

    The agent takes the reinstatement charge as a reinstatement-fee payment on the package, credits back the stated
    number of visits that the expiry removed, returns the package to active status with its closing details cleared,
    and sets its new expiry date. The patient sees the package active again with the restored visits and the new
    expiry date. A receipt with status "reinstated" confirms the reinstatement.

    Args:
        package_id: Id class — the visit package reference number of the expired package, read from the visit package lookup.
        reinstatement_fee: Fixed-format class — the reinstatement charge collected in USD, with 2 decimal places, rounded to the cent.
        payment_method: Enum class — how the patient pays the charge; exactly one of: card (a credit or debit card), cash (cash at the clinic front desk), check (a paper check), hsa_fsa_card (a health savings or flexible spending account card).
        visits_restored: Fixed-format class — the visits credited back to the package, as a non-negative integer (visits).
        new_expiry_date: Fixed-format class — the package's new last day of use, as YYYY-MM-DD.

    Returns:
        A dictionary rendered as text with: status ("reinstated" on success), package_id (the package reference number), payment_event_id (reference number of the reinstatement-fee payment entry), credit_event_id (reference number of the visit credit entry), reinstatement_fee (USD, 2 decimals), visits_remaining (integer visits now available) and expiry_date (YYYY-MM-DD).
    """
    pkg = (ctx.find("visit_packages", package_id=package_id) or [{}])[0]
    today = ctx.now()[:10]
    fee = round(float(reinstatement_fee), 2)
    pay_id = ctx.make_id("pke_", package_id, "reinstatement_fee", reinstatement_fee, payment_method, visits_restored,
                         new_expiry_date)
    ctx.create("package_events", pay_id, package_event_id=pay_id, package_id=package_id,
               customer_id=pkg.get("customer_id", ""), event_type="package_payment_received", event_date=today,
               payment_kind="reinstatement_fee", installment_number=0, amount=fee, payment_method=payment_method)
    cred_id = ctx.make_id("pke_", package_id, "reinstatement_credit", reinstatement_fee, payment_method,
                          visits_restored, new_expiry_date)
    ctx.create("package_events", cred_id, package_event_id=cred_id, package_id=package_id,
               customer_id=pkg.get("customer_id", ""), event_type="package_visits_credited", event_date=today,
               credit_kind="reinstatement", installment_number=0, visits=int(visits_restored))
    left = int(pkg.get("visits_remaining") or 0) + int(visits_restored)
    paid = round(float(pkg.get("amount_paid_total") or 0) + fee, 2)
    ctx.update("visit_packages", package_id, status="active", expiry_date=new_expiry_date, closed_date="",
               close_reason="none", visits_remaining=left, amount_paid_total=paid)
    return str({"status": "reinstated", "package_id": package_id, "payment_event_id": pay_id,
                "credit_event_id": cred_id, "reinstatement_fee": fee, "visits_remaining": left,
                "expiry_date": new_expiry_date})


@tool(owner="user", rw="write")
def confirm_package_cancellation_a8d08ce2(ctx: ToolContext, package_id: str, refund_amount: float,
                                          visits_unused: int) -> str:
    """Confirm, as the package holder, the cancellation of your own self-pay visit package for a refund.

    The patient's confirmation records a confirmed refund request for the stated refund amount and unused visits,
    cancels the package and removes its unused visits. The package shows as cancelled for a refund and the
    request shows as confirmed by the patient. A receipt with status "cancellation_confirmed" confirms it.

    Args:
        package_id: Id class — the visit package reference number of the package being cancelled, as given by the agent.
        refund_amount: Fixed-format class — the refund amount confirmed in USD, with 2 decimal places, rounded to the cent.
        visits_unused: Fixed-format class — the unused visits removed from the package, as a non-negative integer (visits).

    Returns:
        A dictionary rendered as text with: status ("cancellation_confirmed" on success), refund_request_id (reference number of the confirmed refund request), package_id (the package reference number), refund_amount (USD, 2 decimals), visits_unused (integer) and closed_date (YYYY-MM-DD, the cancellation date).
    """
    pkg = (ctx.find("visit_packages", package_id=package_id) or [{}])[0]
    today = ctx.now()[:10]
    amt = round(float(refund_amount), 2)
    req_id = ctx.make_id("prr_", package_id, refund_amount, visits_unused)
    ctx.create("package_refund_requests", req_id, refund_request_id=req_id, customer_id=pkg.get("customer_id", ""),
               package_id=package_id, request_date=today, visits_unused=int(visits_unused), refund_amount=amt,
               request_status="patient_confirmed", created_at=ctx.now())
    ev_id = ctx.make_id("pke_", package_id, "visits_refunded", refund_amount, visits_unused)
    ctx.create("package_events", ev_id, package_event_id=ev_id, package_id=package_id,
               customer_id=pkg.get("customer_id", ""), event_type="package_visits_refunded", event_date=today,
               visits=int(visits_unused))
    left = int(pkg.get("visits_remaining") or 0) - int(visits_unused)
    ctx.update("visit_packages", package_id, status="cancelled", closed_date=today, close_reason="refunded",
               visits_remaining=left)
    return str({"status": "cancellation_confirmed", "refund_request_id": req_id, "package_id": package_id,
                "refund_amount": amt, "visits_unused": int(visits_unused), "closed_date": today})

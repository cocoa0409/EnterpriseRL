"""Hidden task tools of the vision_member_services difficulty (Cascade Mutual Dental & Vision).

The agent tools record Cascade's decision on one claim of a member's enrollment (an exam visit, an
eyeglasses order, a contact-lens order or a stand-alone fitting); the member tools record the member's own
new out-of-network claim. The tools judge nothing: the remark of each denied line and the amount are worked out from the
published vision rules and passed in as fixed values.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def decide_exam_visit_80d2e33d(ctx: ToolContext, claim_number: str, plan_paid: float, exam_remark: str = "", fitting_remark: str = "") -> str:
    """Record Cascade's decision on the exam visit (the routine eye exam and any contact-lens fitting of one claim) carrying the claim number, its open routine eye exam line and, on a claim without a contact-lens line, its open fitting line (lines carrying no remark yet or standing denied as not eligible; the claim's other lines are left as they are) at once: each line given a remark
    argument receives that denial remark, every other line receives the paid remark of its channel (PAID at a
    participating location, PAID_OON_REIMBURSEMENT at a provider without a Cascade agreement), the amount is
    booked on the first line not denied in the order exam, fitting, contact lenses, lenses, frame (the first line
    when every line is denied) with no separate amount on the other lines, and every line's decision date is set to today. After the call the claim's lines show these
    remarks and the amount on the member's claim history, which is the observable sign of success.

    Args:
        claim_number: Verbatim class — the claim number of the claim, copied character for character from the vision claim lookup, with its letters, digits and hyphens unchanged (verbatim).
        plan_paid: Fixed-format class — the amount Cascade pays for the whole visit, 0.00 when the plan pays nothing, in USD, a non-negative number given to 2 decimal places (cents), rounded half up to the cent.
        exam_remark: Enum class — the denial remark recorded on the claim's routine eye exam line: DENIED_FREQUENCY when the line's benefit is not available again under the frequency rule, DENIED_CONTACTS_IN_LIEU when the line is left out because the other materials hold the benefit (contacts in lieu of glasses), DENIED_NOT_COVERED when the plan carries no benefit for the line, DENIED_NOT_ELIGIBLE when the enrollment does not cover the line's date of service, DENIED_TIMELY_FILING when the claim reached Cascade after the filing limit; an empty text when the claim carries no such line or the line is paid or reimbursed.
        fitting_remark: Enum class — the denial remark recorded on the claim's contact-lens fitting line: DENIED_FREQUENCY when the line's benefit is not available again under the frequency rule, DENIED_CONTACTS_IN_LIEU when the line is left out because the other materials hold the benefit (contacts in lieu of glasses), DENIED_NOT_COVERED when the plan carries no benefit for the line, DENIED_NOT_ELIGIBLE when the enrollment does not cover the line's date of service, DENIED_TIMELY_FILING when the claim reached Cascade after the filing limit; an empty text when the claim carries no such line or the line is paid or reimbursed.

    Returns:
        A dictionary rendered as text with: claim_number (the claim recorded), plan_paid (the amount booked, USD with 2 decimal places), lines (for each line recorded, its reference number mapped to the remark now recorded) and adjudicated_date (today's date, YYYY-MM-DD); a returned dictionary means the claim is recorded, while a text starting "No open claim line" means no open line carries that claim number.
    """
    rows = [r for r in ctx.find("vision_claims", claim_number=claim_number) if r.get("remark_code", "") in ("", "DENIED_NOT_ELIGIBLE")]
    if not rows:
        return f"No open claim line carries claim number {claim_number}."
    names = {"vision_contacts_claim": "contact_lenses", "vision_lens_claim": "lenses", "vision_frame_claim": "frame"}
    denied = {k: v for k, v in (("exam", exam_remark), ("fitting", fitting_remark)) if v}
    amount = round(float(plan_paid), 2)
    today = ctx.now()[:10]
    ordered = []
    for k in ["exam", "fitting", "contact_lenses", "lenses", "frame"]:
        for r in rows:
            et = r["event_type"]
            kind = ("exam" if r.get("exam_type", "") == "routine_eye_exam" else "fitting") if et == "vision_exam_claim" else names.get(et, "")
            if kind == k:
                ordered.append((k, r))
    kinds_all = {(("exam" if x.get("exam_type", "") == "routine_eye_exam" else "fitting") if x["event_type"] == "vision_exam_claim" else names.get(x["event_type"], "")) for x in ctx.find("vision_claims", claim_number=claim_number)}
    ordered = [(k, r) for k, r in ordered if k == "exam" or (k == "fitting" and "contact_lenses" not in kinds_all)]
    if not ordered:
        return f"No open claim line carries claim number {claim_number}."
    target = next((r["vision_claim_id"] for k, r in ordered if k not in denied), ordered[0][1]["vision_claim_id"] if ordered else "")
    out = {}
    for k, r in ordered:
        remark = denied.get(k, "PAID_OON_REIMBURSEMENT" if r.get("network_channel", "") == "out_of_network" else "PAID")
        ctx.update("vision_claims", r["vision_claim_id"], remark_code=remark, plan_paid=(amount if r["vision_claim_id"] == target else 0.0), adjudicated_date=today)
        out[r["vision_claim_id"]] = remark
    return str({"claim_number": claim_number, "plan_paid": amount, "lines": out, "adjudicated_date": today})


@tool(owner="agent", rw="write")
def decide_eyeglasses_order_e7a7f40f(ctx: ToolContext, claim_number: str, member_paid: float, lenses_remark: str = "", frame_remark: str = "") -> str:
    """Record Cascade's decision on the eyeglasses order (the spectacle lenses and frame of one claim) carrying the claim number, its open spectacle-lens and frame lines (lines carrying no remark yet or standing denied as not eligible; the claim's other lines are left as they are) at once: each line given a remark
    argument receives that denial remark, every other line receives the paid remark of its channel (PAID at a
    participating location, PAID_OON_REIMBURSEMENT at a provider without a Cascade agreement), the amount is
    booked on the first line not denied in the order exam, fitting, contact lenses, lenses, frame (the first line
    when every line is denied) with no separate amount on the other lines, and every line's decision date is set to today. After the call the claim's lines show these
    remarks and the amount on the member's claim history, which is the observable sign of success.

    Args:
        claim_number: Verbatim class — the claim number of the claim, copied character for character from the vision claim lookup, with its letters, digits and hyphens unchanged (verbatim).
        member_paid: Fixed-format class — the amount the member pays for the whole order, in USD, a non-negative number given to 2 decimal places (cents), rounded half up to the cent.
        lenses_remark: Enum class — the denial remark recorded on the claim's spectacle-lens line: DENIED_FREQUENCY when the line's benefit is not available again under the frequency rule, DENIED_CONTACTS_IN_LIEU when the line is left out because the other materials hold the benefit (contacts in lieu of glasses), DENIED_NOT_COVERED when the plan carries no benefit for the line, DENIED_NOT_ELIGIBLE when the enrollment does not cover the line's date of service, DENIED_TIMELY_FILING when the claim reached Cascade after the filing limit; an empty text when the claim carries no such line or the line is paid or reimbursed.
        frame_remark: Enum class — the denial remark recorded on the claim's frame line: DENIED_FREQUENCY when the line's benefit is not available again under the frequency rule, DENIED_CONTACTS_IN_LIEU when the line is left out because the other materials hold the benefit (contacts in lieu of glasses), DENIED_NOT_COVERED when the plan carries no benefit for the line, DENIED_NOT_ELIGIBLE when the enrollment does not cover the line's date of service, DENIED_TIMELY_FILING when the claim reached Cascade after the filing limit; an empty text when the claim carries no such line or the line is paid or reimbursed.

    Returns:
        A dictionary rendered as text with: claim_number (the claim recorded), member_paid (the amount booked, USD with 2 decimal places), lines (for each line recorded, its reference number mapped to the remark now recorded) and adjudicated_date (today's date, YYYY-MM-DD); a returned dictionary means the claim is recorded, while a text starting "No open claim line" means no open line carries that claim number.
    """
    rows = [r for r in ctx.find("vision_claims", claim_number=claim_number) if r.get("remark_code", "") in ("", "DENIED_NOT_ELIGIBLE")]
    if not rows:
        return f"No open claim line carries claim number {claim_number}."
    names = {"vision_contacts_claim": "contact_lenses", "vision_lens_claim": "lenses", "vision_frame_claim": "frame"}
    denied = {k: v for k, v in (("lenses", lenses_remark), ("frame", frame_remark)) if v}
    amount = round(float(member_paid), 2)
    today = ctx.now()[:10]
    ordered = []
    for k in ["exam", "fitting", "contact_lenses", "lenses", "frame"]:
        for r in rows:
            et = r["event_type"]
            kind = ("exam" if r.get("exam_type", "") == "routine_eye_exam" else "fitting") if et == "vision_exam_claim" else names.get(et, "")
            if kind == k:
                ordered.append((k, r))
    kinds_all = {(("exam" if x.get("exam_type", "") == "routine_eye_exam" else "fitting") if x["event_type"] == "vision_exam_claim" else names.get(x["event_type"], "")) for x in ctx.find("vision_claims", claim_number=claim_number)}
    ordered = [(k, r) for k, r in ordered if k in ("lenses", "frame")]
    if not ordered:
        return f"No open claim line carries claim number {claim_number}."
    target = next((r["vision_claim_id"] for k, r in ordered if k not in denied), ordered[0][1]["vision_claim_id"] if ordered else "")
    out = {}
    for k, r in ordered:
        remark = denied.get(k, "PAID_OON_REIMBURSEMENT" if r.get("network_channel", "") == "out_of_network" else "PAID")
        ctx.update("vision_claims", r["vision_claim_id"], remark_code=remark, member_paid=(amount if r["vision_claim_id"] == target else 0.0), adjudicated_date=today)
        out[r["vision_claim_id"]] = remark
    return str({"claim_number": claim_number, "member_paid": amount, "lines": out, "adjudicated_date": today})


@tool(owner="agent", rw="write")
def decide_contacts_order_55f7002b(ctx: ToolContext, claim_number: str, member_paid: float, fitting_remark: str = "", contact_lenses_remark: str = "") -> str:
    """Record Cascade's decision on the contact-lens order (the contact lenses and any contact-lens fitting of one claim) carrying the claim number, its open contact-lens and fitting lines (lines carrying no remark yet or standing denied as not eligible; the claim's other lines are left as they are) at once: each line given a remark
    argument receives that denial remark, every other line receives the paid remark of its channel (PAID at a
    participating location, PAID_OON_REIMBURSEMENT at a provider without a Cascade agreement), the amount is
    booked on the first line not denied in the order exam, fitting, contact lenses, lenses, frame (the first line
    when every line is denied) with no separate amount on the other lines, and every line's decision date is set to today. After the call the claim's lines show these
    remarks and the amount on the member's claim history, which is the observable sign of success.

    Args:
        claim_number: Verbatim class — the claim number of the claim, copied character for character from the vision claim lookup, with its letters, digits and hyphens unchanged (verbatim).
        member_paid: Fixed-format class — the amount the member pays for the whole order, in USD, a non-negative number given to 2 decimal places (cents), rounded half up to the cent.
        fitting_remark: Enum class — the denial remark recorded on the claim's contact-lens fitting line: DENIED_FREQUENCY when the line's benefit is not available again under the frequency rule, DENIED_CONTACTS_IN_LIEU when the line is left out because the other materials hold the benefit (contacts in lieu of glasses), DENIED_NOT_COVERED when the plan carries no benefit for the line, DENIED_NOT_ELIGIBLE when the enrollment does not cover the line's date of service, DENIED_TIMELY_FILING when the claim reached Cascade after the filing limit; an empty text when the claim carries no such line or the line is paid or reimbursed.
        contact_lenses_remark: Enum class — the denial remark recorded on the claim's contact-lens line: DENIED_FREQUENCY when the line's benefit is not available again under the frequency rule, DENIED_CONTACTS_IN_LIEU when the line is left out because the other materials hold the benefit (contacts in lieu of glasses), DENIED_NOT_COVERED when the plan carries no benefit for the line, DENIED_NOT_ELIGIBLE when the enrollment does not cover the line's date of service, DENIED_TIMELY_FILING when the claim reached Cascade after the filing limit; an empty text when the claim carries no such line or the line is paid or reimbursed.

    Returns:
        A dictionary rendered as text with: claim_number (the claim recorded), member_paid (the amount booked, USD with 2 decimal places), lines (for each line recorded, its reference number mapped to the remark now recorded) and adjudicated_date (today's date, YYYY-MM-DD); a returned dictionary means the claim is recorded, while a text starting "No open claim line" means no open line carries that claim number.
    """
    rows = [r for r in ctx.find("vision_claims", claim_number=claim_number) if r.get("remark_code", "") in ("", "DENIED_NOT_ELIGIBLE")]
    if not rows:
        return f"No open claim line carries claim number {claim_number}."
    names = {"vision_contacts_claim": "contact_lenses", "vision_lens_claim": "lenses", "vision_frame_claim": "frame"}
    denied = {k: v for k, v in (("fitting", fitting_remark), ("contact_lenses", contact_lenses_remark)) if v}
    amount = round(float(member_paid), 2)
    today = ctx.now()[:10]
    ordered = []
    for k in ["exam", "fitting", "contact_lenses", "lenses", "frame"]:
        for r in rows:
            et = r["event_type"]
            kind = ("exam" if r.get("exam_type", "") == "routine_eye_exam" else "fitting") if et == "vision_exam_claim" else names.get(et, "")
            if kind == k:
                ordered.append((k, r))
    kinds_all = {(("exam" if x.get("exam_type", "") == "routine_eye_exam" else "fitting") if x["event_type"] == "vision_exam_claim" else names.get(x["event_type"], "")) for x in ctx.find("vision_claims", claim_number=claim_number)}
    ordered = [(k, r) for k, r in ordered if k in ("contact_lenses", "fitting")]
    if not ordered:
        return f"No open claim line carries claim number {claim_number}."
    target = next((r["vision_claim_id"] for k, r in ordered if k not in denied), ordered[0][1]["vision_claim_id"] if ordered else "")
    out = {}
    for k, r in ordered:
        remark = denied.get(k, "PAID_OON_REIMBURSEMENT" if r.get("network_channel", "") == "out_of_network" else "PAID")
        ctx.update("vision_claims", r["vision_claim_id"], remark_code=remark, member_paid=(amount if r["vision_claim_id"] == target else 0.0), adjudicated_date=today)
        out[r["vision_claim_id"]] = remark
    return str({"claim_number": claim_number, "member_paid": amount, "lines": out, "adjudicated_date": today})


@tool(owner="agent", rw="write")
def decide_contact_fitting_9468302b(ctx: ToolContext, claim_number: str, member_paid: float, fitting_remark: str = "") -> str:
    """Record Cascade's decision on the stand-alone contact-lens fitting claim carrying the claim number, its open fitting line when the claim carries neither a routine eye exam line nor a contact-lens line (lines carrying no remark yet or standing denied as not eligible) at once: each line given a remark
    argument receives that denial remark, every other line receives the paid remark of its channel (PAID at a
    participating location, PAID_OON_REIMBURSEMENT at a provider without a Cascade agreement), the amount is
    booked on the first line not denied in the order exam, fitting, contact lenses, lenses, frame (the first line
    when every line is denied) with no separate amount on the other lines, and every line's decision date is set to today. After the call the claim's lines show these
    remarks and the amount on the member's claim history, which is the observable sign of success.

    Args:
        claim_number: Verbatim class — the claim number of the claim, copied character for character from the vision claim lookup, with its letters, digits and hyphens unchanged (verbatim).
        member_paid: Fixed-format class — the amount the member pays for the fitting, in USD, a non-negative number given to 2 decimal places (cents), rounded half up to the cent.
        fitting_remark: Enum class — the denial remark recorded on the claim's contact-lens fitting line: DENIED_FREQUENCY when the line's benefit is not available again under the frequency rule, DENIED_CONTACTS_IN_LIEU when the line is left out because the other materials hold the benefit (contacts in lieu of glasses), DENIED_NOT_COVERED when the plan carries no benefit for the line, DENIED_NOT_ELIGIBLE when the enrollment does not cover the line's date of service, DENIED_TIMELY_FILING when the claim reached Cascade after the filing limit; an empty text when the claim carries no such line or the line is paid or reimbursed.

    Returns:
        A dictionary rendered as text with: claim_number (the claim recorded), member_paid (the amount booked, USD with 2 decimal places), lines (for each line recorded, its reference number mapped to the remark now recorded) and adjudicated_date (today's date, YYYY-MM-DD); a returned dictionary means the claim is recorded, while a text starting "No open claim line" means no open line carries that claim number.
    """
    rows = [r for r in ctx.find("vision_claims", claim_number=claim_number) if r.get("remark_code", "") in ("", "DENIED_NOT_ELIGIBLE")]
    if not rows:
        return f"No open claim line carries claim number {claim_number}."
    names = {"vision_contacts_claim": "contact_lenses", "vision_lens_claim": "lenses", "vision_frame_claim": "frame"}
    denied = {k: v for k, v in (("fitting", fitting_remark),) if v}
    amount = round(float(member_paid), 2)
    today = ctx.now()[:10]
    ordered = []
    for k in ["exam", "fitting", "contact_lenses", "lenses", "frame"]:
        for r in rows:
            et = r["event_type"]
            kind = ("exam" if r.get("exam_type", "") == "routine_eye_exam" else "fitting") if et == "vision_exam_claim" else names.get(et, "")
            if kind == k:
                ordered.append((k, r))
    kinds_all = {(("exam" if x.get("exam_type", "") == "routine_eye_exam" else "fitting") if x["event_type"] == "vision_exam_claim" else names.get(x["event_type"], "")) for x in ctx.find("vision_claims", claim_number=claim_number)}
    ordered = [(k, r) for k, r in ordered if k == "fitting" and "exam" not in kinds_all and "contact_lenses" not in kinds_all]
    if not ordered:
        return f"No open claim line carries claim number {claim_number}."
    target = next((r["vision_claim_id"] for k, r in ordered if k not in denied), ordered[0][1]["vision_claim_id"] if ordered else "")
    out = {}
    for k, r in ordered:
        remark = denied.get(k, "PAID_OON_REIMBURSEMENT" if r.get("network_channel", "") == "out_of_network" else "PAID")
        ctx.update("vision_claims", r["vision_claim_id"], remark_code=remark, member_paid=(amount if r["vision_claim_id"] == target else 0.0), adjudicated_date=today)
        out[r["vision_claim_id"]] = remark
    return str({"claim_number": claim_number, "member_paid": amount, "lines": out, "adjudicated_date": today})


@tool(owner="user", rw="write")
def file_oon_eyeglass_claim_2513bc70(ctx: ToolContext, claim_number: str, plan_paid: float, exam_remark: str = "", fitting_remark: str = "", contact_lenses_remark: str = "", lenses_remark: str = "", frame_remark: str = "") -> str:
    """The member files their own new out-of-network claim settled on its glasses part (a claim whose spectacle-lens and frame receipts together are at least its contact-lens and fitting receipts together) carrying the claim number, all of its open lines (lines carrying no remark yet) at once: each line given a remark
    argument receives that denial remark, every other line receives the paid remark of its channel (PAID at a
    participating location, PAID_OON_REIMBURSEMENT at a provider without a Cascade agreement), the amount is
    booked on the first line not denied in the order exam, fitting, contact lenses, lenses, frame (the first line
    when every line is denied) with no separate amount on the other lines, and every line's decision date is set to today. After the call the claim's lines show these
    remarks and the amount on the member's claim history, which is the observable sign of success.

    Args:
        claim_number: Verbatim class — the claim number of the claim, copied character for character from the vision claim lookup, with its letters, digits and hyphens unchanged (verbatim).
        plan_paid: Fixed-format class — the claim's total reimbursement the member files for, as stated to the member by the agent, in USD, a non-negative number given to 2 decimal places (cents), rounded half up to the cent.
        exam_remark: Enum class — the denial remark recorded on the claim's routine eye exam line: DENIED_FREQUENCY when the line's benefit is not available again under the frequency rule, DENIED_CONTACTS_IN_LIEU when the line is left out because the other materials hold the benefit (contacts in lieu of glasses), DENIED_NOT_COVERED when the plan carries no benefit for the line, DENIED_NOT_ELIGIBLE when the enrollment does not cover the line's date of service, DENIED_TIMELY_FILING when the claim reached Cascade after the filing limit; an empty text when the claim carries no such line or the line is paid or reimbursed.
        fitting_remark: Enum class — the denial remark recorded on the claim's contact-lens fitting line: DENIED_FREQUENCY when the line's benefit is not available again under the frequency rule, DENIED_CONTACTS_IN_LIEU when the line is left out because the other materials hold the benefit (contacts in lieu of glasses), DENIED_NOT_COVERED when the plan carries no benefit for the line, DENIED_NOT_ELIGIBLE when the enrollment does not cover the line's date of service, DENIED_TIMELY_FILING when the claim reached Cascade after the filing limit; an empty text when the claim carries no such line or the line is paid or reimbursed.
        contact_lenses_remark: Enum class — the denial remark recorded on the claim's contact-lens line: DENIED_FREQUENCY when the line's benefit is not available again under the frequency rule, DENIED_CONTACTS_IN_LIEU when the line is left out because the other materials hold the benefit (contacts in lieu of glasses), DENIED_NOT_COVERED when the plan carries no benefit for the line, DENIED_NOT_ELIGIBLE when the enrollment does not cover the line's date of service, DENIED_TIMELY_FILING when the claim reached Cascade after the filing limit; an empty text when the claim carries no such line or the line is paid or reimbursed.
        lenses_remark: Enum class — the denial remark recorded on the claim's spectacle-lens line: DENIED_FREQUENCY when the line's benefit is not available again under the frequency rule, DENIED_CONTACTS_IN_LIEU when the line is left out because the other materials hold the benefit (contacts in lieu of glasses), DENIED_NOT_COVERED when the plan carries no benefit for the line, DENIED_NOT_ELIGIBLE when the enrollment does not cover the line's date of service, DENIED_TIMELY_FILING when the claim reached Cascade after the filing limit; an empty text when the claim carries no such line or the line is paid or reimbursed.
        frame_remark: Enum class — the denial remark recorded on the claim's frame line: DENIED_FREQUENCY when the line's benefit is not available again under the frequency rule, DENIED_CONTACTS_IN_LIEU when the line is left out because the other materials hold the benefit (contacts in lieu of glasses), DENIED_NOT_COVERED when the plan carries no benefit for the line, DENIED_NOT_ELIGIBLE when the enrollment does not cover the line's date of service, DENIED_TIMELY_FILING when the claim reached Cascade after the filing limit; an empty text when the claim carries no such line or the line is paid or reimbursed.

    Returns:
        A dictionary rendered as text with: claim_number (the claim recorded), plan_paid (the amount booked, USD with 2 decimal places), lines (for each line recorded, its reference number mapped to the remark now recorded) and adjudicated_date (today's date, YYYY-MM-DD); a returned dictionary means the claim is recorded, while a text starting "No open claim line" means no open line carries that claim number; a text starting "Not settled on its glasses part" means the claim's contact-lens and fitting receipts exceed its spectacle-lens and frame receipts and nothing was recorded.
    """
    rows = [r for r in ctx.find("vision_claims", claim_number=claim_number) if r.get("remark_code", "") in ("",)]
    if not rows:
        return f"No open claim line carries claim number {claim_number}."
    claim_rows = ctx.find("vision_claims", claim_number=claim_number)
    glasses_receipts = sum(float(x.get("retail_charge") or 0) for x in claim_rows if x["event_type"] in ("vision_lens_claim", "vision_frame_claim"))
    contact_receipts = sum(float(x.get("retail_charge") or 0) for x in claim_rows if x["event_type"] == "vision_contacts_claim" or (x["event_type"] == "vision_exam_claim" and x.get("exam_type", "") in ("contact_lens_fitting_specialty", "contact_lens_fitting_standard")))
    if contact_receipts > glasses_receipts:
        return f"Not settled on its glasses part: the contact-lens and fitting receipts of claim {claim_number} exceed its spectacle-lens and frame receipts."
    names = {"vision_contacts_claim": "contact_lenses", "vision_lens_claim": "lenses", "vision_frame_claim": "frame"}
    denied = {k: v for k, v in (("exam", exam_remark), ("fitting", fitting_remark), ("contact_lenses", contact_lenses_remark), ("lenses", lenses_remark), ("frame", frame_remark)) if v}
    amount = round(float(plan_paid), 2)
    today = ctx.now()[:10]
    ordered = []
    for k in ["exam", "fitting", "contact_lenses", "lenses", "frame"]:
        for r in rows:
            et = r["event_type"]
            kind = ("exam" if r.get("exam_type", "") == "routine_eye_exam" else "fitting") if et == "vision_exam_claim" else names.get(et, "")
            if kind == k:
                ordered.append((k, r))
    target = next((r["vision_claim_id"] for k, r in ordered if k not in denied), ordered[0][1]["vision_claim_id"] if ordered else "")
    out = {}
    for k, r in ordered:
        remark = denied.get(k, "PAID_OON_REIMBURSEMENT" if r.get("network_channel", "") == "out_of_network" else "PAID")
        ctx.update("vision_claims", r["vision_claim_id"], remark_code=remark, plan_paid=(amount if r["vision_claim_id"] == target else 0.0), adjudicated_date=today)
        out[r["vision_claim_id"]] = remark
    return str({"claim_number": claim_number, "plan_paid": amount, "lines": out, "adjudicated_date": today})


@tool(owner="user", rw="write")
def file_oon_contact_lens_claim_04f2b50e(ctx: ToolContext, claim_number: str, plan_paid: float, exam_remark: str = "", fitting_remark: str = "", contact_lenses_remark: str = "", lenses_remark: str = "", frame_remark: str = "") -> str:
    """The member files their own new out-of-network claim settled on its contact-lens part (a claim whose contact-lens and fitting receipts together exceed its spectacle-lens and frame receipts together) carrying the claim number, all of its open lines (lines carrying no remark yet) at once: each line given a remark
    argument receives that denial remark, every other line receives the paid remark of its channel (PAID at a
    participating location, PAID_OON_REIMBURSEMENT at a provider without a Cascade agreement), the amount is
    booked on the first line not denied in the order exam, fitting, contact lenses, lenses, frame (the first line
    when every line is denied) with no separate amount on the other lines, and every line's decision date is set to today. After the call the claim's lines show these
    remarks and the amount on the member's claim history, which is the observable sign of success.

    Args:
        claim_number: Verbatim class — the claim number of the claim, copied character for character from the vision claim lookup, with its letters, digits and hyphens unchanged (verbatim).
        plan_paid: Fixed-format class — the claim's total reimbursement the member files for, as stated to the member by the agent, in USD, a non-negative number given to 2 decimal places (cents), rounded half up to the cent.
        exam_remark: Enum class — the denial remark recorded on the claim's routine eye exam line: DENIED_FREQUENCY when the line's benefit is not available again under the frequency rule, DENIED_CONTACTS_IN_LIEU when the line is left out because the other materials hold the benefit (contacts in lieu of glasses), DENIED_NOT_COVERED when the plan carries no benefit for the line, DENIED_NOT_ELIGIBLE when the enrollment does not cover the line's date of service, DENIED_TIMELY_FILING when the claim reached Cascade after the filing limit; an empty text when the claim carries no such line or the line is paid or reimbursed.
        fitting_remark: Enum class — the denial remark recorded on the claim's contact-lens fitting line: DENIED_FREQUENCY when the line's benefit is not available again under the frequency rule, DENIED_CONTACTS_IN_LIEU when the line is left out because the other materials hold the benefit (contacts in lieu of glasses), DENIED_NOT_COVERED when the plan carries no benefit for the line, DENIED_NOT_ELIGIBLE when the enrollment does not cover the line's date of service, DENIED_TIMELY_FILING when the claim reached Cascade after the filing limit; an empty text when the claim carries no such line or the line is paid or reimbursed.
        contact_lenses_remark: Enum class — the denial remark recorded on the claim's contact-lens line: DENIED_FREQUENCY when the line's benefit is not available again under the frequency rule, DENIED_CONTACTS_IN_LIEU when the line is left out because the other materials hold the benefit (contacts in lieu of glasses), DENIED_NOT_COVERED when the plan carries no benefit for the line, DENIED_NOT_ELIGIBLE when the enrollment does not cover the line's date of service, DENIED_TIMELY_FILING when the claim reached Cascade after the filing limit; an empty text when the claim carries no such line or the line is paid or reimbursed.
        lenses_remark: Enum class — the denial remark recorded on the claim's spectacle-lens line: DENIED_FREQUENCY when the line's benefit is not available again under the frequency rule, DENIED_CONTACTS_IN_LIEU when the line is left out because the other materials hold the benefit (contacts in lieu of glasses), DENIED_NOT_COVERED when the plan carries no benefit for the line, DENIED_NOT_ELIGIBLE when the enrollment does not cover the line's date of service, DENIED_TIMELY_FILING when the claim reached Cascade after the filing limit; an empty text when the claim carries no such line or the line is paid or reimbursed.
        frame_remark: Enum class — the denial remark recorded on the claim's frame line: DENIED_FREQUENCY when the line's benefit is not available again under the frequency rule, DENIED_CONTACTS_IN_LIEU when the line is left out because the other materials hold the benefit (contacts in lieu of glasses), DENIED_NOT_COVERED when the plan carries no benefit for the line, DENIED_NOT_ELIGIBLE when the enrollment does not cover the line's date of service, DENIED_TIMELY_FILING when the claim reached Cascade after the filing limit; an empty text when the claim carries no such line or the line is paid or reimbursed.

    Returns:
        A dictionary rendered as text with: claim_number (the claim recorded), plan_paid (the amount booked, USD with 2 decimal places), lines (for each line recorded, its reference number mapped to the remark now recorded) and adjudicated_date (today's date, YYYY-MM-DD); a returned dictionary means the claim is recorded, while a text starting "No open claim line" means no open line carries that claim number; a text starting "Not settled on its contact-lens part" means the claim's spectacle-lens and frame receipts are at least its contact-lens and fitting receipts and nothing was recorded.
    """
    rows = [r for r in ctx.find("vision_claims", claim_number=claim_number) if r.get("remark_code", "") in ("",)]
    if not rows:
        return f"No open claim line carries claim number {claim_number}."
    claim_rows = ctx.find("vision_claims", claim_number=claim_number)
    glasses_receipts = sum(float(x.get("retail_charge") or 0) for x in claim_rows if x["event_type"] in ("vision_lens_claim", "vision_frame_claim"))
    contact_receipts = sum(float(x.get("retail_charge") or 0) for x in claim_rows if x["event_type"] == "vision_contacts_claim" or (x["event_type"] == "vision_exam_claim" and x.get("exam_type", "") in ("contact_lens_fitting_specialty", "contact_lens_fitting_standard")))
    if glasses_receipts >= contact_receipts:
        return f"Not settled on its contact-lens part: the spectacle-lens and frame receipts of claim {claim_number} are at least its contact-lens and fitting receipts."
    names = {"vision_contacts_claim": "contact_lenses", "vision_lens_claim": "lenses", "vision_frame_claim": "frame"}
    denied = {k: v for k, v in (("exam", exam_remark), ("fitting", fitting_remark), ("contact_lenses", contact_lenses_remark), ("lenses", lenses_remark), ("frame", frame_remark)) if v}
    amount = round(float(plan_paid), 2)
    today = ctx.now()[:10]
    ordered = []
    for k in ["exam", "fitting", "contact_lenses", "lenses", "frame"]:
        for r in rows:
            et = r["event_type"]
            kind = ("exam" if r.get("exam_type", "") == "routine_eye_exam" else "fitting") if et == "vision_exam_claim" else names.get(et, "")
            if kind == k:
                ordered.append((k, r))
    target = next((r["vision_claim_id"] for k, r in ordered if k not in denied), ordered[0][1]["vision_claim_id"] if ordered else "")
    out = {}
    for k, r in ordered:
        remark = denied.get(k, "PAID_OON_REIMBURSEMENT" if r.get("network_channel", "") == "out_of_network" else "PAID")
        ctx.update("vision_claims", r["vision_claim_id"], remark_code=remark, plan_paid=(amount if r["vision_claim_id"] == target else 0.0), adjudicated_date=today)
        out[r["vision_claim_id"]] = remark
    return str({"claim_number": claim_number, "plan_paid": amount, "lines": out, "adjudicated_date": today})

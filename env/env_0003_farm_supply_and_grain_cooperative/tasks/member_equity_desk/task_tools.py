"""Hidden task tools for the member equity desk of Prairie Ridge Cooperative Association.

Each function performs one atomic write on the member's equity records. None of them
aggregates history, works out an amount or judges whether the write is due: the agent
reads the books, applies the cooperative's equity policies and passes the finished
figure in.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="write")
def book_qualifying_units_5a905387(ctx: ToolContext, membership_id: str, fiscal_year: int,
                                   allocation_basis: str, qualifying_units: float) -> str:
    """Credit a further parcel of qualifying business to a member's equity account for a
    fiscal year that has already closed.

    One call adds one accrual line to the equity account: the volume named is credited to the
    membership on the stream named, dated today and carrying the fiscal year it belongs to, so
    that the member's qualifying volume for that year stands complete on the books. Nothing
    else on the membership moves - no allocation is declared, no cash is issued and no equity
    is retained by this call. The member sees the extra volume on the next equity statement for
    that year.

    Args:
        membership_id: Id class — the internal reference number of the equity membership the
            volume is credited to, as returned by the equity membership lookup.
        fiscal_year: Fixed-format class — the cooperative fiscal year the business falls in,
            given as a four-digit fiscal year, e.g. 2026; the fiscal year ends 31 August and is
            named for the calendar year in which it ends. There is no empty value: a year must
            always be named.
        allocation_basis: Enum class — the stream of business the volume was earned on, written
            exactly as one of: grain_bushels when the volume is bushels of grain the member
            marketed through the cooperative; input_dollars when it is dollars of seed,
            fertilizer or crop protection bought on a crop input account; energy_gallons when it
            is gallons of propane or refined fuel delivered; feed_tons when it is tons of feed
            milled or delivered; service_dollars when it is dollars billed for custom
            application or other field services.
        qualifying_units: Fixed-format class — the volume of qualifying business being credited,
            expressed as a number to 2 decimal places, in the unit implied by allocation_basis
            (bushels, dollars, gallons or tons); half a unit rounds up, and the value is never
            negative.

    Returns:
        A single confirmation sentence naming the equity ledger reference minted for the new
        accrual line, the volume credited, the stream it was credited on and the fiscal year it
        was dated to. The sentence appearing at all is what indicates the line was written; a
        failure raises instead of returning.
    """
    rid = ctx.make_id("pu_", membership_id, fiscal_year, allocation_basis, qualifying_units)
    ctx.create("patronage_ledger", rid, entry_id=rid, membership_id=membership_id,
               customer_id=(ctx.find("patronage_memberships", membership_id=membership_id) or [{}])[0].get("customer_id", ""),
               event_type="patronage_units_accrued", entry_date=ctx.now()[:10],
               fiscal_year=int(fiscal_year), allocation_basis=allocation_basis,
               patronage_units=round(float(qualifying_units), 2), posted_date=ctx.now()[:10])
    return (f"Equity ledger line {rid} credited {round(float(qualifying_units), 2)} of "
            f"{allocation_basis} to membership {membership_id} for fiscal year {int(fiscal_year)}.")


@tool(owner="agent", rw="write")
def restate_allocation_notice_7a44a997(ctx: ToolContext, membership_id: str, notice_number: str,
                                       allocation_basis: str, restated_units: float,
                                       restated_allocation_amount: float) -> str:
    """Restate a patronage allocation that has already been declared on a written notice, so the
    books carry the allocation the member's true volume earns.

    One call adds one restatement line to the equity account against the notice named, carrying
    the volume the allocation is now worked out on and the allocation as restated, on the stream
    named, dated today and taking its fiscal year from the notice it restates. The original
    notice line is left standing as the historical record and the restatement line supersedes
    it; no cash is issued and no equity is retained by this call. The member sees the restated
    allocation on the equity statement for the year restated.

    Args:
        membership_id: Id class — the internal reference number of the equity membership whose
            allocation is being restated, as returned by the equity membership lookup.
        notice_number: Fixed-format class — the written patronage notice the allocation was
            originally reported on, of the form PN- followed by six digits, e.g. PN-201188, read
            from the equity ledger line carrying that allocation. There is no empty value.
        allocation_basis: Enum class — the stream of business being restated, written exactly as
            one of: grain_bushels when the restatement concerns bushels of grain marketed
            through the cooperative; input_dollars when it concerns dollars spent on a crop input
            account; energy_gallons when it concerns gallons of propane or refined fuel
            delivered; feed_tons when it concerns tons of feed milled or delivered;
            service_dollars when it concerns dollars billed for custom application or other
            field services.
        restated_units: Fixed-format class — the volume the restated allocation is worked out on,
            expressed as a number to 2 decimal places, in the unit implied by allocation_basis
            (bushels, dollars, gallons or tons); half a unit rounds up, and the value is never
            negative.
        restated_allocation_amount: Fixed-format class — the total patronage the year now
            allocates on this notice before any split between cash and equity, in USD to 2
            decimal places, half a cent rounding up, never negative.

    Returns:
        A single confirmation sentence naming the equity ledger reference minted for the
        restatement line, the notice it was booked against, the volume it rests on and the
        restated allocation. The sentence appearing at all is what indicates the restatement was
        written; a failure raises instead of returning.
    """
    rows = ctx.find("patronage_ledger", notice_number=notice_number)
    year = rows[0].get("fiscal_year") if rows else None
    rid = ctx.make_id("pa_", membership_id, notice_number, allocation_basis, restated_units,
                      restated_allocation_amount)
    ctx.create("patronage_ledger", rid, entry_id=rid, membership_id=membership_id,
               customer_id=(ctx.find("patronage_memberships", membership_id=membership_id) or [{}])[0].get("customer_id", ""),
               event_type="patronage_allocation_adjusted", entry_date=ctx.now()[:10],
               fiscal_year=year, notice_number=notice_number, allocation_basis=allocation_basis,
               patronage_units=round(float(restated_units), 2),
               allocated_amount=round(float(restated_allocation_amount), 2),
               adjustment_reason="restatement", posted_date=ctx.now()[:10])
    return (f"Equity ledger line {rid} restated notice {notice_number} on membership "
            f"{membership_id} to {round(float(restated_allocation_amount), 2)} on "
            f"{round(float(restated_units), 2)} of {allocation_basis}.")


@tool(owner="agent", rw="write")
def record_capital_retain_31b65d0b(ctx: ToolContext, membership_id: str, fiscal_year: int,
                                   allocation_basis: str, retain_amount: float) -> str:
    """Take the cooperative's per-unit capital retain for a fiscal year and credit it to the
    member's equity account.

    One call adds one capital retain line to the equity account: the amount named is credited to
    the membership's equity for the fiscal year named, recorded against the stream named and
    dated today. The member's equity grows by that amount; no allocation is declared and no cash
    moves. The member sees the retain as a separate credit line on the equity statement for the
    year.

    Args:
        membership_id: Id class — the internal reference number of the equity membership the
            retain is credited to, as returned by the equity membership lookup.
        fiscal_year: Fixed-format class — the cooperative fiscal year the retain belongs to,
            given as a four-digit fiscal year, e.g. 2026; the fiscal year ends 31 August and is
            named for the calendar year in which it ends. There is no empty value.
        allocation_basis: Enum class — the stream of business the retain line is recorded
            against, written exactly as one of: grain_bushels when the retain is recorded against
            bushels of grain marketed through the cooperative; input_dollars when it is recorded
            against dollars spent on a crop input account; energy_gallons when it is recorded
            against gallons of propane or refined fuel delivered; feed_tons when it is recorded
            against tons of feed milled or delivered; service_dollars when it is recorded against
            dollars billed for custom application or other field services.
        retain_amount: Fixed-format class — the capital retained and credited to the member's
            equity on this line, in USD to 2 decimal places, half a cent rounding up, never
            negative.

    Returns:
        A single confirmation sentence naming the equity ledger reference minted for the retain
        line, the amount credited to equity, the stream it was recorded against and the fiscal
        year it belongs to. The sentence appearing at all is what indicates the retain was
        written; a failure raises instead of returning.
    """
    rid = ctx.make_id("pr_", membership_id, fiscal_year, allocation_basis, retain_amount)
    ctx.create("patronage_ledger", rid, entry_id=rid, membership_id=membership_id,
               customer_id=(ctx.find("patronage_memberships", membership_id=membership_id) or [{}])[0].get("customer_id", ""),
               event_type="patronage_retain_withheld", entry_date=ctx.now()[:10],
               fiscal_year=int(fiscal_year), allocation_basis=allocation_basis,
               retain_amount=round(float(retain_amount), 2), posted_date=ctx.now()[:10])
    return (f"Equity ledger line {rid} credited a capital retain of "
            f"{round(float(retain_amount), 2)} to membership {membership_id} for fiscal year "
            f"{int(fiscal_year)} on {allocation_basis}.")


@tool(owner="user", rw="write")
def transfer_membership_equity_359bd53a(ctx: ToolContext, membership_id: str, request_id: str,
                                        equity_standing_amount: float) -> str:
    """Sign a whole equity membership over to the transferee named on a registered transfer
    instruction, as the member themselves.

    One call closes the member's own equity account and records what moved: the membership is
    put into transferred standing, dated today, with the equity standing at that moment written
    onto it, and the registered instruction is marked completed. From then on the account is
    closed to further allocation and the transferee holds the equity in the member's place. The
    member sees a closing equity statement showing the amount signed over.

    Args:
        membership_id: Id class — the internal reference number of the equity membership being
            signed over, as returned by the equity membership lookup.
        request_id: Id class — the internal reference number of the registered transfer
            instruction the member signed, as returned by the equity request lookup.
        equity_standing_amount: Fixed-format class — the equity standing on the membership at the
            moment it is signed over, in USD to 2 decimal places, half a cent rounding up, never
            negative.

    Returns:
        A single confirmation sentence naming the membership closed, the equity recorded as
        signed over, the date the transfer took effect and the instruction it was recorded
        against. The sentence appearing at all is what indicates the transfer was recorded; a
        failure raises instead of returning.
    """
    ctx.update("patronage_memberships", membership_id, status="transferred",
               closed_date=ctx.now()[:10],
               equity_balance=round(float(equity_standing_amount), 2))
    ctx.update("patronage_requests", request_id, request_status="completed")
    return (f"Membership {membership_id} signed over on {ctx.now()[:10]} with equity of "
            f"{round(float(equity_standing_amount), 2)} recorded against instruction {request_id}.")


@tool(owner="agent", rw="write")
def record_equity_revolvement_d16ad296(ctx: ToolContext, membership_id: str, fiscal_year: int,
                                       revolvement_amount: float) -> str:
    """Pay a member's equity back out under the board's revolvement cycle for one allocation
    year.

    One call adds one revolvement line to the equity account: the amount named is paid back out
    against the allocation year named, dated today, and the member's equity falls by that
    amount. No allocation is declared and no membership standing changes. The member sees the
    revolvement as a payment line on the equity statement and receives the money on the
    cooperative's ordinary remittance run.

    Args:
        membership_id: Id class — the internal reference number of the equity membership the
            revolvement is paid on, as returned by the equity membership lookup.
        fiscal_year: Fixed-format class — the allocation year whose equity is being revolved,
            given as a four-digit fiscal year, e.g. 2026; the fiscal year ends 31 August and is
            named for the calendar year in which it ends. There is no empty value.
        revolvement_amount: Fixed-format class — the equity paid back out to the member on this
            line, in USD to 2 decimal places, half a cent rounding up, never negative.

    Returns:
        A single confirmation sentence naming the equity ledger reference minted for the
        revolvement line, the amount paid back out and the allocation year it was drawn from.
        The sentence appearing at all is what indicates the revolvement was written; a failure
        raises instead of returning.
    """
    rid = ctx.make_id("pv_", membership_id, fiscal_year, revolvement_amount)
    ctx.create("patronage_ledger", rid, entry_id=rid, membership_id=membership_id,
               customer_id=(ctx.find("patronage_memberships", membership_id=membership_id) or [{}])[0].get("customer_id", ""),
               event_type="patronage_equity_revolved", entry_date=ctx.now()[:10],
               fiscal_year=int(fiscal_year),
               revolvement_amount=round(float(revolvement_amount), 2),
               posted_date=ctx.now()[:10])
    return (f"Equity ledger line {rid} revolved {round(float(revolvement_amount), 2)} out of "
            f"membership {membership_id} against allocation year {int(fiscal_year)}.")


@tool(owner="user", rw="write")
def retire_estate_equity_f4a8a7dc(ctx: ToolContext, membership_id: str, request_id: str,
                                  retired_equity_amount: float) -> str:
    """Retire a deceased member's equity to the estate on the registered estate application, as
    the estate's own act.

    One call closes the equity account and settles it: the membership is put into retired
    standing, dated today, with the equity settled to the estate written onto it and the
    recorded notice of death carried on the closed record, and the registered application is
    marked completed. The account earns nothing further and the estate receives the settled
    amount on the cooperative's ordinary remittance run.

    Args:
        membership_id: Id class — the internal reference number of the equity membership being
            retired, as returned by the equity membership lookup.
        request_id: Id class — the internal reference number of the registered estate retirement
            application, as returned by the equity request lookup.
        retired_equity_amount: Fixed-format class — the equity settled to the estate on this
            retirement, in USD to 2 decimal places, half a cent rounding up, never negative.

    Returns:
        A single confirmation sentence naming the membership retired, the equity settled to the
        estate, the date the retirement took effect and the application it was recorded against.
        The sentence appearing at all is what indicates the retirement was recorded; a failure
        raises instead of returning.
    """
    ctx.update("patronage_memberships", membership_id, status="retired",
               closed_date=ctx.now()[:10], estate_flag=True,
               equity_balance=round(float(retired_equity_amount), 2))
    ctx.update("patronage_requests", request_id, request_status="completed")
    return (f"Membership {membership_id} retired on {ctx.now()[:10]} with equity of "
            f"{round(float(retired_equity_amount), 2)} settled to the estate against "
            f"application {request_id}.")

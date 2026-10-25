"""Hidden task tools for the installation_scheduling_and_job_charges difficulty of
env_0060_window_replacement_company (Ridgeline Window & Door).

Each tool lands exactly one atomic write on an installation job: a job charge, a credit, a crew
booking or a customer-approved charge for added work. A tool never works out an amount, a count or
a date for the caller and never judges whether the write is owed; the caller passes the values the
installation charter fixes, and the tool records them as given.
"""

from erlbench import ToolContext, tool


class _JobRows:
    """Value helpers shared by the tools below (they compute field values only and never write)."""

    @staticmethod
    def activity_fields(install_job_id: str, customer_id: str) -> dict:
        """Blank activity-row fields shared by every job-charge write."""
        return {
            "install_job_id": install_job_id,
            "customer_id": customer_id,
            "credit_kind": "not_applicable",
            "source_install_activity_id": "",
            "initiated_by": "not_applicable",
            "notice_hours": 0,
            "previous_date": "",
            "new_date": "",
            "punch_kind": "not_applicable",
            "crew_day_number": 0,
            "arrival_minutes_late": 0,
        }


@tool(owner="agent", rw="write")
def assess_reschedule_fee_4c3399da(ctx: ToolContext, install_job_id: str, customer_id: str, fee_date: str, amount: float) -> str:
    """Bill the customer's installation job the late reschedule fee owed for one customer
    reschedule of a booked crew date. One call records one job charge of kind late reschedule fee,
    dated the day that reschedule was requested, for the amount given; the charge adds to the job
    charges the customer owes, which are collected with the contract's final balance. The customer
    sees the fee on the job's charges from then on. A receipt with a new charge reference means the
    fee is on the job.

    Args:
        install_job_id: Id class — the installation job record number of the job whose crew date the
            customer moved or released, as returned by the installation job lookup.
        customer_id: Id class — the customer reference number of the job's owner, as returned by the
            customer profile lookup.
        fee_date: Fixed-format class — the date the customer reschedule being charged was requested,
            written YYYY-MM-DD (calendar date at the service address, no time part).
        amount: Fixed-format class — the late reschedule fee charged, in USD as a positive amount
            rounded to 2 decimal places.

    Returns:
        A text rendering of a dictionary with these fields: "charge_id" (text, the new job charge
        reference number), "install_job_id" (text, the job charged), "fee_kind" (text, always
        late_reschedule_fee), "fee_date" (text, YYYY-MM-DD, the date the charge is booked on) and
        "amount" (number, USD with 2 decimal places, the amount added to the job charges). Its
        presence means the charge was recorded.
    """
    rid = ctx.make_id("iac_", install_job_id, customer_id, fee_date, amount, "late_reschedule_fee")
    fields = _JobRows.activity_fields(install_job_id, customer_id)
    ctx.create("install_activities", rid, install_activity_id=rid, event_type="install_fee_assessed",
               activity_date=fee_date, amount=round(float(amount), 2), fee_kind="late_reschedule_fee",
               units=0, **fields)
    return str({"charge_id": rid, "install_job_id": install_job_id, "fee_kind": "late_reschedule_fee",
                "fee_date": fee_date, "amount": round(float(amount), 2)})


@tool(owner="agent", rw="write")
def assess_permit_admin_fee_bf2a1df3(ctx: ToolContext, install_job_id: str, customer_id: str, fee_date: str, amount: float) -> str:
    """Bill a permitted installation job the permit administration fee Ridgeline charges for filing
    the building permit and booking the final inspection. One call records one job charge of kind
    permit administration fee, dated as given, for the amount given; the charge adds to the job
    charges the customer owes, which are collected with the contract's final balance, and the job's
    charges show the permit filing from then on. A receipt with a new charge reference means the fee
    is on the job.

    Args:
        install_job_id: Id class — the installation job record number of the permitted job, as
            returned by the installation job lookup.
        customer_id: Id class — the customer reference number of the job's owner, as returned by the
            customer profile lookup.
        fee_date: Fixed-format class — the date the charge is booked on, written YYYY-MM-DD
            (calendar date at the service address, no time part).
        amount: Fixed-format class — the permit administration fee charged, in USD as a positive
            amount rounded to 2 decimal places.

    Returns:
        A text rendering of a dictionary with these fields: "charge_id" (text, the new job charge
        reference number), "install_job_id" (text, the job charged), "fee_kind" (text, always
        permit_admin_fee), "fee_date" (text, YYYY-MM-DD, the date the charge is booked on) and
        "amount" (number, USD with 2 decimal places, the amount added to the job charges). Its
        presence means the charge was recorded.
    """
    rid = ctx.make_id("iac_", install_job_id, customer_id, fee_date, amount, "permit_admin_fee")
    fields = _JobRows.activity_fields(install_job_id, customer_id)
    ctx.create("install_activities", rid, install_activity_id=rid, event_type="install_fee_assessed",
               activity_date=fee_date, amount=round(float(amount), 2), fee_kind="permit_admin_fee",
               units=0, **fields)
    return str({"charge_id": rid, "install_job_id": install_job_id, "fee_kind": "permit_admin_fee",
                "fee_date": fee_date, "amount": round(float(amount), 2)})


@tool(owner="agent", rw="write")
def book_crew_date_2f98f590(ctx: ToolContext, install_job_id: str, scheduled_date: str,
                            crew_days_planned: int) -> str:
    """Book a crew date for an installation job that is waiting to be scheduled. One call sets the
    job's booked crew date (the day the crew arrives to start the work) and the number of crew days
    reserved for it, and moves the job to scheduled; the job record then
    shows that date and crew-day count. A receipt with status scheduled means the booking stands.

    Args:
        install_job_id: Id class — the installation job record number of the job being booked, as
            returned by the installation job lookup.
        scheduled_date: Fixed-format class — the crew date the customer accepted, written YYYY-MM-DD
            (calendar date at the service address, no time part).
        crew_days_planned: Fixed-format class — the crew days reserved for the job, a non-negative
            integer count of whole days.

    Returns:
        A text rendering of a dictionary with these fields: "install_job_id" (text, the job
        booked), "status" (text, always scheduled once booked), "scheduled_date" (text, YYYY-MM-DD,
        the booked crew date) and "crew_days_planned" (integer, the crew days reserved). Its presence
        means the job is booked.
    """
    ctx.update("install_jobs", install_job_id, status="scheduled", scheduled_date=scheduled_date,
               crew_days_planned=int(crew_days_planned))
    return str({"install_job_id": install_job_id, "status": "scheduled", "scheduled_date": scheduled_date,
                "crew_days_planned": int(crew_days_planned)})


@tool(owner="user", rw="write")
def approve_trim_capping_649df03e(ctx: ToolContext, install_job_id: str, customer_id: str,
                                  work_date: str, units: float,
                                  amount: float) -> str:
    """The customer approves, in their own name, exterior aluminum trim capping on every opening of
    their installation job and accepts its price. One call records one job charge of kind exterior
    capping charge for the openings and amount given, dated the crew day the capping is done; the
    charge adds to the job charges the customer owes, which are collected with the contract's final
    balance. A receipt with a new charge
    reference means the approval is on record.

    Args:
        install_job_id: Id class — the installation job record number of the customer's job, as
            given to the customer by the agent from the installation job lookup.
        customer_id: Id class — the customer's own reference number, as given to the customer by the
            agent from the customer profile lookup.
        work_date: Fixed-format class — the crew day on which the capping is done, written
            YYYY-MM-DD (calendar date at the service address, no time part).
        units: Fixed-format class — the openings the capping covers: non-negative number; openings
            for per-opening fees, linear feet for rot repair; here a whole count of openings.
        amount: Fixed-format class — the capping charge the customer accepts, in USD as a positive
            amount rounded to 2 decimal places.

    Returns:
        A text rendering of a dictionary with these fields: "charge_id" (text, the new job charge
        reference number), "install_job_id" (text, the job charged), "fee_kind" (text, always
        exterior_capping_charge), "work_date" (text, YYYY-MM-DD, the date the charge is booked on),
        "units" (number, the openings covered) and "amount" (number, USD with 2 decimal places, the
        amount added to the job charges). Its presence means the approval was recorded.
    """
    rid = ctx.make_id("iac_", install_job_id, customer_id, work_date, units, amount, "exterior_capping_charge")
    fields = _JobRows.activity_fields(install_job_id, customer_id)
    ctx.create("install_activities", rid, install_activity_id=rid, event_type="install_fee_assessed",
               activity_date=work_date, amount=round(float(amount), 2), fee_kind="exterior_capping_charge",
               units=float(units), **fields)
    return str({"charge_id": rid, "install_job_id": install_job_id, "fee_kind": "exterior_capping_charge",
                "work_date": work_date, "units": float(units), "amount": round(float(amount), 2)})


@tool(owner="agent", rw="write")
def issue_company_reschedule_credit_53c525ee(ctx: ToolContext, install_job_id: str, customer_id: str,
                                             source_install_activity_id: str, amount: float) -> str:
    """Credit the customer's installation job for one crew date that Ridgeline itself moved or
    released. One call records one credit of kind company reschedule credit, dated today, naming the
    reschedule it is for, for the amount given; the credit reduces the job charges the customer
    owes, which are collected with the contract's final balance. The customer sees the credit on the
    job's charges from then on. A receipt with a new credit reference means the credit stands.

    Args:
        install_job_id: Id class — the installation job record number of the job whose crew date
            Ridgeline moved, as returned by the installation job lookup.
        customer_id: Id class — the customer reference number of the job's owner, as returned by the
            customer profile lookup.
        source_install_activity_id: Id class — the activity record number of the company reschedule
            being credited, as returned by the installation activity lookup.
        amount: Fixed-format class — the credit granted, in USD as a positive amount rounded to 2
            decimal places.

    Returns:
        A text rendering of a dictionary with these fields: "credit_id" (text, the new credit
        reference number), "install_job_id" (text, the job credited), "credit_kind" (text, always
        company_reschedule_credit), "source_install_activity_id" (text, the reschedule credited),
        "credit_date" (text, YYYY-MM-DD, the date the credit is booked on) and "amount" (number, USD
        with 2 decimal places, the amount taken off the job charges). Its presence means the credit
        was recorded.
    """
    rid = ctx.make_id("iac_", install_job_id, customer_id, source_install_activity_id, amount,
                      "company_reschedule_credit")
    fields = _JobRows.activity_fields(install_job_id, customer_id)
    fields["source_install_activity_id"] = source_install_activity_id
    ctx.create("install_activities", rid, install_activity_id=rid, event_type="install_credit_issued",
               activity_date=ctx.now()[:10], amount=round(float(amount), 2), fee_kind="not_applicable",
               units=0, **{k: v for k, v in fields.items() if k != "credit_kind"},
               credit_kind="company_reschedule_credit")
    return str({"credit_id": rid, "install_job_id": install_job_id, "credit_kind": "company_reschedule_credit",
                "source_install_activity_id": source_install_activity_id, "credit_date": ctx.now()[:10],
                "amount": round(float(amount), 2)})


@tool(owner="agent", rw="write")
def assess_failed_access_fee_5745b419(ctx: ToolContext, install_job_id: str, customer_id: str, fee_date: str,
                                      amount: float) -> str:
    """Bill the customer's installation job the failed-access fee for one crew visit at which the crew
    could not get access or found the work area not cleared. One call records one job charge of kind
    failed-access fee, dated as given, for the amount given; the charge adds to the job charges the
    customer owes, which are collected with the contract's final balance. The customer sees the fee
    on the job's charges from then on. A receipt with a new charge reference means the fee is on the
    job.

    Args:
        install_job_id: Id class — the installation job record number of the job whose visit failed,
            as returned by the installation job lookup.
        customer_id: Id class — the customer reference number of the job's owner, as returned by the
            customer profile lookup.
        fee_date: Fixed-format class — the date the charge is booked on, written YYYY-MM-DD
            (calendar date at the service address, no time part).
        amount: Fixed-format class — the failed-access fee charged, in USD as a positive amount
            rounded to 2 decimal places.

    Returns:
        A text rendering of a dictionary with these fields: "charge_id" (text, the new job charge
        reference number), "install_job_id" (text, the job charged), "fee_kind" (text, always
        failed_access_fee), "fee_date" (text, YYYY-MM-DD, the date the charge is booked on) and
        "amount" (number, USD with 2 decimal places, the amount added to the job charges). Its
        presence means the charge was recorded.
    """
    rid = ctx.make_id("iac_", install_job_id, customer_id, fee_date, amount, "failed_access_fee")
    fields = _JobRows.activity_fields(install_job_id, customer_id)
    ctx.create("install_activities", rid, install_activity_id=rid, event_type="install_fee_assessed",
               activity_date=fee_date, amount=round(float(amount), 2), fee_kind="failed_access_fee",
               units=0, **fields)
    return str({"charge_id": rid, "install_job_id": install_job_id, "fee_kind": "failed_access_fee",
                "fee_date": fee_date, "amount": round(float(amount), 2)})


@tool(owner="agent", rw="write")
def assess_lead_safe_fee_cf2f582a(ctx: ToolContext, install_job_id: str, customer_id: str, fee_date: str,
                                  units: float, amount: float) -> str:
    """Bill the customer's installation job the lead-safe work practice fee for the job's work under
    the EPA Renovation, Repair and Painting rule. One call records one job charge of kind lead-safe
    fee for the openings and amount given, dated as given; the charge adds to the job charges the
    customer owes, which are collected with the contract's final balance, and the job's charges show
    the lead-safe work from then on. A receipt with a new charge reference means the fee is on the
    job.

    Args:
        install_job_id: Id class — the installation job record number of the job worked under
            lead-safe practices, as returned by the installation job lookup.
        customer_id: Id class — the customer reference number of the job's owner, as returned by the
            customer profile lookup.
        fee_date: Fixed-format class — the date the charge is booked on, written YYYY-MM-DD
            (calendar date at the service address, no time part).
        units: Fixed-format class — the openings the fee covers: non-negative number; openings for
            per-opening fees, linear feet for rot repair; here a whole count of openings.
        amount: Fixed-format class — the lead-safe fee charged, in USD as a positive amount rounded
            to 2 decimal places.

    Returns:
        A text rendering of a dictionary with these fields: "charge_id" (text, the new job charge
        reference number), "install_job_id" (text, the job charged), "fee_kind" (text, always
        lead_safe_fee), "fee_date" (text, YYYY-MM-DD, the date the charge is booked on), "units"
        (number, the openings covered) and "amount" (number, USD with 2 decimal places, the amount
        added to the job charges). Its presence means the charge was recorded.
    """
    rid = ctx.make_id("iac_", install_job_id, customer_id, fee_date, units, amount, "lead_safe_fee")
    fields = _JobRows.activity_fields(install_job_id, customer_id)
    ctx.create("install_activities", rid, install_activity_id=rid, event_type="install_fee_assessed",
               activity_date=fee_date, amount=round(float(amount), 2), fee_kind="lead_safe_fee",
               units=float(units), **fields)
    return str({"charge_id": rid, "install_job_id": install_job_id, "fee_kind": "lead_safe_fee",
                "fee_date": fee_date, "units": float(units), "amount": round(float(amount), 2)})


@tool(owner="user", rw="write")
def approve_interior_casing_01c7ec6d(ctx: ToolContext, install_job_id: str, customer_id: str, work_date: str,
                                     units: float, amount: float) -> str:
    """The customer approves, in their own name, new interior casing on every opening of their
    installation job and accepts its price. One call records one job charge of kind interior trim
    charge for the openings and amount given, dated the crew day the casing is fitted; the charge
    adds to the job charges the customer owes, which are collected with the contract's final
    balance. A receipt with a new charge
    reference means the approval is on record.

    Args:
        install_job_id: Id class — the installation job record number of the customer's job, as
            given to the customer by the agent from the installation job lookup.
        customer_id: Id class — the customer's own reference number, as given to the customer by the
            agent from the customer profile lookup.
        work_date: Fixed-format class — the crew day on which the casing is fitted, written
            YYYY-MM-DD (calendar date at the service address, no time part).
        units: Fixed-format class — the openings the casing covers: non-negative number; openings
            for per-opening fees, linear feet for rot repair; here a whole count of openings.
        amount: Fixed-format class — the casing charge the customer accepts, in USD as a positive
            amount rounded to 2 decimal places.

    Returns:
        A text rendering of a dictionary with these fields: "charge_id" (text, the new job charge
        reference number), "install_job_id" (text, the job charged), "fee_kind" (text, always
        interior_trim_charge), "work_date" (text, YYYY-MM-DD, the date the charge is booked on),
        "units" (number, the openings covered) and "amount" (number, USD with 2 decimal places, the
        amount added to the job charges). Its presence means the approval was recorded.
    """
    rid = ctx.make_id("iac_", install_job_id, customer_id, work_date, units, amount, "interior_trim_charge")
    fields = _JobRows.activity_fields(install_job_id, customer_id)
    ctx.create("install_activities", rid, install_activity_id=rid, event_type="install_fee_assessed",
               activity_date=work_date, amount=round(float(amount), 2), fee_kind="interior_trim_charge",
               units=float(units), **fields)
    return str({"charge_id": rid, "install_job_id": install_job_id, "fee_kind": "interior_trim_charge",
                "work_date": work_date, "units": float(units), "amount": round(float(amount), 2)})

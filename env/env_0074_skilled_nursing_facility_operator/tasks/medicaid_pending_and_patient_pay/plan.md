# plan — medicaid_pending_and_patient_pay (M=2)  [revised by successor agent; supersedes earlier plan]

Draw (draw_counts.py --tasks 2): task 0 prereq=2 factors [5,4,4]; task 1 prereq=1 factors [5,5].

Why revised (details in worklog "Resume"): settlement and accrual cannot carry 4 load-bearing factors with >=2
parameter ladders on records (settlement varies only with the penalty end; accrual rate year is two-valued and
the schedule is not readable by the DSL); the HMA-from-accrual-rows edge contradicts the calendar. The one
quantity with several real, record-borne dimensions is a month's COST OF CARE (federal/PA rule: patient pay never
exceeds the month's cost of care): Part A days by band (Medicare pays days 1-20 in full; days 21-100 leave the
daily coinsurance), the resident's coinsurance share by supplemental coverage, the coinsurance rate of the year
of service, and days away on hospital / therapeutic leave whose bed was held at the resident's expense.

## Task 0 — eligible case (approval notice 2026-09-22, eligible from 2026-07-01), resident in a long Part A
## rehab stay with Medigap Plan L; center is SSA representative payee. frozen 2026-11-09 10:40:00 EST
- P0a medicaid_ext_actual_month_cost_cap (agent, state_due, 4): cost_of_care_cap on October's actual charge.
- P0b medicaid_ext_estimate_month_trueup (agent, state_due, 5): trueup_decrease on September's estimate.
- P0c medicaid_ext_eligible_advance_payment (user, on_request, 4, ROOT): December advance = patient pay in effect
  for December less the benefit the payee account applies (less the allowance it keeps) less the case credit.
  Edges P0c->P0a, P0c->P0b value_input (credit). P0a/P0b commute (different charges).
## Task 1 — pending case, HMA tier, going home Dec 4; October had a home visit, a hospital stay and Part A.
## frozen 2026-11-09 10:20:00 EST
- P1a medicaid_ext_pending_estimate_cost_cap (agent, state_due, 5): cost_of_care_cap on October's estimate.
- P1b medicaid_ext_pending_advance_payment (user, on_request, 5, ROOT): December advance of the estimate
  (allowance, move-out partial month, interest income) less the standing-authorization payment, less credit.

## FINAL (as built, third agent 2026-10-22; see worklog for the gate-forced changes)
- T0: medicaid_ext_actual_month_cost_cap (4) + medicaid_ext_estimate_month_trueup (5, actual = lesser of notice amount and the reconciled month's cost of care) -> root medicaid_ext_eligible_advance_payment (user, 4). New admission 2026-09-02.
- T1: medicaid_ext_pending_estimate_cost_cap (5) -> root medicaid_ext_pending_advance_payment (user, 5). Admission 2026-10-06; no December move-out.

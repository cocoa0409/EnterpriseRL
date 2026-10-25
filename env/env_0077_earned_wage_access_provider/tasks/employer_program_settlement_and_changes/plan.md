# plan — employer_program_settlement_and_changes (category program), M=2
Draw: task0 prereq=1 factors [6,5]; task1 prereq=2 factors [5,6,6].

## Task 0 (Enterprise tier, frozen 2026-10-14, SLA month 2026-09)
- R0 root, owner=user: program_ext_sla_claim_credit (subject program_sla_credit, on_request), 5 factors:
  covered_fee_lines (method: platform / +per-worker line / +sponsored lines, net of billing-error credits),
  breach_recurrence (param mult: SLA credits booked in 6 months), product_footprint (param add pts, cross paycard+disburse, multi-source),
  enrolled_reach (param add pts: census enrolled), hypercare_window (param mult: months since go-live).
- Q0 prereq, agent: program_ext_worker_fee_rerate (subject program_credit_memo billing_error on employer_paid_pepm line, state_due), 6 factors:
  proration_anchor (method: fee-model effective date / go-live / full month, 30-day convention), enrollment_bands (method graduated),
  card_bundle_depth (param, cross paycard, multi-source), commitment_term (param), launch_pricing (param), adoption_level (param).
- Edge R0->Q0 value_input (SLA base reads per-worker line net of billing-error credits), state form, negated direction.

## Task 1 (Enterprise Plus, frozen 2026-10-26)
- R1 root, owner=user: program_ext_access_ceiling (subject program_amend -> signed cap_change request), 6 factors:
  ramp_start (method), delinquency_record (param: late charges 365d), return_record (param: remittance returns 365d),
  card_pay_channel (param, cross paycard, multi-source), turnover_signal (param: employment_ended notices 6m), loss_ratio (param: net-pay write-offs / schedules 6m).
- Q1a agent: program_ext_return_late_charge (late charge on schedule reinstated by latest remittance return), 6 factors:
  balance_bands (method graduated), bounce_history, resend_relief, program_age_relief, relationship_rate (cross), prior_charges.
- Q1b agent: program_ext_shortfall_late_charge (late charge on latest employer-liable notice), 5 factors:
  reason_surcharge, cure_progress, shortfall_frequency, notice_balance_bands (method), notice_age_relief.
- Edges: R1->Q1a value_input (late-charge count, affirmative), Q1a->Q1b value_input (prior_charges count, affirmative). Chain.

## Status
- [x] task0 green (all per-task gates); program_amend dropped (authorized_role mixed gate unsatisfiable) -> task1 = termination+ETF root
- [x] task1 green: termination notice + ETF (user, 6) <- return late charge (6) <- shortfall late charge (5); chain, both value_input
- [x] XF sweep recorded in both design_rationale worklogs; final gate block green except check_traceability (only the 5 unlock tool-name misses, expected before render)

## Final design (supersedes the Task 1 plan above)
- Task 1 root program_ext_termination_fee (frozen 2026-10-20 09:40:00 EDT, Enterprise Plus); access-percentage policy dropped: program_amend authorized_role gate (authority mixed over a one-field group) cannot pass check_solvability.

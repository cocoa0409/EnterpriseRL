# plan — virtual_visit_booking_and_fees (env_0081), M=2

Draws (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=3 (4 problems), factor_counts [5,4,6,5]; >= 2 value_input edges
- task 1: prerequisite_problems=2 (3 problems), factor_counts [4,6,4]; >= 1 value_input edge

Constraints found in the DSL / charter (drive the design):
- visit holding = one visit_appointments row; SUM/COUNT/LATEST only see THIS visit's charges/estimates.
  Cross-visit counters (courtesy waivers, included-visit counts, sponsor plan-year counts, established
  status) are NOT computable -> no late-cancel / no-show fee policies, no paths decided by counters.
- status / path / reschedule writes carry no amount -> they are opening facts, never problems.
  Every problem is a priced write on visit_charges or visit_estimates of ONE visit.
- value_input edges flow only through this visit's posted lines (SUM) or estimates (LATEST).
- no Subscript in compute -> per-tier catalogue maps are restated as K params.
- time-of-day is testable only by string comparison of scheduled_start with F('booked_date')+' HH:MM'
  (exact for same-day Urgent Care Video Visits, the only type with an after-hours surcharge).
- pack_credit path triggers pack writes -> never written; sponsor/membership/claim rows read-only.

Task 0 (Urgent Care Video Visit, rescheduled; patient located in a Central-time state):
- root A: after-hours surcharge for the visit's new start, paid by the patient with an HSA card
  (owner=user, ruling (c)); honour cap = latest estimate less the other self-pay lines (base gfe cap).
- B: Good Faith Estimate for the new start (fee of the path + expected surcharge).
- C: billing-error refund of the visit fee line (posted at list price; member price applies).
- D: billing-error refund of the surcharge posted for the booked start (local daytime).
- edges A->B, A->C, A->D all value_input through the honour-cap room binding.

Task 1: to be designed after task 0 closes, on the remaining events (visit_fee_charged,
visit_cost_share_collected, other refund reasons) — disjoint tools/policies.

Order of work: base copy of extended yaml -> T0 policies one by one (scratch evaluator in
/tmp/virtual_visit_booking_and_fees_0081/) -> tools -> seed -> task json pieces -> per-task gates ->
T1 -> final gates -> worklog last line.

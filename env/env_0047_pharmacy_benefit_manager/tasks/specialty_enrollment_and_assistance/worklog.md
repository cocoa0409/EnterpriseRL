# worklog — specialty_enrollment_and_assistance (M=2)

## Step 0 draw (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=1, factor_counts=[4, 4]
- task 1: prerequisite_problems=1, factor_counts=[4, 6]

## Scope plan
- Owner=user numeric writes available in this product: only the member's own payment on a shipped fill
  (consent / maximizer / decline / disenroll carry no computable figure). Each task needs one user tool, tools
  must be disjoint, so the member payment is split by billing subtype with exclusive scopes:
  ordinary fill payment (enrollment not on a payment hold) vs hold-release payment (enrollment on a
  payment_overdue hold). Shipping a fill is excluded: a shipped row with a deductible/out-of-pocket portion
  satisfies the plan-category triggers. The only realistic agent write that changes what the member owes is
  manufacturer assistance applied to a fill; it is split by program mechanic (copay card under
  standard/variable copay vs maximizer even draw), both distinct in base specialty_cost_share_assistance.
- task 0: root = ordinary member fill payment (user) <- prereq = copay-card assistance on that fill (agent), value_input.
- task 1: root = hold-release payment (user) <- prereq = maximizer assistance on the oldest unpaid fill (agent), value_input.

## Task 0 design (frozen)
- root P2 specialty_ext_member_fill_payment (user, pays the member's remaining share on the latest shipped fill), 4 factors
- prereq P1 specialty_ext_card_assistance (agent, copay-card payment on that fill), 4 factors; edge value_input (gate = unpaid binding / card on fill)
- world: Dupixent, Northbridge Specialty Exclusive with Copay Assist (variable_copay floor 25), plan Northbridge Rx Select
  (standard accumulation, plan year starts Oct 1 so the Oct fill carries a 150.00 deductible portion), 2025 + 2026 card loads,
  retail courtesy fill of Dupixent 2026-07-14 paid by the card at the counter, earlier member overpayment 10.00.
- P1 gold 380.00 (avail-bound: 3080 - 2400 card since load - 300 retail card use); P2 gold 13.33 (floor 25 x 28/30 - 10 credit).
- 2026-10-08T06:50:29 P1+P2 written to specialty.extended.yaml
- 2026-10-08T06:52:56 task0 world seeded (tasks/0.json, via temp _build0.py)
- 2026-10-08T06:56:35 task0 closed: per-task gates extended/task_tools/replay/solvability/compute/grounding/cross_fire OK; P1=380.00 P2=13.33
- 2026-10-08T07:03:59 P3 specialty_ext_maximizer_draw written (6 factors)
- 2026-10-08T07:04:37 P4 specialty_ext_hold_release_payment written (4 factors)
- 2026-10-08T07:11:30 task1 closed: per-task gates OK; P3 maximizer draw = 900.00 (6 factors), P4 hold-release payment = 150.00 (4 factors)
- 2026-10-08T07:11:30 final difficulty-wide run: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (branches mean 32.00, steps mean 13.00, history max 44, branch max 35), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; check_traceability deferred until the KB is published
- open: (1) the member payment and the assistance application are each split into two tools by billing subtype (ordinary vs hold-release payment; copay card vs maximizer draw), because the only owner=user write in this product that carries a computable figure is the member's payment; flag for audit as a possible near-synonym concern. (2) Some factor ladders are refinements authored for this charter (retail card use, member credit, release target, retail-dispensed set-aside) and should go through the policy audit for realism. (3) The copay card tool fixes accumulator_adjusted=false, so the copay card rule leaves out members whose plan backs assistance out of the accumulators. (4) The hold is lifted by a resume action that this difficulty has no task tool for.

## Rework round 2 (audit: audits/policy_task/specialty_enrollment_and_assistance/)
- 2026-10-08T08:31:36 start: round-1 artifacts copied to /tmp for reference; extended_policies being rewritten policy by policy
- plan per item: F-POL-1 declare override of specialty_maximizer charge clause (enrolled member keeps maximizer cost share only on the part the even draw covers); F-POL-2 declare override of evt_assistance cap clause in both assistance policies and cap at the fill's cost share; F-POL-3 maximizer draw pays deductible first (tool gains deductible_portion) and scopes out accumulator-adjustment plans; F-POL-4 release target rewritten in whole months, compute = rule; F-FAC-1..6 every struck factor replaced by a live ladder (card basis without the scope conjunct, program-year window, retail use with live no-load tier, guaranteed share folded with split proration, credit window by plan year, draw mode, refund add-back); task 1 world rebuilt (Humira 42-day fills, two fills left in the horizon) so every factor bites
- 2026-10-08T08:32:22 P1 rewritten (F-FAC-1/2/3, F-POL-2 overwrite)
- 2026-10-08T08:32:59 P2 rewritten (F-FAC-4 count folded into guaranteed share, O-5 no 28-day proration, O-4 scope excludes maximizer, credit window factor cross plan)
- 2026-10-08T08:34:02 P3 rewritten (F-POL-1/2/3 overrides and deductible-first, F-FAC-2/3/5 replaced: draw mode, program-year window, live retail tiers)
- 2026-10-08T08:34:40 P4 rewritten (F-POL-4 release target in whole months, compute = rule; F-FAC-6 payments-counted dropped, replaced by returned-overpayment factor)
- 2026-10-08T08:36:36 task0 reworked: P1 380.00, P2 15.00; per-task gates OK
- 2026-10-08T08:40:08 task1 rebuilt (Humira 42-day fills, on-time maximizer enrollee, approval to 2026-12-26, retail courtesy fill 2026-04-20): P3 475.00 (6 factors), P4 225.00 (4 factors); first numbers (500/200) gave a coincidence where forcing every cross-category read off also gave 500.00, so the retail member share was moved to 150.00
- 2026-10-08T08:40:08 final run: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (branches mean 35.00, steps mean 13.00, history max 45, branch max 38), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability deferred
- audit item responses: F-POL-1 declared override of specialty_maximizer charge clause; F-POL-2 declared override of evt_assistance cap clause in both assistance policies; F-POL-3 maximizer draw pays deductible first (tool param) and excludes accumulator-adjustment plans; F-POL-4 release target in whole months, compute = rule; F-FAC-1..6 replaced (see dossiers); O-1 kept month-granular windows stated exactly in the rules; O-2 program year stated as Jan 1 - Dec 31; O-3 kept (latest approval by effective date), noted; O-4 member payment rule excludes maximizer enrollments; O-5 no 28-day proration; O-6 retail use floored at zero; O-7/O-8 prorated maximizer basis removed, set-aside kept as parameter (value per tier); T0-O1/T1-O1 persona go-ahead lines no longer name any program; T0-O2 rationale corrected; T0-O4 and the task 1 person slip fixed; T1-O2 kept (no resume tool; persona asks only to pay); T1-O3 plan accumulators made consistent

## Rework round 3 (audit revision_2)
- 2026-10-08T10:37:16 start. Plan: R2-T1-F1 rebuild task 1 world so every seed follows the plan/retail charters (Biktarvy 30-day fills on the 90-day list, plan Northbridge Rx Value with plan year Jan 1, accumulators posted at full cost share, out-of-pocket under the maximum; retail member_paid = deductible + copay); retail card/program use redefined from the retail charter (member's payment on paid retail claims, billed to the card as secondary payer) and task 0's retail claim corrected to member_paid 300.00 (value unchanged); R2-F-POL-A overpayment by payment date and fill date both stated; R2-F-POL-B release target no longer restates a due point; R2-O3 late-enrollee clause declared; R2-O4 card basis keyed to the member's payments against the deductible portion; O-8 set-aside relabelled method; R2-T1-O4 consent dates moved before the latest load in both tasks
- 2026-10-08T10:44:31 task 0: values unchanged (card 380.00, member 15.00); retail claim member_paid_amount 0.00 -> 300.00 per the retail charter; consent 2025-12-20; rationale appended with round-2 responses; per-task gates OK
- 2026-10-08T10:44:31 task 1 rebuilt: Biktarvy 30-day fills (90-day list), Northbridge Rx Value with sponsor plan year from May 1, accumulators at full cost share (2025-26 out-of-pocket reaches 3,600.00 on the 2026-01-30 fill, later fills 0.00), G = 2026-05-30 first fill of plan year 2026-27 (550.00 incl. 200.00 deductible), outside specialty courtesy fill 2025-08-03 and retail courtesy claim 2026-06-12 (one per plan year), frozen 2026-07-01 11:20:00 CDT; P3 draw 500.00 (deductible portion 200.00), P4 hold-release payment 50.00; an intermediate world (first 2026 fill as G) failed the history-load gate because no 2026 draw sat in the window, hence the May plan year
- 2026-10-08T10:44:31 final run: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (branches mean 31.00, steps mean 13.00, history max 62, branch max 34), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability deferred

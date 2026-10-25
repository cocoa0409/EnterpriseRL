# plan — activity_fees_and_waivers (env_0078), M=2

Draw (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=1, factor_counts=[5,4]
- task 1: prerequisite_problems=3, factor_counts=[5,5,4,6]

Constraint found in Step 0: every base money rule of `activity` is per ledger row (one waiver / credit /
charge per source fee) and carries one or two natural ladders; DSL cannot read the household's other
participations (own-category cross reads are rejected), so the household fee cap cannot be computed.
Route: each extended policy is a Calloway Creek ISD board-approved schedule provision layered on the base
clause it refines (declared overwrites), with factors reading distinct evidence (this participation's dates,
records log, ledger; meals status/applications; enrollment record).

Task 0 (household Esquivel; High School UIL Athletics, football, fall 2026-27; season-ending injury):
- root: refund check of the credit balance on the closed participation (agent)  [5 factors]
- prereq: the family's withdrawal after clearance with its leaving credit (owner=user, ruling (a)) [4 factors]
- edge root -> prereq: value_input (refund amount reads the credit the withdrawal books), state form.

Task 1 (household Lindgren; Cheer and Dance Team, cut at tryouts): root = the parent's own online payment
of the balance (owner=user, ruling (b)) [6]; prereqs = cut credit [5], waiver true-up [5], late-fee
correction [4] (agent), value_input edges. Details fixed when task 1 starts (task-by-task).

Order of work: T0 policies -> tools -> seed -> persona -> verify script -> GT -> gates; then T1; then XF
recipe tables, traceability pre-run, final gates.
Scratch: /tmp/activity_fees_and_waivers_0078/ only.

## Progress
- 2026-10-24: task 0 DONE on disk (policies activity_ext_waiver_carryback [4], activity_ext_leaving_credit [5];
  tools post_waiver_carryback_credit_28598765, withdraw_activity_participant_4832a954; tasks/0.json).
  Per-task gates: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK;
  traceability pre-docs: only the 2 unlock tool-name misses.
- task 1 tree (revised; cut-at-tryouts outline dropped): Grade 5 Outdoor Education Trip, household Lindgren,
  frozen 2026-11-04. Root = the family's own cancellation of the trip registration before clearance with the
  trip cancellation credit on the trip balance (owner=user) [6]. Prereqs (agent), all value_input into the
  root through the balance's net and the payment allocation (oldest fee first, stated same-date order):
  posting-date waiver on the trip balance [5], posting-date waiver on the trip deposit [4], status-upgrade
  carry-back on the trip balance [5] (waits on both waivers).
- 2026-10-24: task 1 DONE (activity_ext_trip_deposit_carryback [4], activity_ext_trip_balance_carryback [5],
  activity_ext_trip_cancellation [6, owner=user], activity_ext_trip_deposit_release [5, root]); task 0's carry-back
  replaced_by revised for the sibling trip carry-backs (task 0 gates re-run green). Final gate block (no --task):
  EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO,
  SCOPE OK; TRACEABILITY NOT OK only on the 6 unlock tool names (expected before the KB is rendered).
- 2026-10-24: rework round 2 (policy-task audit r1): invented factors removed, P1–P5/F2/F3/O2/O3/O6 closed; factor
  shortfall documented in worklog.md; gates RED only on factor floors (check_extended, check_compute).

## Round 2 (final) redesign — realism_bar AMENDMENT 1 (R6)
Old six policies and tools are retired. The new trees are registration flows on roster-opened participations: the
director's roster opens the participation, and its fees post when the parent submits the signed packet (declared
overwrite of activity_evt_fees S1/S2 for these two types only).
- Task 0 (Esquivel, UIL Academic and Robotics Team, robotics, Ridgecrest MS, grade 07, employee-child transfer,
  roster 2027-01-19, frozen 2027-01-27): root = travel fee posting (agent) [4 honest: activity, level x grade,
  enrollment type, join share + 1 R6 booking lead] <- packet submission posting the participation fee (owner=user)
  [4 honest]. Draw [5,4].
- Task 1 (Lindgren, Fine Arts band, Hollis MS, grade 06, non-resident transfer, district large-instrument checkout,
  roster 2027-01-11, packet 2027-02-02): root = the parent's first installment (owner=user) [2 honest: count,
  travel timing + 2 R6: plan-lead down payment, concert-rush late-fee upfront] <- packet (owner=user) [4 honest +
  1 R6 instrument program], travel fee (agent) [4 honest + 2 R6 booking lead, instrument haul], late fee (agent)
  [3 honest: packet lag, level x grade, enrollment type + 2 R6 concert rush, instrument fitting]. Draw [5,5,4,6].

## Final (rework round 2)
Built: UIL packet/travel (T0 [5,4]); Fine Arts packet/travel/late/first installment (T1 [5,5,4,6]); R6 slots tagged in worklog; gates 7/7 green.

## Rework round 3 plan (audit revision_2: TS, IN, LF, FL, A3, B8, RO)
- RO: scope = exact record test "a <type> participation for the 2026-27 school year whose registration date is after 2026-08-03" (every overwrite, rule, tail); "roster date" -> "registration date" everywhere.
- Join/membership methods re-tiered inside the scope: full within the grace days after the first practice / weekly proration / flat spring share.
- TS: travel trip-season share -> trip share over the team's three scheduled trips (100 before the first; trips left out of three; single-trip pct for the last one). Trip dates are shared by the method and the booking factor (A3).
- B8: drop "(day trips)" and every framing parenthetical.
- IN: instrument_program_tier removed; the FA packet level tier is keyed on grade band only, plus a new campus program tier (R1 campus).
- LF: Fine Arts late fee policy removed; both packet policies overwrite base S2 (a mid-year addition posts no late fee). New 4th T1 problem: Fine Arts concert attire package (uniform_package component; rate by ensemble, grade band, campus, rental term method, concert rush by days to the next concert).
- Installment: late placement -> attire placement; travel placement reads the next scheduled trip.
- T1 draw [5,5,4,6]: packet 5, attire 5, installment 4, travel 6 (R6: late_booking, instrument_haul). T0 [5,4]: travel 5 (R6: booking_lead), packet 4.
- Round 3 built as planned; gates 7/7 green (see worklog "REWORK round 3 claims").
- Round 4: TR (trip-share fall-through = baseline), AT (attire rush-order method + order timing, no proration); gates 7/7 green.
- Round 5: renderer F1 (fee net = latest entry less the three named credit reasons), F2 (Sunflower ECC not elementary), F3 (participation's campus stated); gates 7/7 green.
- Round 6: EN (all 16 enrollment reads select the record in status enrolled for the school year; probes stated); gates 7/7 green.
- Round 7 (seed-only): S1 music checkout due_back_date 2027-05-21 per docs/music; yaml/tools byte-identical; gates 7/7 green.

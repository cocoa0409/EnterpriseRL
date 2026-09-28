# prior_authorization_services — instantiation worklog (M=2)

Category: auth. Blueprint frozen; read domain = this scenario's blueprint + this directory + erlbench + skill files.

## Step 0 — draws (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=2, factor_counts=[4, 6, 6]
- task 1: prerequisite_problems=3, factor_counts=[6, 4, 4, 6]

## Asset ledger / scope plan
Numeric-capable writes of the claimed events: expiry release (auth_units_released), void+release,
provider change (units carried), member extension request, extension (auth_extend), member
deadline extension (auth_timeline_extension), transition-of-care request (auth_submit).
Withdraw / expedite / notice carry no computable parameter, so no problem is built on them.
value_input edges need the dependent's computation to read the holding the prerequisite writes, so:
- task 0 (3 problems): expired BH IOP approval -> expiry release -> transition-of-care request built on
  it (value_input) -> member's own deadline extension on the new request (user tool, value_input).
- task 1 (4 problems): approved PT approval -> provider change (value_input into both) -> member's own
  extension request (user tool, value_input) -> extension (root); void of an overlapping second PT
  approval (state_gate).
Tools (uuid8 minted once each): release_expired_units_43b7942e, record_transition_of_care_request_bf098d50,
request_review_time_extension_2522d00e (user) | void_authorization_7849b1e5,
change_servicing_provider_0d360835, file_extension_request_1d826295 (user), record_extension_d36e0acf.

Owner note: the blueprint names withdrawal as the member's own write; withdrawal carries no computed
parameter, so each task's user write is a request the member makes in person over her/his own case
(requested_by = member): the deadline extension "when the member asks for it" (auth_turnaround) and the
extension request (requested_by member). Recorded as a deliberate deviation for the audit.

Identifier band: phone 4025520000-4025520999, medicaid PR20000000-PR29999999, ssn_last4 2000-2999.
- task 0: Marisela Quintanar-Voss, phone 4025520417, PR24719386, ssn 2638
- task 1: Wendell Achterberg-Sowa, phone 4025520863, PR28056142, ssn 2915

## Log
(per-task details, gate outputs and revisions live in each task's design_rationale)

### Task 0 (closed)
- Tree: auth_ext_expiry_release (4 factors) -> auth_ext_transition_units (6) -> auth_ext_member_review_extension (6, user tool, root).
- Values: release 1 (fall-back 6), transition-of-care units 15 (fall-back 9; 14 without the release), extension days 5 (fall-back 13).
- Revisions: (1) check_extended flagged the module-level helper `_authorization` as an unnamed task tool -> inlined the lookup into each tool; (2) check_compute's cross-category floor looks the target holding up in initial_state, so the deadline-extension computation (which reads only class parameters and cross-category records) targets the earlier approval whose class the new request copies; rationale and factor_trace updated.
- Per-task gates (--task 0): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (closure 23/23), SOLVABILITY OK (7 base gates, 10 seed rows), COMPUTE OK (16 factors, 14 cross-difficulty, 15 history rows, 68 branches, 18 steps), GROUNDING OK, SCOPE OK; CACHE-DIFF info only. check_traceability skipped (KB not rendered).

### Task 1 (closed)
- Tree (root auth_ext_extension_units, 6 factors): <- auth_ext_member_extension_request (6, user tool, value_input), <- auth_ext_provider_carryover (4, value_input into both the request and the extension), <- auth_ext_void_release (4, state_gate). 3 prerequisite problems, 3 value_input edges.
- Values: void 1 (fall-back 5), units carried 2 (fall-back 3), units requested 25 (fall-back 22; 19 without the provider change), units added 11 (fall-back 12; 8 without the provider change). Reordered replay (void after the request) gives the same 25/11.
- Revision: check_compute reported the extension request's history as not load-bearing (zeroing the two-month usage left the rate tier unchanged) -> the weekly-rate ladder now separates "at least one but fewer than twice the cap" from "no use posted, or fewer than twice the cap without a care plan update"; rule, compute, basis, ladder and traces updated together.

## Difficulty-level gates (final run, no --task)
EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK (23/23, 38/38 closure) | SOLVABILITY OK | COMPUTE OK (suite branches mean 70, steps mean 20, history_rows_max 16, branches_max 72) | GROUNDING OK | CACHE-DIFF INFO (optional) | SCOPE OK | check_traceability not run (KB not yet rendered).

## Rework round 2 (policy-task audit round 1: audits/policy_task/prior_authorization_services/)
- F-1: auth_ext_transition_units.overwrite[0].replaced_by now quotes the standard-method sentence plus the six-adjustment sentence (unique merged semantics).
- F-2: auth_ext_extension_units.remaining_units_deduction middle tier now computes the units remaining beyond what the weekly cap delivers before the current end date (new input: whole weeks to end date) - an honest method; auth_ext_member_extension_request's former method-labelled deduction became the parameter factor remaining_units_share (deducted share in halves).
- O-1: transition-of-care standard capped in compute. O-2/O-3: expiry rule covers ended approvals whatever their status (incl. expiry recorded without release); void rule applies only before the end date. O-4: carryover rule states start-date fallback and the four-times-cap boundary. O-5: annual-limit promise removed from the extension rule (base limit inherited; world check: units added equal the annual units left). O-6: kept (state_gate gate as table.field is the skill's allowed form). O-7: overlap prerequisite sentence names same class and, for therapy, same discipline (task 1 edge copied). O-8: care/appeal factors relabelled cross_difficulty null. O-9: class without weekly cap asks for the class allotment. O-10: realism observation recorded; ladders kept.
- Task 1 persona: move no longer volunteered; last Riverbend visit 2026-09-22, late-August Capitol visit and booked 2026-09-29 ride stated consistently.
- Scored values unchanged. Full gate block re-run: EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK | SOLVABILITY OK | COMPUTE OK | GROUNDING OK | CACHE-DIFF INFO | SCOPE OK; check_traceability not run (KB not rendered).

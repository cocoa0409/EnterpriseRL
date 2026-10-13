# Worklog — policy_endorsements_and_renewals (category auto), M=2

## Step 0 — difficulty pre-check
- Read: references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml, products/auto.yaml,
  db_schema.json, share_tools.py (verify threshold K=2 credentials).
- Draw (`draw_counts.py --tasks 2`):
  - task 0: prerequisite_problems=2, factor_counts=[5, 5, 4]
  - task 1: prerequisite_problems=1, factor_counts=[4, 5]
- Compute DSL reach (decisive constraint): history primitives may read only auto tables
  (auto_policies / auto_transactions / auto_change_requests, scoped to the policy). drivers,
  driving_records, vehicles, rating_worksheets are owned by no category and are unreadable by
  compute, so no computation can re-rate a policy from worksheets. Computable quantities are
  therefore premium entries built from figures already recorded on the ledger (full-term
  before/after on endorsement rows, term premium rows, AP/RP rows), flat add-on premiums of other
  products (rental / roadside tier parameters), and cross-category ledgers (billing, physdmg,
  rental, roadside, telematics, sr22).
- Customer-owned writes: the blueprint hands the customer the signature of a cancellation request
  and of a named driver exclusion form; the lifecycle marks in_force -> cancelled as `by: user`
  ("The named insured signs a midterm cancellation request and the cancellation takes effect on the
  requested date"). auto_change_requests carries no amount, so the customer's signature tool is
  designed as the signature that carries out the request (form -> signed, plus the effect it
  carries and its return premium). The base clause "processed only when a signed ... request
  exists" is declared overwritten (signature and processing are one act), sentence by sentence.
- Cross-category trigger note: auto_additional_premium / auto_return_premium declare an untriggered
  `billing:billing_premium_change`. The blueprint explicitly gives premium entries to this
  difficulty's agent ("writes the endorsements, premium entries ..."); the billing posting is the
  billing system's own downstream step and is never written by a task tool. No task tool writes
  auto_vehicle_remove (cross triggers into physdmg/roadside/telematics) and no cancellation is
  written on a policy carrying a filing (sr22 trigger stays off).

## Occupation plan (principle C)
- task 0 (3 problems): insured cancellation refund (customer's signature) <- vehicle removal
  credit (agent) <- rental option removal credit (agent). Tools: record_rental_removal_credit,
  book_vehicle_removal_credit, sign_cancellation_request.
- task 1 (2 problems): named driver exclusion credit (customer's signature) <- driver addition
  premium (agent, AP for a recorded addition). Disjoint policies and tools from task 0.

## Task 0 — closed (Carver, OH)
- Tree: insured cancellation refund (user, 5 factors) <- vehicle removal credit (agent, 5) <- rental
  option removal credit (agent, 4). Gold 3.16 / 214.44 / 207.08; all-standard 12.37 / 452.80 / 257.22.
- Skip runs: removal credit without the option credit 223.95; refund without the removal credit
  285.14; refund without the option credit 204.77.
- Revisions: helper function in task_tools.py read as a tool -> inlined; empty driver_id read as a
  dangling FK -> removed; noise rows (drivers, worksheets) dropped; vehicle lookup added (+1 step).
- Per-task gates: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK.

## Task 1 — closed (Ellison, IN)
- Tree: named driver exclusion credit (user, 5 factors) <- driver addition premium (agent, 4).
  Gold 342.22 / 88.81; all-standard 467.53 / 263.61; exclusion credit without the addition premium 0.00.
- Revisions: signature_start factor had no record read in its bindings -> form-date LATEST added to it;
  addition charge read by LATEST only, failing the history floor -> SUM over the addition row by its
  reference; unread DriveSense score postings dropped; vehicle lookup added (+1 step).

## Difficulty closing
- Coverage: 5 extended policies, 5 task tools, claimed 3 + 2 with disjoint scopes; no policy or
  tool reserved. Both tasks call an owner=user signature tool; no handoff in any gold.
- Prerequisite sentences: refund (affirmative "only after"), removal credit (negated "not ... until"),
  exclusion credit (negated "not ... until") — all state form, each satisfiable by exactly one write.
- Final gates (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK,
  COMPUTE OK (suite branches mean 54.50, steps mean 20.00, history max 12, branches max 75),
  GROUNDING OK, CACHE-DIFF INFO, SCOPE OK. check_traceability deferred until the KB is published.

## Rework round 2 — audit audits/policy_task/policy_endorsements_and_renewals/ (plan)
- G1: the rental-option edge disappears with the rental credit (below); every remaining state-form
  sentence names the exact entry kind ("its own additional premium entry", "its own return premium
  entry"), which no ordinary-lifecycle entry satisfies.
- G2 a-d: no extended policy re-decides a sibling product's premium any more. The rental option
  credit is withdrawn; physical damage / roadside earning and DriveSense grants/recaptures are
  removed; task 0's world becomes liability-only (no PD, rental, roadside, DriveSense holdings) and
  the cancellation rule returns any optional-coverage premium pro rata, applying its return share to
  the remainder only. Task 1 drops the Teen Coach factors and its enrollment row.
- G3: the cancellation gets an honest method factor (effective-date anchor: the signing day when
  the date on the request is earlier); the tenure ladder stays, labelled parameter.
- G4a: all tenure/payment-history haircuts on endorsement credits removed (rental, deletion,
  exclusion credit rates). G4b: DriveSense recapture removed.
- Task 1 finding 2: persona sentence carrying "first" rewritten; no_user_hint rewritten.
- New auto-owned factors: loss-payee notice days (deletion and cancellation), excess-vehicle
  rating, operator assignment, minimum charge period, credit basis on the charge actually written
  (also closes O6: the exclusion/removal credits carry the written AP amount).
- Task 0 tree: cancellation refund (user, 5) <- vehicle removal credit (agent, 5) <- vehicle
  addition premium (agent, 4). Task 1: exclusion credit (user, 4) <- driver addition premium (agent, 5),
  package Plus -> Standard (Plus carries accident forgiveness, which base rating would apply to
  Tyler's first chargeable accident).

## Rework round 2 — closed
- Charter now: auto_ext_vehicle_addition_premium (4 factors), auto_ext_vehicle_removal_credit (5),
  auto_ext_insured_cancellation_refund (5) [task 0]; auto_ext_driver_addition_premium (5),
  auto_ext_named_driver_exclusion_credit (4) [task 1]. Rental option credit and its tool
  (record_rental_removal_credit_1b50ed15) withdrawn; new tool book_vehicle_addition_premium_9393c661;
  sign_cancellation_request_695fb1aa takes cancellation_effective_date; "already" dropped from docstrings.
- Task 0 rebuilt (liability-only Carver world, Kia added/sold, cancellation dated before signature):
  gold 180.41 / 94.27 / 381.16; all-standard 239.76 / 178.83 / 351.85; skip runs 0.00, 420.52, 345.19.
- Task 1 revised (Standard package, no Teen Coach, no billing rows, persona without ordering hint):
  gold 337.99 / 73.16; all-standard 467.53 / 277.48; skip run 0.00.
- Final gates (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK
  (branches mean 31.00, steps mean 14.50, history max 22, branches max 38), GROUNDING OK,
  CACHE-DIFF INFO, SCOPE OK; traceability deferred until the KB is published.

## Rework round 3 (audit revision_2) — 2026-10-05

Open items: R2-P1, R2-P2, R2-F1 (RED) and 1.md r1 finding 6 (claim not borne out, = R2-O2); observations R2-O1, R2-O3, R2-O4, R2-O5 (notice tier 2), R2-O6 addressed alongside.

- R2-F1: minimum_charge_period (VA) and driver_minimum_charge_period (DA) withdrawn; charged days never exceed the days left in the term. Replaced by report-window parameter factors with declared overwrites of the base window sentences: financed_report_window (VA: package newly acquired days +30 loan effective on the purchase date / +14 loan on another date / +0) and member_report_window (DA: household days +15 licensed / +7 moved in, no lapse marker / +0).
- R2-O6: both charge-start ladders now give nil for an addition that took effect before the current term (start = term expiration). Ladders reordered window-first; standard = recorded date.
- R2-O2 / 1.md r1 finding 6: seeds now consistent with the overwritten windows (Kia 21 days in a 44-day window; Tyler 42 days in a 45-day window), so the effective dates on the add rows are the prescribed ones. R2-O1: lateness measured from the addition's effective date in rule and compute.
- R2-P2: both notice ladders speak only of when the payoff "took effect (its effective date, whenever it was recorded)"; tier 2 = days from the credit start / cancellation date to a later payoff, at most 10; none when the lien ended before. Kia payoff reseeded effective 2026-10-01 (recorded 2026-10-02) -> 3 days; persona updated. R2-O4: tier 1 reads "more new loans than loan payoffs".
- R2-O3: VR and EX credit bases divide the written charge by the days it was written for (same window logic).
- R2-P1: VR and EX prerequisite sentences/conditions scoped to additions "during the current term with a premium effect".
- Recomputed (harness on check_compute's evaluator): task 0 VA 183.41, VR 103.73, refund 378.46 (skips 0.00 / 421.78 / 345.19); task 1 DA 346.44, EX 74.99 (skip 0.00). All factors load-bearing; baselines differ from gold.
- Gates (per task and final): EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; CACHE-DIFF INFO; traceability deferred.

## Rework round 4 (audit revision_3) — 2026-10-05

Open items: R3-P1 (task 0) and R3-F1 (tasks 0 and 1).

- R3-P1: financed_report_window and its overwrite of auto_vehicle_changes withdrawn; the vehicle charge-start ladder tests the package's own newly_acquired_additional_report_days, the window every base sentence states, so no base sentence is left unsuperseded. R2-O2 closed by changing the rows instead: the Kia addition and its Ally loss payee entry are now recorded 2026-09-12 (day 11 of Basic's 14).
- R3-F1: financed_report_window (VA) and member_report_window (DA) removed, together with the auto_driver_changes window overwrite. Tyler's addition is now recorded 2026-09-11 (day 28 of Standard's 30); persona says it was called in about four weeks after licensing, around September 11. Each addition policy's two-source loyalty factor is split into tenure-only loyalty plus continuous_coverage_share (lapse marker: none -> whole credit, 36+ months old -> half, newer -> none), which keeps the drawn counts (VA 4, DA 5). Removal and exclusion credit denominators use the base windows.
- Gold unchanged: task 0 183.41 / 103.73 / 378.46; task 1 346.44 / 74.99. New baselines: VA 218.14 (late start 166.88), DA 361.10 (late start 267.58). All factors bear weight.
- Gates (per task and final): EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; CACHE-DIFF INFO; traceability deferred.

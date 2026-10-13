# tire_center_services — instantiation worklog (M=2)

## Step 0 — difficulty pre-check
- Category `tire`; holding `tire_holdings`, event table `tire_services`. Claimed events: tire_install_booked,
  tire_appointment_rescheduled, tire_install_cancelled, tire_set_retired, tire_service_charged,
  tire_service_credited, tire_road_hazard_replaced, tire_treadwear_adjusted.
- Base automatic clauses: tire_installed (system) books the installation_package charge; road hazard / treadwear
  determinations trigger a credit and a replacement_tire charge; no daily accrual, no auto-lock.
- DSL limits found while reading check_compute.py: history primitives are scoped to one package; filters are
  equality only (values may be expressions); item_price_history belongs to no category, so no compute can read the
  current regular price — every computed write is a credit or a Tire Center fee derived from package/tier/ledger
  records, and the current price enters only as a replacement_tire charge already posted by the bay.
- Division of labour adopted for every task world: the Tire Center bay logs the work (rotation, flat repair,
  road hazard / treadwear determination rows with odometer, tread and damage, and the replacement_tire charge at
  the register price); member services posts the money entries that settle a work order (credits, fitting and
  service fees). A determination row's own `amount` is left 0.00 by the bay (stale stamp, never read by any rule).
- Draw (`draw_counts.py --tasks 2`):
  - task 0: prerequisite_problems=2, factor_counts=[6, 4, 5]
  - task 1: prerequisite_problems=1, factor_counts=[5, 4]
- Headroom plan: 5 extended policies / 5 tools in all. Task 0 claims the claim-settlement chain (treadwear-claim
  fitting charge -> treadwear credit -> road hazard credit, the root accepted by the member). Task 1 claims the
  paid-service chain on a Mount & Balance package (rotation charge authorised by the member -> flat repair charge).
  Disjoint by construction: credits and claim fitting vs. rotation and flat-repair fees.
- Tool names (uuid4().hex[:8] drawn once per tool):
  post_claim_fitting_charge_0bdb2547 (agent), post_treadwear_credit_0e44552f (agent),
  accept_road_hazard_credit_d64b14f0 (user), authorize_rotation_charge_d4760d29 (user),
  post_flat_repair_charge_9a2582c0 (agent).

## Task 0 — closed
- Tree: tire_ext_road_hazard_credit (root, user) -> tire_ext_treadwear_credit (value_input) -> tire_ext_claim_fitting_charge (state_gate).
- Gold: fitting 6.49 (baseline 31.99), treadwear 88.35 (baseline 78.57), road hazard 53.95 (baseline 112.49); skip-treadwear -> 112.33.
- History credit 2025-03-24 = 117.00 re-derived by the road hazard rule on the world of that day.
- Per-task gates (--task 0): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- r1 docstring rounding wording fixed; r2 treadwear baseline.params -> [].

## Task 1 — closed
- Tree: tire_ext_flat_repair_charge (root, agent) -> tire_ext_service_rotation_charge (value_input, user tool).
- Gold: rotation 20.51 (baseline 19.99), flat repair 7.04 (baseline 15.00); skip rotation -> 14.07.
- History charges re-derived on their own days: 7.60, 6.84, 9.60 (flat), 8.55.
- Per-task gates (--task 1) all OK. r1: persona clause about the earlier patch removed.

## Final difficulty-wide gates (no --task)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 21/21, 1.json 25/25 closure match); SOLVABILITY OK;
  COMPUTE OK (suite means branches 40.50, steps 12.50; history_rows_max 15; branches_max 55); GROUNDING OK;
  CACHE-DIFF INFO (no quantity fields); SCOPE OK.
- check_traceability NOT OK, expected: the five task-tool names reach the agent only through the published KB
  (docs/), which is rendered later; re-run after erl-kb-doc-render.
- Temporary authoring helpers (_calc.py, _build_t*.py, _gold_t*.py, _finish_t*.py, _rat_t0.py, id maps) deleted.

## Rework round 2 (audits/policy_task/tire_center_services)
- D-F1 (task 1): overwrite entries added — rotation: tire_lifetime_services 'Rebalancing is free ... per tire' and
  'Each fee is its own entry on the visit's service date'; flat repair: the same two plus tire_installation_charges'
  tpms_service_kit clause; each replaced by an explicit rule sentence (folded fees are not separate entries and not
  priced at their own fees). solvability policy_scope conditions rewritten. Amounts unchanged (20.51, 7.04).
- D-F2 (task 0): treadwear_rotation_factor now reads the average rotation interval (<=5000 / <=7000 / above);
  fall-through reachable by admitted claims. Value unchanged (1.05).
- D-F3 (task 0): treadwear_price_paid ladder removed (price paid net of purchase credits is the baseline method);
  new factor treadwear_membership_years_allowance (16 fee charges seeded, read at new step 8). road_hazard_price_basis
  rebuilt with three distinct sources. Gold: treadwear 100.35, road hazard 46.02; writes at steps 10/12/14.
- O-6: fitting replacement count stated as 'whatever their service dates'. Task 1 obs 3: sale line seeded and read
  (find_order_lines, step 5); writes at steps 9/11.
- Full gate block re-run: all OK except check_traceability (only the five task-tool names; KB not rendered).

## Rework round 3 (audit revision_2)
- R2-T0-1: task 0 rationale section 6 seed-sensitivity figure 92.96 -> 104.96; rotation-removal reason restated on the
  average-interval ladder (7888.8 > 7000).
- R2-T0-2: task 0 rationale section 4 write steps 9/11/13 -> 10/12/14.
- R2-T1-1: task 1 rotation write cited as step 9 (was 8) in prerequisite_closure (flips_to_true_by, edge_load_bearing),
  computations[1].factor_trace, evaluation_criteria[11] tracing, design_rationale.
- R2-O1: rotation / flat repair replacement sentences now scoped ("every other Tire Center fee ... remains its own entry").
- R2-O2: treadwear rotation count stated "whatever their dates (a rotation entry dated after the claim entry counts too)".
- R2-O3: road hazard price basis tier 2 = one or more earlier road hazard replacements on the wheel, average net cost.
- Gold unchanged (6.49 / 100.35 / 46.02; 20.51 / 7.04). Full gate block re-run.

## Rework round 4 (audit revision_3)
- R3-D-F4: universal "every other Tire Center fee remains its own entry" clauses in the rotation and flat repair rules
  (rule, overwrite replaced_by, compute_basis) replaced by scoped clauses: each exception governs only its own entry, the
  make-up of every other entry follows the rule that books it, and an unfolded fee (e.g. installation sensor kits) stays
  its own entry. Single readings: 20.51 / 7.04.
- Task 1 rationale near-miss 17.09 -> 17.10 (recomputed). Task 0 rationale tenure near-miss restated (-3 months -> 9.73).
- R3-T0-O1: step-14 tracing wording now matches the persona (sidewall bulge).
- R3-O1: averaging kept with a stated business reason; R3-O2 unchanged (disclosed in the rule).
- Every figure in both task files' self-describing fields recomputed with a scratch replay (outside the repo).

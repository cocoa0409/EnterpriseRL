# road_hazard_claims (hazard) — instantiation plan / worklog

## Step 0 draws (draw_counts.py --tasks 2)
- task 0: prerequisite_problems=2, factor_counts=[5,6,6]
- task 1: prerequisite_problems=2, factor_counts=[5,4,4]

## DSL constraints found (drive the design)
- compute reads only: this certificate's fields/events, tier params, policy K params, OTHER categories'
  holdings/events. No own-category cross reads (check_extended rejects), no vehicles/stores reads.
- => a value_input edge must come from a write on the SAME certificate the root computes on.
- => every scored number must be derivable from DB rows; receipt figures (caller documents) can only
  decide scope, never enter compute. Out-of-area reimbursements are therefore scoped to receipts at or
  above the plan cap (self-naming overwrite), the cap being the quantity the factors act on.
- LATEST is not zeroed by the history floor; at least one SUM/COUNT/MAX must bear weight per computation.
- hazard_cancellation_refund with payment_method crestline_card/fleet_account triggers card/fleet: every
  certificate whose refund we write is paid cash_or_debit or bank_card.
- No date-valued computations (near() is string-equal for dates; DSL has no date builder).

## Tree decision
User-owned computable writes available: holder cancellation of an active certificate (base: holder confirms).
Two disjoint cancellation situations exist in base refund ordering: covered set still in service (pro_rata /
full window) vs covered set returned under the satisfaction trial (covered_set_returned). One user tool each.

Task 0 (root = pro-rata cancellation, user):
  R0 hazard_ext_holder_cancellation_refund  <- P1 hazard_ext_outside_replacement_reimbursement (value_input: benefits paid)
  P1 <- P2 hazard_ext_outside_tow_reimbursement (state_gate: occurrence claim number opened by the earliest service = tow)
Task 1 (root = returned-set refund, user):
  R1 hazard_ext_returned_set_refund <- P3 hazard_ext_outside_repair_reimbursement (value_input: benefits paid)
  R1 <- P4 hazard_ext_store_replacement_share (value_input: benefits paid)

## REVISED tree decision (supersedes the block above) — reasons
- A pro-rata cancellation refund deducts benefits paid, so a store/out-of-area REPLACEMENT share feeding a
  cancellation floors the refund at 0 unless the certificate price is high and the shares are prorated small.
  Life-of-Tread (72 months, 22%, max 64.99/tire, spare covered) is the only plan with enough refund headroom.
- Two tread-based store-replacement computations in one task collide on "latest technician damage reading";
  the out-of-area replacement therefore reads the position's latest ROUTINE reading (wear_pattern even), the
  counter replacement reads the DAMAGE reading: distinct filters.
- Tow / repair reimbursements are thin (cap-bounded): they go to task 1 whose draw is 4,4.
- Two user tools: holder cancellation split by plan family (Life-of-Tread refunds on a usage share; term
  plans on months) — two disjoint policy scopes, two tools.

Task 0 (draw 5,6,6) — Life-of-Tread holder cancels (vehicle moved into business use):
  R0 hazard_ext_lot_cancellation_refund (user, 5)  <- P1 hazard_ext_counter_replacement_posting (agent, 6) [value_input: benefits]
  R0 <- P2 hazard_ext_outside_replacement_reimbursement (agent, 6) [value_input: benefits]   (P1,P2 commute)
Task 1 (draw 5,4,4) — term-plan holder cancels:
  R1 hazard_ext_term_cancellation_refund (user, 5) <- P3 hazard_ext_outside_repair_reimbursement (agent, 4) [value_input]
  P3 <- P4 hazard_ext_outside_tow_reimbursement (agent, 4) [state_gate: the breakdown's claim number, opened by the tow]

## FINAL tree (supersedes both blocks above; resumed after account cut)
Why changed: replacement-sized benefits floor a cancellation refund to 0 unless the plan is Life-of-Tread
(5 tires x 64.99, 72-month term); thin cap-bounded reimbursements (tow, repair) cannot carry 6 factors,
so they go to task 1 (draw 4,4); task 1's user write is the holder's own authorization of a store
replacement (the holder accepts the prorated replacement — a confirmation over their own affairs).

Tools (uuid8 generated once each):
  confirm_life_of_tread_cancellation_58ab2fcf   user   (task 0 root)
  post_hazard_counter_replacement_324c4972      agent  (task 0)
  reimburse_hazard_outside_replacement_5f5d3272 agent  (task 0)
  authorize_hazard_store_replacement_0d9adf2d   user   (task 1 root)
  reimburse_hazard_outside_repair_444e27b0      agent  (task 1)
  reimburse_hazard_outside_tow_3bff1c36         agent  (task 1)
Task 0 (5,6,6): R0 hazard_ext_lot_cancellation_refund <- P1 hazard_ext_counter_replacement_posting [value_input]
                R0 <- P2 hazard_ext_outside_replacement_reimbursement [value_input]; P1/P2 commute.
Task 1 (5,4,4): R1 hazard_ext_store_replacement_authorization <- P3 hazard_ext_outside_repair_reimbursement
                [value_input: the position's repair count selects the coverage route]
                P3 <- P4 hazard_ext_outside_tow_reimbursement [state_gate: the breakdown's claim number is the
                one the tow opened]
Scratch design/simulation: /tmp/road_hazard_claims_0062/design.py

## Task 0 factor plan (committed)
R0 lot cancellation refund (6): clock_start_fx[M, fleet roster: enrolled & not removed -> enrollment date | pending
  cancellation request -> its date | cancellation date]; day_count_fx[M, in force <12m actual days | 12-35m 30-day
  months | calendar months]; tread_life_fx[P, tires routine reading usable share <=25% x0.5 | <=50% x0.8 | x1];
  cancel_fee_fx[P, card open & no late fee 12m -> 0 | open & late fee -> reduced | plan fee];
  roadside_credit_fx[P, unused calls & none used -> K1/call | some used -> K2/call | 0];
  bundle_clawback_fx[P, alignment plan sold on the certificate's ticket -> K1 | alignment bought separately within 30d -> K2 | 0]
P1 counter replacement posting (6) & P2 out-of-area replacement (6): price/tread selection methods + coverage
  points (card perk, care club rotations, tire-and-alignment bundle, prior covered repairs on the position).

## Progress log
- task_tools.py: 3 task-0 tools written; TASK TOOL CONTRACT OK (fixed unit wording for odometer/tread).
- hazard.extended.yaml assembled from scratch fragments (frag/r0,p1,p2.yaml) by assemble.py; base text copied verbatim.
- check_extended: structure clean (only "no tasks yet" fails at that moment).
- check_compute first run: recompute == expected for all three; card factors failed "no card rows touched" ->
  seeded a 2024-06-08 card late fee (outside the 12-month window: also the near-miss for the card tiers).
- factor sensitivity (task 0): P1 110.70 (baselines 114.80/97.20/102.60/99.90/121.50; all 92.40);
  P2 75.60 (269.99/56.00/77.00/67.50/64.80/86.40; all 200.00); R0 56.43 (54.87/55.50/95.73/31.43/16.43/76.43; all 45.37)
- TASK 0 CLOSED (all 7 per-task gates green). Build chain (scratch): t0_world.py -> t0_task.py -> t0_trace.py ->
  t0_text_a/b/c/d.py -> t0_build.py; policy fragments p1.py/p2.py/r0.py -> assemble.py.
  Probe table + revisions recorded in tasks/0.json design_rationale.

## Task 1 plan (draw 5,4,4)
R1 hazard_ext_store_replacement_authorization (user authorize_hazard_store_replacement_0d9adf2d, 5 factors)
P3 hazard_ext_outside_repair_reimbursement (reimburse_hazard_outside_repair_444e27b0, 4)  [value_input: repair count]
P4 hazard_ext_outside_tow_reimbursement (reimburse_hazard_outside_tow_3bff1c36, 4) [state_gate: breakdown claim number]
- Task 1 policies written (frag r1/p3/p4 via r1.py, p34.py); 6 tools in task_tools.py (gate OK).
- Hygiene fix: every out-of-area policy is scoped to a receipt that COVERS its computed allowance/base (so the
  plan never pays more than the receipt); task 0 receipt raised to tire 289.50 (+26.50 mounting = 316.00).
  P1/R1 both retire the same two hazard_evt_replacement clauses: each replaced_by is its scope sentence naming
  the sibling case. P2/P3/P4 all retire the out-of-area sentence: each tail names the other two cases.
- Task 0 re-run after these changes: all 7 per-task gates green.

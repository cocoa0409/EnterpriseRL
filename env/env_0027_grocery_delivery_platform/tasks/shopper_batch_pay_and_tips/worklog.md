# Worklog — shopper_batch_pay_and_tips (category batch), M=2

## Step 0 — difficulty pre-check
- Read references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml, products/batch.yaml, db_schema.json, share_tools.py, gate scripts.
- Draw (draw_counts.py --tasks 2):
  - task 0: prerequisite_problems=3, factor_counts=[4, 5, 5, 4]
  - task 1: prerequisite_problems=2, factor_counts=[4, 4, 5]
- => 7 extended policies, 7 task tools (4 in task 0, 3 in task 1), >=1 owner=user tool per task.
- DSL constraints noted: SUM/COUNT/MAX/LATEST are scoped to the one batch (holding pk batch_id);
  batch_pay_disputes is a batch intake table so it is readable per batch; X* reads other categories
  only for rows with customer_id = shopper's profile (shopper_events, payout_events, ...).
- Identity preamble: find_customers at step 0, verify_customer_identity (>=2 of phone/email/dob/zip) at step 1.
- Identifier band: phone 6175540000-6175549999, email @postloft.com, last4 6000-7999, surnames N-R.
- Note on event triggers: every batch money event (pay posted/adjusted/reversed, tip changes) declares a
  payout earnings trigger with no `when`; the blueprint nevertheless assigns these writes to this difficulty
  ("the agent computes and books owed adjustments"). Task tools write only batch tables (batches,
  batch_events, batch_pay_disputes) and never a payout row; the downstream payout credit is the platform's
  declared consequence, not a write of this difficulty.

## Difficulty-level plan (space budget, Principle C)
Write types available in the batch category without touching another category's tables:
batch_pay_posted, batch_pay_adjusted, batch_pay_reversed (batch_events), batch_pay_disputes (intake).
Tip rows need order rows whose ordering customers would sit outside any read closure, so no tip write is claimed.
Seven tools (frozen names):
- task 0: post_pay_component_6b97a1a8 (agent), reverse_duplicate_pay_33b66c45 (agent),
          submit_pay_dispute_0c2b2ed2 (user), book_pay_adjustment_e97659e1 (agent, root)
- task 1: reverse_undelivered_pay_ec14645c (agent), submit_cancellation_claim_9760e860 (user),
          book_cancellation_adjustment_6678c254 (agent, root)
Split rationale: completed-batch shortfall flow (task 0) vs canceled-mid-shop flow (task 1); the two reversal
tools differ by ground (duplicate_pay vs order_not_delivered_verified, fixed inside each tool).

## Task 0 thesis
Surface: shopper Nadia Pereira says her Triple Delivery Batch paid less than the offer showed.
Tree (4 problems; draw 3 prerequisites, factor counts [4,5,5,4]):
- root batch_ext_shown_pay_adjustment (book_pay_adjustment, agent, 4 factors) <- value_input (claimed amount on
  the shopper's shown-pay dispute)
- batch_ext_shown_pay_claim (submit_pay_dispute, USER, 5 factors) <- value_input (pay standing) from both:
  - batch_ext_long_distance_bonus (post_pay_component, agent, state_due, 5 factors): bonus missing at opening
  - batch_ext_duplicate_recovery (reverse_duplicate_pay, agent, state_due, 4 factors): mileage posted twice
Order: {long_distance_bonus, duplicate_recovery} (commute) -> shown_pay_claim -> shown_pay_adjustment.
- Step 1 (task 0): four policies written to batch.extended.yaml (long_distance_bonus, duplicate_recovery,
  shown_pay_claim, shown_pay_adjustment). Prerequisite sentences: claim <- bonus (state, affirmative
  "fixed only after"), claim <- duplicate (state, negated "not worked out until"), adjustment <- claim (state,
  affirmative "booked only after").
- Step 2 (task 0): task_tools.py written with the four task-0 tools; helpers inlined (check_extended counts every
  module-level def as a tool). check_task_tools: TASK TOOL CONTRACT OK.
- Step 3/5 (task 0) handling-time recomputation (scratch evaluator reusing check_compute's build_env/eval_compute):
  long_distance_bonus 4.55 (factor baselines 4.22/4.00/3.63/3.67/4.14, all-baseline 2.00);
  duplicate_recovery 2.37 (2.87/2.50/2.52/4.75, all 6.30); shown_pay_claim 3.65 (6.56/4.83/3.15/3.39/3.15, all 6.57);
  shown_pay_adjustment 6.13 (5.94/4.55/5.60/5.83, all 3.65).
  Fix found on the way: ceil written as -int(-x) is a floor in Python; replaced by -(-x // 1) in both method factors
  (duplicate cash-out 0.75 tier, card method 1.05 tier); adjustment moved 6.12 -> 6.13.
- Step 4 (task 0): persona drafted in .build/t0_persona.txt (assembled into tasks/0.json).
- Revision (task 0): the two mileage postings shared one date, so "the later posting" named no unique row -> the
  re-post is dated 2026-03-18; values now 4.55 / 2.45 / 3.73 / 6.22; instant cashout lowered to 25.00.
- tasks/0.json written (assembled from .build/t0_persona.txt, .build/t0_rationale.txt and the scratch evaluator).
- Per-task gates task 0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK. Task 0 closed.

## Task 1 thesis
Surface: shopper Omar Rashidi's Double Delivery Batch was canceled by both customers while he was shopping; he
wants the cancellation pay he is owed. Draw: prerequisite_problems=2, factor_counts=[4,4,5].
Tree (chain): root batch_ext_cancellation_adjustment (book_cancellation_adjustment, agent, 5 factors)
 <- value_input batch_ext_cancellation_claim (submit_cancellation_claim, USER, 4 factors)
 <- value_input batch_ext_undelivered_recovery (reverse_undelivered_pay, agent, state_due, 4 factors): the system
    posted completion base pay on the canceled batch (orders never delivered).
- Task 1 re-scope (before any task-1 asset was written): base batch_evt_clawback.clawback_window and
  batch_evt_pay_disputes.dispute_window both anchor on batches.completed_date, which a canceled batch never
  carries, so neither a reversal nor a cancellation-pay adjustment could be shown in-window on a canceled batch.
  Task 1 moves to a completed Double Delivery Batch: the shopper disputes mileage (driven route far above the
  estimate); a wrong-address violation against the batch verifies one order was not delivered, so that order's
  share of the mileage must first be taken back (ground order_not_delivered_verified).
  Tools: reverse_undelivered_pay_ec14645c (kept), submit_cancellation_claim_9760e860 and
  book_cancellation_adjustment_6678c254 are dropped unwritten and replaced by freshly generated names (below).
- Step 1 (task 1): policies batch_ext_undelivered_recovery (4 factors), batch_ext_mileage_claim (4),
  batch_ext_mileage_adjustment (5) appended. Mileage claim declares an overwrite of the base mileage_underpaid
  sentence; both adjustments now declare the overwrite of the base "owed amount" sentence (shown-pay adjustment
  gained that second entry in the same pass).
- Step 2 (task 1): three task-1 tools appended to task_tools.py; TASK TOOL CONTRACT OK (7 tools).
- Step 3/5 (task 1): world in scratch t1_world.py (Double Delivery Batch, estimated 7.4, driven 12.2, Silver 27 months,
  3 points from a wrong-address violation on the batch, ratings 5 and 2, Instant Cashout plan with a 0.50 fee).
  First pass (driven 12.0) put the claim on an exact half cent (3.065); driven moved to 12.2 to keep every scored
  value off a half-cent tie. Values: undelivered_recovery 1.54 (baselines 0.58/2.10/1.94/1.84, all 1.60);
  mileage_claim 3.16 (3.05/4.29/2.74/2.96, all 3.38); mileage_adjustment 4.83 (5.00/4.31/4.42/4.05/4.65, all 3.16).
  Edges: claim without the reversal 1.62; adjustment without the claim 0. Terminal batch earnings 18.99.
- Step 4 (task 1): persona in .build/t1_persona.txt.
- tasks/1.json written (assembled by the scratch builder from .build/t1_*.txt).
- Per-task gates task 1: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK. Task 1 closed.

## Final difficulty closing (both tasks)
- Union: 7 extended policies, each claimed by exactly one task; task scopes and tools pairwise disjoint
  (task 0: 4 policies / 4 tools, task 1: 3 policies / 3 tools); both trees end at a root the shopper asked for, and
  each gold calls exactly one owner=user tool (submit_pay_dispute_0c2b2ed2, submit_mileage_claim_29030431).
- Prerequisite sentences: 4 edges, all state form, directions affirmative x2 (task 0) and negated x2
  (one in task 0, both in task 1); no sentence names a tool, id or code token (rules scanned: no snake_case token).
- Final gate run (no --task; traceability deferred until the KB is published): EXTENDED OK, TASK TOOL CONTRACT OK,
  REPLAY OK, SOLVABILITY OK, COMPUTE OK (suite means branches 59.50, steps 16.00; history_rows_max 13;
  branches_max 67), GROUNDING OK, CACHE-DIFF INFO (no cache trap chosen), SCOPE OK.
- Cleanup: temporary .build/ inputs (persona and rationale drafts, now inside tasks/*.json) and __pycache__
  removed from the write domain; the scratch builders live outside it.
- Known tension, recorded for the audit: every batch money event declares a payout earnings trigger with no
  `when`, so the claimed batch writes (reversal, posting, adjustment) carry a declared downstream payout effect;
  the tools write only batch tables, as the blueprint's own difficulty summary assigns these writes here.

## Rework round 2 (audit env/env_0027_grocery_delivery_platform/audits/policy_task/shopper_batch_pay_and_tips/)
Plan per item: F1/T0-1 (LD extension becomes two genuinely different formulas), F4 (LD amount and MC rate ladders
become increments over the type value), F2/T1-1 (UR distance method removed; new payout settlement method; timing
ladder without the scope-restating clause; recovery base read from the one mileage posting, O9), F3/T1-2 (detour
method rebuilt as three distinct methods), T1-3 (an expired, cleared violation seeded as the near-miss for the
point-based ladders), T1-4 (all baseline figures checked in exact decimals, no half-cent tie), T0-2 (task-0
rationale regenerated), O3 (MA declares the mileage_underpaid supersession too), O8 (completed-or-finalized wording).
- F4: ld_amount_by_points and mc_claim_rate ladders now read type value + 1.00/+0.50 (LD) and type rate + 0.10/+0.05 (MC), so no tier equals the fall-through on any batch type (batch.extended.yaml rule, compute, basis, ladder).
- F2/T1-1: batch_ext_undelivered_recovery rewritten: the delivery-distance method (scope-restating tiers, driven-mile recomputation) is removed; recovery base is the not-delivered share of the one mileage posting (LATEST, closes O9); timing ladder keyed on day span only; new method ur_settlement_method (cash-out + fee-charging plan: x0.75 down / halve up / full) over payout records; 4 factors, 1 method.
- F1/T0-1: batch_ext_long_distance_bonus.ld_route_extension now applies two different formulas — tier 1 (no late
  delivery) 0.25 per estimated mile beyond the threshold that applies; tier 2 (late delivery) a proportional
  extension, bonus amount x (miles beyond the threshold that applies) / that threshold, rounded down to the ten
  cents; fall-through none (rule, compute ld_extension, basis, ladder; param ext_rate_late removed). The first
  replacement tried (one fifth of the route's mileage pay) made ld_threshold_by_standing decorative on the task-0
  world (baseline = gold 5.02) and was replaced in the same pass. Task-0 values: LD 5.50, DR 2.45 (unchanged),
  claim 2.78, adjustment 5.17; all figures checked in exact decimal half-up (no tie).
- T0-2: tasks/0.json design_rationale [2] (sibling scope now names UR/MC/MA and their real tools) and [4]
  (single-write argument for the duplicate edge now states that the not-delivered reversal acts on completed
  batches against a mileage posting but only on the not-delivered ground where a wrong-address violation exists)
  rewritten; [5], [10]-[15], tracing (steps 10/14/16), objectives, business_effect, factor_trace, tier_taken and
  prerequisite_closure texts regenerated from the recomputation.
- F2 follow-up: UR's recovery base reads the latest mileage posting, which check_compute's history-zeroing floor
  does not zero; a count of mileage postings was added (rule and baseline: "a batch carrying no mileage posting
  has nothing to take back on this ground"), making the ledger read load-bearing. COMPUTE OK after the change.
- F3/T1-2: batch_ext_mileage_claim.mc_detour_exclusion rebuilt with three distinct methods — wrong-address
  violation recorded: prorate by delivered/all orders, rounded down to a tenth (a single-order batch gives none
  within the same formula); no wrong-address but a late delivery: halve, rounded down to a whole mile; otherwise
  all count (rule, compute with new binding mc_late, basis, ladder).
- T1-3: tasks/1.json initial_state gains the shopper's older dropped Single Delivery Batch (2026-01-20, shopper
  choice, no earnings), its batch_dropped violation (2 points) and the expiry clearing (2026-04-20); the recorded
  points sum to 5 while the active balance is 3 — the near-miss for mc_claim_rate (also ur_standing_share and
  ma_approval_share). seed_consistency covers the new batch row.
- T1-4: every gold, per-factor and fall-back figure is now recomputed with float and with exact decimal half-up
  rounding in the scratch kit; the task-1 batch moved to estimated 7.6 / driven 12.4 miles (mileage posting 3.30)
  because a 0.50 rate over a route ending in an odd hundredth always sat on a half cent. New values: UR 0.72,
  claim 2.35, adjustment 4.03; fall-backs 1.65 / 2.55 / 2.35; no tie anywhere. Persona figures updated to 12.4 /
  7.6 / $3.30; every text field of tasks/1.json regenerated.
- O3: batch_ext_mileage_adjustment now also declares the supersession of the base mileage_underpaid sentence.
- O8: MC and MA rules state that a batch whose pay has been finalized still counts as completed.
- O9: closed with F2 (the recovery base is the one mileage posting, LATEST).
- O1, O2, O4, O5, O6, O7 (observations, no scoring consequence): unchanged by design — O1/O2 the base dedup
  contracts force adjustment_reason/pay_component-style arguments on every tool of a write type; O4 no world
  combines both reversal triggers; O5/O6 accepted by the audit; O7 tip writes need order rows whose ordering
  customers could not enter any read closure.
- Final gate block after rework round 2 (no --task; traceability deferred): EXTENDED OK, TASK TOOL CONTRACT OK,
  REPLAY OK (0.json 17 acts closure 22/22; 1.json 15 acts closure 22/22), SOLVABILITY OK, COMPUTE OK (suite means
  branches 62.50, steps 16.00; history_rows_max 13; branches_max 68), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.
  Scratch folder scratchpad/shopper_batch_pay_and_tips/ deleted; __pycache__ removed from the write domain.

## Rework round 3 (audit revision_2 sections)
- N1 (late-delivery tier of ld_route_extension outpaid the on-time tier): tiers swapped in kind. On-time tier
  (no late-delivery violation, route >= 3.0 miles beyond the type threshold) = proportional growth of the bonus
  amount (amount x miles beyond the threshold that applies / that threshold, rounded down to the ten cents);
  late tier = 0.10 per whole estimated mile beyond the threshold that applies (part miles not counted); otherwise
  none. Since type bonus / type threshold is 2.00/10 or 3.00/15 and the other ladders only raise the amount or lower
  the threshold, the on-time tier yields >= 0.20 per mile while the late tier yields <= 0.10, so lateness never
  raises the bonus on any batch type (batch.extended.yaml rule sentence, ld_extension, basis, ladder; param
  ext_rate_ontime removed, ext_rate_late 0.1 added). Task 0: LD 4.18 (the same shopper on time: 5.50).
- Knock-on (T1-4 discipline): the new claim 4.10 put SA's card-method fall-back on a half cent (4.10 x 1.05);
  batch_ext_shown_pay_adjustment's upper rating tier 1.05 -> 1.04 (param, rule, basis, ladder). Task-0 values:
  LD 4.18, DR 2.45, claim 4.10, adjustment 6.58; every gold/sensitivity/fall-back figure checked in exact decimal
  half-up, no tie. tasks/0.json rationale [4]-[6], [10]-[15], tracing, objectives, business_effect, factor_trace,
  tier_taken and prerequisite_closure regenerated. Task 1 untouched (all PASS in revision 2).
- O10 (base mileage_underpaid sentence superseded in both MC and MA): observation, unique merged semantics; kept.
- O1, O2, O4, O5, O6, O7: unchanged observations (reasons in round 2).
- Final gate block after round 3: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK (traceability deferred). Scratch folder deleted; no __pycache__ in the write domain.

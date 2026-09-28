# Worklog — shopper_ratings_and_deactivations (category: shopper), M=2

## Step 0 — difficulty pre-check (round 1)
- Read skill references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml, products/shopper.yaml,
  db_schema.json, share_tools.py (verify threshold: 2 matching details; customer_id never counts).
- Draw (draw_counts.py --tasks 2):
  - task 0: prerequisite_problems=3, factor_counts=[5, 6, 4, 6]
  - task 1: prerequisite_problems=3, factor_counts=[4, 4, 6, 5]
- Writable tables of this category: shopper_accounts, shopper_events, shopper_appeals.
- DSL constraint noted: SUM/COUNT/MAX/LATEST are scoped to shopper_account_id=HID; cross reads (CFIELD/CPARAM/X*) are
  scoped to customer_id=CUST (the shopper's own profile) -> the delivered orders (other customers') are NOT readable
  by compute; batches/batch_events/payout_* ARE (customer_id = shopper). Factor evidence therefore comes from the
  shopper ledger, the account fields, tier params, and the shopper's batch and payout records.
- Numeric/date write fields available: shopper_events.points, shopper_events.event_date, shopper_accounts dates,
  reactivation_count, violation_points_balance. shopper_appeals carries no numeric field.

## Design decision (round 1)
- Every scored parameter must be a number written to a field and must be computable by the DSL from records the DSL can
  read (the shopper ledger, the account, tier params, the shopper's own batch/payout records). The DSL has no date
  arithmetic that returns a date, so every scored value is an integer count of violation points (shopper_events.points).
- Charter concept: for each of four violation types the charter carries one SEVERITY policy (the points an owed
  violation is booked with, agent) and one EXCUSAL policy (the points a record-decided dispute removes). Assessment and
  excusal of one type sit in different tasks, so no task claims both sides of one type.
  - task 0: root = shopper's own in-app dispute of the most recent late-delivery violation (user, late EXCUSAL);
    prereqs = drop SEVERITY (agent), wrong-address SEVERITY (agent), missing-items EXCUSAL of the pending dispute (agent).
  - task 1: root = shopper's own in-app dispute of the most recent dropped-batch violation (user, drop EXCUSAL);
    prereqs = late SEVERITY (agent), missing-items SEVERITY (agent), wrong-address EXCUSAL of the pending dispute (agent).
- Every root excusal carries a benefit-of-the-doubt factor over the account's other standing points (recorded minus
  cleared, the disputed violation excluded): the three prerequisite writes each move that figure -> value_input edges.
- Tool names (uuid8 generated one per tool, frozen):
  record_dropped_batch_violation_61b8c422 (agent), record_wrong_address_violation_db63d782 (agent),
  decide_missing_items_dispute_36c35ef8 (agent), dispute_late_delivery_violation_c2c67d58 (user),
  record_late_delivery_violation_939f2196 (agent), record_missing_items_violation_e43bab28 (agent),
  decide_wrong_address_dispute_4037a75e (agent), dispute_dropped_batch_violation_598e80dc (user).
- Task 0 tree (draw: 3 prereqs, factors [5,6,4,6]): root late excusal (5) <- missing excusal (4) [value_input],
  root <- wrong-address severity (6? no: 4) ... final allocation: drop severity 6, late excusal 5, missing excusal 4,
  wrong-address severity 6. Chain: root <- wrong-address severity <- drop severity (track-record count pins order).
- [saved] task-0 policies on disk: shopper_ext_dropped_batch_severity (6), shopper_ext_wrong_address_severity (6,
  <- dropped severity), shopper_ext_missing_items_excusal (4), shopper_ext_late_delivery_excusal (5, root, <- missing
  excusal, <- wrong-address severity). Task-0 tools on disk; TASK TOOL CONTRACT OK after each addition.
- Next: task-0 seed via a scratchpad builder script, then run compute gate and tune numbers.
- [saved] tasks/0.json initial_state (SEED-FRESH, uuid4 ids; customers 4, shopper_events 21, batches 13, batch_events 44,
  orders 15, order_events 2, payout 1+3, appeals 2) and evaluation_criteria draft (8 reads + 4 unlock/call pairs).
- Revision: clawback thresholds 15/8 USD -> 5.0/2.5 USD (symptom: clawback_size_surcharge decorative on the 3.00
  reversal; cause: thresholds above any per-order pay component; re-run: W0 = 2).
- Handling-time sensitivity run (scratchpad sens.py, gate functions): A0=2 (factor baselines 0/1/1/3, all 0);
  R0=3 (4/1/2/2/2/5, all 2); W0=2 (4/1/0/1/4/3, all 3; skip R0 -> 1); U0=4 (3/3/3/2/5, all 0; skip A0 -> 3, skip W0 -> 5).
- Revision (replay closure/FK): symptom: replay flagged 96 dangling FKs ("" ids) and 22 seed rows outside the read
  closure (other customers, their orders, order_events, payout events). Root cause: ratings/violations referenced
  other customers' orders, which no justified read touches. Change: the world carries no order rows; ratings and
  violations reference the batch only (order_id null); wrong-address severity now keys on the reversal's batch
  (tool takes batch_id, no order_id; harm tier counts 1-star / 2-3-star ratings on that batch); missing-items feedback
  reads the latest rating on the disputed violation's batch; empty FK fields are null; read find_payout_events added.
  Re-run: A0=2, R0=3, W0=2, U0=4 unchanged; sensitivities unchanged.
- [saved] task 0 design_rationale written; all task-0 per-task gates green (replay, solvability, compute, grounding, scope, extended, tools).
- REDESIGN (before task 1): symptom: the task-0 seed carried a 5-point late-delivery violation and 3-point missing-items
  violations, but no policy of the charter can book late or missing-items severities (their owed-evidence lives in other
  customers' orders, outside any world), so base points apply (late 1, missing 2) -> the seed contradicted the charter,
  and a 1-point late violation cannot carry a 5-factor excusal. Change: the eight policies are
  dropped-batch severity, wrong-address severity (owed, agent), and six record-decided excusals: missing-items (pending,
  agent), conduct-complaint (in-app, user; task-0 root), dropped-batch (in-app, user; task-1 root), wrong-address
  (pending, agent), alcohol-procedure (pending, agent), late-delivery (pending, agent; a single-point violation, decided
  as a full-or-nothing threshold). Tools record_late_delivery_violation_939f2196 / record_missing_items_violation_e43bab28
  are abandoned (never written). Task 0 root becomes the conduct-complaint excusal (new tool uuid), the seeded
  missing-items violations carry the base 2 points, the late-delivery story becomes a store conduct complaint.
- [saved] task 0 re-closed after redesign: A0=1, R0=3, W0=4, root conduct=3; all per-task gates OK; rationale rewritten.

## Task 1 — design thesis (draw: prerequisite_problems=3, factor_counts=[4, 4, 6, 5])
- Occupied by task 0: dropped-batch severity, wrong-address severity, missing-items excusal, conduct-complaint excusal.
- Task 1 claims: root shopper_ext_dropped_batch_excusal (6, user in-app dispute, dispute_dropped_batch_violation_598e80dc);
  prereqs shopper_ext_wrong_address_excusal (5, decide_wrong_address_dispute_4037a75e), shopper_ext_alcohol_procedure_excusal
  (4, decide_alcohol_procedure_dispute_63dedfc1), shopper_ext_late_delivery_excusal (4, decide_late_delivery_dispute_3251c6fd,
  single-point violation decided full-or-nothing against an excusal mark). Fan-out of three value_input edges into the root's
  standing-points reduction. Customer: Priya Iyer, Full-Service Shopper Diamond, frozen 2026-09-23T11:25:00; opening standing 12
  (< Diamond hold 13): late 1 + alcohol 6 + wrong-address 2 (booked under the wrong-address severity) + dropped 3 (booked under
  the dropped-batch severity). Targets: wrong 1, alcohol 3, late 1, root 2.
- [saved] task-1 policies written: wrong-address excusal (5), alcohol-procedure excusal (4).
- [saved] late-delivery excusal (4) written.
- [saved] root dropped-batch excusal (6) written; all 8 policies on disk.
- [saved] tasks/1.json initial_state (Priya Iyer, Diamond, balance 12 = recorded 26 - cleared 14).
- task-1 seed revision: historical violation points aligned with the severity rules at their booking dates (prior wrong-address 2, prior drops 3 and 6); balance stays 12 (recorded 29 - cleared 17). Sensitivity: PW=1, PA=3, PL=1, root=2 (skip each prereq -> 1).
- NOTE: shared scratchpad files were removed by another process mid-run; authoring helpers moved to a private subfolder (scratchpad/shopper_rd_work) and the id maps are rebuilt from tasks/*.json.
- [saved] task 1 design_rationale; all task-1 per-task gates OK. Helpers moved to scratchpad/shopper_ratings_and_deactivations/ (own files only).

## Final closure (round 1)
- Suite: 8 extended policies, 8 task tools, tasks 0 and 1 disjoint, together covering every policy.
  task 0: missing-items excusal (4) + dropped-batch severity (6) -> wrong-address severity (6) -> conduct-complaint excusal (5, user root).
  task 1: wrong-address excusal (5), alcohol-procedure excusal (4), late-delivery excusal (4) -> dropped-batch excusal (6, user root).
- Full gate run (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (suite means
  branches 61.00, steps 16.00; history max 35; branches max 65), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.
  check_traceability skipped (KB not yet published).
- Manual value gates recorded per task in design_rationale (tree cards, factor cards, base-invariant cards, draft
  recomputation). Open notes for audit: ratings carry the batch only (rated orders belong to other customers' profiles and
  are outside the worlds); the levels (Platinum, Diamond) are held on the ledger's modest last-month batch counts within
  their demotion grace cycles.
- Temporary authoring scripts deleted; no __pycache__ in the write domain.

## Rework round 2 (audit env/.../audits/policy_task/shopper_ratings_and_deactivations/)
Plan per item:
- F1 / T0-F1 (dropped-batch severity vs batch charter excused_drop_reasons): the severity now applies only to drops
  with reason shopper_choice (the only reason the batch charter records a violation for); every other reason owes none.
  The fault_by_drop_reason ladder is removed; a new parameter factor (dropped item-units surcharge) keeps the drawn
  count of 6. E1's sentence/condition narrowed to drops made by the shopper's own choice. Task 0's dropped batch becomes a
  shopper_choice drop (persona line changed); task 1's historical drop points re-derived under the new rule.
- F3 / T0-F3 (clawback_relief not a real severity condition): replaced by a wrong-address repeat surcharge (other
  wrong-address violations recorded in the twelve months before); payout reads/rows leave task 0; task 0 seeds one
  expired prior wrong-address violation; level of task 0's shopper moves to Diamond so the end balance stays under hold.
- F2 / T1-F2 (alcohol hand-off praise not a real condition): replaced by a recent-record reduction (other violations
  recorded in the month before the decision); outage credits re-tiered; root standing tiers re-tuned.
- T0-F4 (stale 2026-09-05 date in evaluation_criteria[4].objective): corrected to 2026-09-16.
- Observations: boundary_check texts of submitted-dispute decisions re-anchored on the submission date.
- R2 task 0 re-closed: A0=1, R0=4, W0=5, conduct=3 (edge runs 3->2, 3->4, 5->4).
Round 2 — what changed, per audit item:
- F1 / T0-F1 (closed): shopper.extended.yaml shopper_ext_dropped_batch_severity — rule now owes a violation only for drops
  with reason shopper_choice and states that every excused or other reason owes none; fault_by_drop_reason removed; new
  parameter factor stranded_items_surcharge (item units 60+/30-59/fewer -> 2/1/0); volume_high_relief 2 -> 3; compute selects
  the dropped batch with drop_reason='shopper_choice'. shopper_ext_wrong_address_severity E1 sentence and condition narrowed
  to "every batch the account dropped by its own choice". tasks/0.json: the dropped Stock-Up batch is a shopper_choice drop
  (45 units), dropped-batch severity 3 -> 4, persona's reaction line changed. tasks/1.json: historical drop severities
  re-derived (Bd 26 units -> 3; Vp2 6 -> 7 with its clearing).
- F3 / T0-F3 (closed): clawback_relief removed from shopper_ext_wrong_address_severity; repeat_address_surcharge added (other
  wrong-address violations recorded in twelve months, 2+/1/0 -> 2/1/0); cross_category payout dropped. tasks/0.json:
  payout account/events and the two payout reads removed; a 2026-01-20 wrong-address violation (expired) with its batch and
  reversal seeded; wrong-address batch's 1-star rating now 2 stars; wrong-address severity 4 -> 5; shopper level Diamond
  (end balance 11 < hold 13); conduct standing tiers 11/6. Steps re-indexed (8, 10, 12, 14).
- F2 / T1-F2 (closed): shopper_ext_alcohol_procedure_excusal loses alcohol_handoff_praise_credit; new
  alcohol_recent_record_reduction (violations of other types recorded in the month: 4+/1-3/none -> 2/1/0); outage credits
  3/4; tenure method now acts on the outage credit. tasks/1.json: alcohol result 3 -> 2; dropped-batch excusal standing tiers
  6/3 (root still 2, every skip -> 1). Wrong-address excusal low-rating tier now counts ratings of 2 stars or fewer; the
  Triple batch carries two 2-star ratings and an excluded 3-star (keeps the historical wrong-address severity at 2).
- T0-F4 (closed): tasks/0.json evaluation_criteria find_shopper_appeals objective now says "submitted 2026-09-16".
- Observations: boundary_check texts of submitted-dispute decisions re-anchored on the submission date (tasks 0 and 1).
- Unchanged and still passing: problem trees, prerequisite sentences E2-E6, missing-items / conduct / late-delivery /
  dropped-batch excusal formulas, user tools.
- Round 2 closed: full gate block green (traceability skipped); scratch folder and __pycache__ removed.

## Rework round 3 (merge acceptance, erlbench.validate_scenario)
- Item "shopper_ratings_and_deactivations/0|1: frozen_time must start with YYYY-MM-DD" (closed): the validator's
  `^\d{4}-\d{2}-\d{2}\b` fails on the 'T' separator. frozen_time rewritten to the same instant in the persona's local zone
  (Austin, CDT): task 0 '2026-09-22T15:10:00' -> '2026-09-22 15:10:00 CDT'; task 1 '2026-09-23T11:25:00' ->
  '2026-09-23 11:25:00 CDT'. The literal was also quoted in prerequisite_closure.edges[0].unresolved_at_frozen_time.why_false
  and in design_rationale of each task; both updated (3 occurrences per file).
- Effect: every computation reads NOW = frozen_time[:10] and every tool writes event_date = ctx.now()[:10], so dates, windows
  and all scored points are unchanged (task 0: 1/4/5/3; task 1: 1/2/1/2). ctx.now() itself returns the stamp verbatim, so the
  timestamp fields written from it (dispute created_at of the user tools, verification verified_at) now carry
  'YYYY-MM-DD HH:MM:SS CDT' text for the same instant; gold and rollouts share the one clock, so scoring is unaffected.
- Round 3 verification: full gate block green; validate_scenario: 0 non-document errors, the 8 errors naming this difficulty are all 'required document not found' (KB not rendered). No scratch files created; no __pycache__ in the write domain.

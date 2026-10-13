# worklog — group_room_block_contracts (M=2)

## Step 0 draws (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=1, factor_counts=[5, 4]
- task 1: prerequisite_problems=2, factor_counts=[5, 5, 6]

## Difficulty pre-check
- Base: group.yaml. DSL limits: SUM/COUNT/MAX/LATEST scoped to this block (group_ledger, group_amendments);
  cross reads scoped to the organiser's customer_id (booking/loyalty/...); attendee reservations held by other
  customers cannot be aggregated, so pickup-based problems (attrition, comps, cut-off release) are not
  machine-recomputable here -> not claimed as computations.
- User-owned acts with a computed figure: paying a group deposit, signing the written cancellation (the notice
  carries the damages the organiser signs for). Post-event payments carry no multi-factor figure -> not used.
- Allocation: task 0 = {interim deposit payment (user, root), signed-reduction implementation (agent)};
  task 1 = {deposit refund on cancellation (root), deposit retention toward damages, signed cancellation with damages (user)}.
  Pairwise disjoint; every tool claimed once.

## Resume (fresh agent #3, round 1) — breakpoint and redesign of task 1
- On disk at resume: base section of group.extended.yaml verbatim (diff vs products/group.yaml = identical prefix),
  one extended policy complete (group_ext_reduction_room_nights, 5 factors, prerequisite []), no task_tools.py, no tasks.
- Draws re-run and unchanged: task 0 {prereq 1, factors [5,4]}, task 1 {prereq 2, factors [5,5,6]}.
- Task 0 allocation kept: root = interim deposit paid by the organiser (owner=user, 4 factors) <- signed reduction
  implementation (agent, 5 factors, the policy already on disk). Wedding Room Block (interim 25% at 120 days).
- Task 1 allocation CHANGED (symptom -> root cause -> change):
  symptom: the recorded task-1 tree {deposit refund (root), deposit retention, signed cancellation} makes two of its
  three computations balance identities: retention = min(deposits held, damages) and refund = deposits held after
  retention. root cause: base group_deposit_schedule pins both ("retained ... up to their amount", "any deposit beyond
  the damages is refunded"); any load-bearing factor on either would leave money stranded in deposit_held or refund
  money while damages are still owed, i.e. an incoherent ledger; the customer would also have to ask for the
  cancellation itself (the prerequisite), breaking Principle H. Same defect for a post-event "pay the master balance"
  root (payment = balance). change: task 1 = Tour & Travel Series Block cancelled by its tour operator after cut-off:
  root = signed cancellation with damages (owner=user, 6 factors) <- cut-off release owed since the cut-off date
  (agent, 5 factors) and <- signed increase addendum awaiting implementation (agent, 5 factors); the release also
  waits on the increase (held room nights). A Tour block holds no deposits (deposit_signing_pct = interim_pct = 0),
  so the cancellation lights no retention/refund obligation; its rooming-list reservations are held on the tour
  operator's own profile (channel group_rooming_list, guarantee group_master_account), so the room nights reserved
  inside the block are readable through the organiser-scoped booking reads. The customer raises only the cancellation.
- DSL notes: history filters are equality-only (no date thresholds inside SUM/COUNT); cancellation_scale is a list
  parameter and cannot be indexed, so the damages compute reads the scale step through a ternary on block type and days.

## Task 0 (closed)
- Policies: group_ext_reduction_room_nights (on disk, 5 factors; amended: added the missing replaced_by sentence
  "Room nights an addendum requests beyond the allowance still open are not removed ..." to its rule so its declared
  overwrite[1] is verbatim) + new group_ext_interim_deposit_amount (4 factors: late_receipt_load, event_deposit_relief,
  rewards_relief, deposit_true_up[method]; prerequisite on the reduction, state form, value_input on `revenue`).
- Route-around (base clause unworkable as evidence): group_deposit_schedule.once_per_milestone binds the action's
  entry_basis to a pre-action system value, which no record can carry for a deposit not yet received; retired by a
  declared overwrite whose replaced_by restates the same dedup per deposit kind ("an interim deposit is received at most
  once on a block ..."). group_addenda.reduction_allowance was already retired by the reduction overwrite.
- Tools: implement_block_reduction_df5160bf (agent), pay_group_deposit_93013531 (user; entry_basis enum is required by
  the base dedup action_binding name). uuid8 generated per tool with uuid.uuid4().hex[:8].
- World: Wedding Room Block YCW115 (Ashbury Grand SDGRN), arrival 2027-01-15, frozen 2026-10-07 (100 days out, interim
  due 2026-09-17 = 20 days late). Signed 2026-08-13 reduction (18 rn) unimplemented = the falsified prerequisite.
- Probe (check_compute primitives): reduction 14 (sens 10/10/13/10/11, all-baseline 2); interim 3080.70 after the
  reduction (sens 2362.50/3798.90/3439.80/3231.90, all-baseline 3591.00); skipping the reduction -> 3940.65.
- Symptom -> fix: replay dangling FK on '' ids -> empty FKs seeded/written as null; replay closure mismatch (past stays
  and the event ledger unread) -> added find_booking_reservations(loyalty_member_id) and find_meeting_ledger reads,
  call steps moved to 11 and 13 everywhere.
- Per-task gates task 0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK (cache diff info only).
- Manual gates: persona raises only the second deposit; addendum mentioned only in a conditional reaction; user tool
  is the organiser paying with her own card; time gate 2026-10-17 accepted / 2026-10-18 refused; every factor sits off
  its fall-through; prerequisite sentence affirmative ("only after"), state form, single write books the state.

## Task 1 (closed)
- Tree: root group_ext_cancellation_damages (owner=user, 6 factors) <- group_ext_increase_commitment (agent, 5) and
  <- group_ext_cutoff_release_nights (agent, 5); release <- increase. 3 value_input edges, all state form; directions:
  release "only after", damages "not ... until" (increase) and "only after" (release).
- Tools (uuid8 drawn one per tool): implement_block_increase_5576c741, record_cutoff_release_57832b69,
  sign_group_cancellation_1ea1e1e5 (user; writes status/cancelled_date, the contract_cancelled release of held nights
  and the damages charge, mirroring the base group_contract_cancel triggers).
- Route-around: group_cancellation.signed_notice is a caller_statement gate bound to the internal block id, which no
  caller can state; retired by a declared overwrite keeping the same requirement as the organiser's own signature
  through the user-owned signing step (signature date = notice date). Base cut-off release and damages formula
  sentences, and the scale-step sentence, are superseded by declared overwrites. Elimination waiver kept as out of
  scope of the computation (no waiver on Tour blocks).
- DSL note: the damages compute restates the six base cancellation_scale ladders as a ternary on block type (the list
  parameter cannot be indexed); the values are the base variants' own, verified step by step (/tmp scale check).
- Increase factor set revised twice: (a) lead_time_share / increase_size_cut had no record-reading binding -> lead days
  binding moved into the share factor and the count-start method now decides the count offset; (b) size cut 5 points
  was decorative (int(12 x 0.60) = int(12 x 0.65) = 7) -> cut points 10/20; (c) history floor failed (only LATEST)
  -> size cut measured against the allocation entry (SUM), which is the contract at signing.
- Probe: increase 6 (sens 3/9/5/9/7, all-baseline 12); release 7 (sens 8/13/11/10/13, all-baseline 27); damages
  6137.60 (sens 8329.60/6576.00/7288.40/6675.20/6451.20/6406.40, all-baseline 12312.00). Skips: no increase -> release
  2, damages 5868.80; no release -> damages 6451.20.
- Manual gates: customer raises only the cancellation and fences off the rooming-list reservations themselves (her own
  portal act, no ask to the desk); prerequisites appear only as conditional consents; the cut-off time gate 2026-09-30
  refused / 2026-10-01 accepted; every factor off its fall-through; no deposits, so no retention/refund lit.

## Final gate block (no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK (suite means branches 68.50, steps 14.50;
history_rows_max 10; branches_max 109); GROUNDING OK; CACHE-DIFF INFO (optional); SCOPE OK. Traceability deferred
until the KB is published (orchestrator instruction).

## Rework round 2 — final gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (branches 67.00, steps 14.50, history_rows_max 10, branches_max 108), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability deferred
## Rework round 2 items (audits/policy_task/group_room_block_contracts: _difficulty.md, 0.md, 1.md)
- F-G2 (binding) / T0-F1: interim `rewards_relief` (co-brand card + tier) deleted from rule, compute, basis, factors,
  params, cross_category (loyalty dropped from this policy). Replaced by `reduction_exposure_load` (parameter): room
  nights of the block's reduction entries against its allocation entry, >=15 % -> +5 points, >=5 % -> +2.5, else 0
  (risk-based deposit scheduling: a block already shrinking carries more attrition exposure). Interim keeps 4 factors
  (3 parameter, 1 method). Task 0 deposit 3080.70 -> 4158.00 (sens late 3439.80, event 4876.20, exposure 3439.80,
  true-up 4309.20; all-baseline 3591.00); skip-reduction 3940.65 -> 4791.15. tasks/0.json step 13 arg, computation,
  tracing, contract business_effect, closure, read-node texts and rationale updated.
- F-G2 (binding) / T1-F1: release `late_name_holdback` (Premier card + personal night credits) re-based on the
  block's pickup: confirmed Group Block Rate room nights naming the block vs contracted, >=70 % -> share-of-contract
  method (5 %), >=50 % -> fixed rooms-per-night method, else none. Still the release's method factor (5 factors, 1
  method); cross_difficulty booking via its own XSUM binding; loyalty dropped from this policy. Same tier on task 1
  (60/81 = 74 %) -> holdback 4, release 7, damages 6137.60 unchanged. Task-1 texts updated; persona no longer
  mentions the card.
- F-G1: damages rule now states "When the matching step is the top step of the block type's cancellation_scale, no
  step has a longer lead and the step one longer lead is the top step itself."; next_pct basis quotes it.
- O-G1 / O-T0-3 / O-T1-2: kept (courtesy and tenure as codified relationship concessions; not binding); decision
  recorded; the "multi-source" label on tenure_scale_step trace removed.
- O-G2: no change (no base sentence fixes the committed share; baseline = full commitment).
- O-G3: dedup sentence and its overwrite now cover both deposit kinds ("each kind of scheduled deposit is received at
  most once ... signing kind or ... interim kind").
- O-G4: damages <- increase sentence now "matched by an increase entry on the block ledger that names it" (policy,
  task 1 closure and rationale).
- O-G5: release overwrite split into two clauses; rule and first replaced_by state that a call-in block is outside
  the policy and keeps the base release of every unreserved held room night on the cut-off date.
- O-G6, O-G7: no change (no sequence statement; base orders ground no edge).
- O-G8: reduction selection sentence no longer says "one at a time in the order they were issued"; it reads "The
  addendum implemented is the most recently issued reduction addendum whose status is signed ..." (basis updated).
  An already-implemented latest addendum is barred by the inherited "No addendum is implemented twice."
- O-G9 / O-T1-3: kept; base dates the release on the cut-off date itself.
- O-T0-1: reads kept (closure requires every seeded row to be read; they confirm credited stays / received event
  deposit). O-T0-2: event_deposit_relief no longer labelled multi-source. O-T1-1: both replay conventions recorded
  in edge_load_bearing (5868.80 with release at gold 7; 6092.80 with release recomputed).
- Closing checklist: per-task files map 1:1 to tasks/0.json, 1.json; scopes disjoint and jointly cover the 5 policies;
  trees unchanged (task 0: 1 prereq / 1 value_input; task 1: 2 prereqs / 3 value_input); every factor bears weight
  and every fall-back differs from gold (gates below); instantiation gates re-run on the final form.

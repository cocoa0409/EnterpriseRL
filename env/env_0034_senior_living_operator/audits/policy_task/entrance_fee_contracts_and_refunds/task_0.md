# Policy-task audit — entrance_fee_contracts_and_refunds / task 0

## revision_1

## source_derivation_frozen

- Auditor: independent policy-task auditor (erl-task-policy-audit). Round 1.
- Freeze time: 2026-10-05T09:15Z, written before any task JSON of this difficulty was opened.
- Inputs and hashes: view `audits/_views/policy_task/entrance_fee_contracts_and_refunds/task_0.view.json` sha256 c9256f577ddb64e637271e3a6f73a01a07c7ac0a1599249c5c8cac060d877c38; `entrance.extended.yaml` c593bac6…3cc3339; `task_tools.py` 04a31a9c…a4e3336 (all re-hashed by the auditor and matching the MANIFEST).
- Fields permitted: `frozen_time`, `user_scenario`, `initial_state` (view), the extended charter, the task tool module, `blueprint/`, `erlbench/`, and the DSL primitives in `skills/erl-task-instantiate/scripts/check_compute.py`. Fields masked: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`, and the worklog.
- contamination_disclosure: none. The brief carried no scored value. No recursive search was run over `tasks/` or `audits/`. The only listing of `tasks/entrance_fee_contracts_and_refunds/` was a file-name `ls`.
- Recomputation tool: a temporary script in /tmp that evaluates the charter's own `compute` with `check_compute.build_env` over the view's `initial_state`, plus the auditor's simulated tool effects. Removed after the audit. Every number below was also worked by hand.

### policy_self_consistency (this task only)

- Charter-global conclusions are cited, not restated: `_difficulty.md` § policy_conflict_scan, § rule_compute_equivalence, § action_binding_and_uuids, § prerequisite_graph, § prerequisite_sentences, § override_declarations, § factor_ladders.
- F-2 (`_difficulty.md` § findings): no consequence on this world. The cancellation here is the resident's own (termination_reason will be pre_occupancy_cancellation, payee resident), so the death/illness branch is not reached.
- O-3: after the gold refund the refundable balance is −205.69. A cancelled agreement has no transition to `closed`, so no scored field differs.
- Override sweep against this world: base `entrance_pre_occupancy_cancellation` S1 (plan fee 2 % = 8,126.00 and "the rest of the money paid is refunded") is superseded by declared overwrites for both quantities scored here. No undeclared base sentence yields a second processing fee or refund on this world. Base rescission does not apply: Willow Creek's period is 7 days from 2026-07-08, so it ended 2026-07-15.
- Handling time:
  - Step A (cancellation fee) is evaluated on the opening world at 2026-10-02.
  - Step B (refund) is evaluated after step A's real effects land: status cancelled, termination_date 2026-10-02, processing-fee entry 2,358.00, request c9083c26 signed.
  - The refund formula reads `termination_date` and `fee_retained`, both of which exist only after step A, so it is not evaluable earlier.
- No real-world waits:
  - Every fact consumed is in `initial_state` (agreement, deposit row, pending request, signed extension request, cancelled IL reservation, active IL residency, respite trial-stay charge) or is the effect of step A.
  - The cancellation is signed on the call by the resident herself (persona: "say you would rather sign now and be done").
  - The refund is a check issued by the tool on the call.
  - The occupancy deadline (90 + 30 days from 2026-07-08) has not passed, and no clearing or approval is pending.

### problem_chain

Walked from the root:

- Root: the customer asks for "the money you paid on that contract refunded to you", i.e. a refund on a cancellation before occupancy → `entrance_ext_pre_occupancy_refund` (agent, `pay_pre_occupancy_refund_45806fa1`).
- The root rule's prerequisite sentence: "A refund on a cancellation before occupancy is not paid until the agreement stands in cancelled status and its ledger carries the processing fee retained on that cancellation."
  - At 2026-10-02 the state is false. `entrance_agreements[b3873efc…].status` = `reserved`, and `entrance_ledger` holds only `c2f87e7e…` (entrance_deposit_payment 40,630.00); no entrance_processing_fee_retention row exists.
  - The policy whose rule writes that state is `entrance_ext_cancellation_processing_fee` ("signing it cancels the agreement and retains the processing fee from the money paid"). Its target tool is `sign_pre_occupancy_cancellation_25852637`, owner = user.
  - Its own rule carries no prerequisite sentence. Its eligibility holds at the opening: rescission period over, agreement reserved, signer is the resident herself, and the pending request c9083c26 (`pre_occupancy_cancellation`, `pending_signature`) supplies the request id.
- Derived tree: nodes {pre_occupancy_refund (root, agent), cancellation_processing_fee (user)}. One edge root → cancellation, kind value_input (`fee_retained`; it also fixes the cancellation date that `deposit_days_held` runs to). n = 1, so the floor of max(n−1,1) = 1 value_input edge is met. Acyclic. One owner=user write in the tree.
- Topological order: sign cancellation (user) → pay refund (agent).
- Load-bearing run: skip the cancellation and replay.
  - The status stays `reserved`, so base `refund_on_closed_agreement` forbids the payment.
  - `termination_date` is empty, so the refund formula's `DAYS(…, F('termination_date'))` has no value.
  - Forcing termination_date to 2026-10-02 to isolate the value edge gives `fee_retained` 0.00 and refund 40,835.69 instead of 38,477.69. The edge bears weight.
- Parallel edges: none.
- No-wait: the resolving action is the customer's signature on the call.
- Tools do not judge the prerequisite. The `pay_pre_occupancy_refund_45806fa1` body reads the agreement row only for the balance and payee, then creates the entry unconditionally. `sign_pre_occupancy_cancellation_25852637` likewise has no branch on status or timing.
- Customer raises only the root problem. The persona states the facts of September ("phoned the Willow Creek office and told them you are not going to move in") but "You assume the office took care of everything … so you do not raise any paperwork yourself". The cancellation surfaces only through the conditional "If the agent explains that the contract still has to be cancelled with your own signature …". She names no prerequisite, asks nothing outside the charter, and closes after the check number.
- Isomorphic to the declared `prerequisite` of the charter (refund → cancellation, value_input, state form).

### task_independent_derivation

- Need/authorisation/timing: the resident herself, calling for herself, wants the money paid on the Willow Creek contract refunded now, by check to the address on file. She signs the cancellation herself when handed the step. Identity is established with DOB 1952-03-17 + SSN last4 7342 (profile e51cfd93…). Clear and unique.
- Now / wait / refuse: act now. The rescission period is over (7 days from 2026-07-08). The agreement is reserved, not occupied. The occupancy deadline has not passed. No date_of_death is recorded. The signer is the resident, so `representative_authority` = authorized_contact is irrelevant.
- Object: agreement `b3873efc-2e95-4a1d-aaf4-79219ed744e1` (LifeChoice 75% Refundable, Willow Creek, One-Bedroom Deluxe 3107, entrance fee 406,300.00 = 276,400 × 1.47 rounded to 100). Request `c9083c26-0425-4e74-826c-d22dbae729fd`.
- Step A — processing fee (handling time 2026-10-02, opening world):
  - Notice date: a cancellation request awaits signature, registered 2026-09-02 (tier 1). Days of notice from 2026-09-02 to the planned occupancy date 2026-11-04 = 63.
  - Fee percentage: 63 ≥ 60 → 1.0 %.
  - Extension surcharge: a signed occupancy_extension request `7e87e3ea…` is on file and notice days are ≥ 30 → 0.25 points.
  - Gross: 406,300.00 × 1.25 % = 5,078.75.
  - Trial stay: respite_ledger `11b8c40e…` (respite_nightly_charge, Independent Living Trial Stay, 5 nights, 725.00, posted 2026-04-20, 5 whole months before). 5 nights → share 0.5, credit 362.50, so 4,716.25.
  - Internal move: active IL residency `966716c3…` (Juniper Point, move-in 2024-03-11, 30 whole months before) → ≥ 24 → halved and rounded down to the dollar: 2,358.125 → **2,358.00**.
- Step B — refund (handling time 2026-10-02, after step A):
  - Money received 40,630.00, less fee retained 2,358.00.
  - Escrowed deposit 40,630.00 ≥ 40,000 → 2.05 %.
  - Days held 2026-07-08 → 2026-10-02 = 86 → 60-89 → +0.20, so the combined rate is 2.25 %.
  - The deposit instrument is `check` (personal check; the schema enum separates `certified_check`, and the persona says "personal check") → accrual 86 − 5 = 81 days.
  - Willow Creek → /360: 40,630 × 2.25 % × 81/360 = 205.689375 → 205.69.
  - Refund = 40,630.00 − 2,358.00 + 205.69 = **38,477.69**.
  - Contrast: on the opening world the root is not evaluable (no termination date, no fee entry). With the date forced and no fee it would be 40,835.69. 38,477.69 is right because the refund's own rule fixes its moment after the fee is retained.
- Write sequence (scored writes):
  1. `verify_customer_identity`(customer_id e51cfd93-6568-4ea0-a143-3de2d8cbf471, date_of_birth 1952-03-17, ssn_last4 7342) — agent.
  2. `sign_pre_occupancy_cancellation_25852637`(customer_id e51cfd93-6568-4ea0-a143-3de2d8cbf471, entrance_agreement_id b3873efc-2e95-4a1d-aaf4-79219ed744e1, entrance_request_id c9083c26-0425-4e74-826c-d22dbae729fd, processing_fee 2358.00) — **user**, handed over by the agent.
  3. `pay_pre_occupancy_refund_45806fa1`(entrance_agreement_id b3873efc-2e95-4a1d-aaf4-79219ed744e1, refund_amount 38477.69) — agent.
- Necessary reads: customer, agreement, entrance ledger, entrance requests, independent residencies, respite ledger.
- Terminal state:
  - Agreement cancelled, termination_date 2026-10-02, reason pre_occupancy_cancellation, payee resident, refundable_balance −205.69.
  - Request c9083c26 signed.
  - Ledger + processing fee 2,358.00 + refund 38,477.69 (check).
- Closest alternatives excluded:
  - Notice date = signing day (33 days, 1.5 %) — excluded because a request awaits signature (rule tier 1).
  - Plan 2 % fee (8,126.00) — superseded by the declared overwrite.
  - Counting the respite_payment row `3d64da29…` (725.00) as a charge — excluded: "trial-stay nightly charges".
  - Using 2026-09-02 as the cancellation date for the term bonus (56 days → no bonus) — excluded: the cancellation date is the signed cancellation (termination_date).
  - Treating `check` as certified (no hold) — excluded by the enum and the persona.

### factor_weight

Computation A — processing_fee, gold-blind 2,358.00; whole-baseline (baseline.rule: 2 % × 406,300.00) **8,126.00** ≠ 2,358.00.

| factor | effect (honest?) | tier taken / records | baseline from baseline.rule | result under that baseline | bears weight |
| --- | --- | --- | --- | --- | --- |
| cancellation_notice_date | method (selects the anchor record) — yes | tier 1: request c9083c26 pending_signature, created 2026-09-02 | notice date = day signed (credit 0) | 3,373.00 | yes |
| notice_fee_percentage | parameter — yes | tier 1: 63 days ≥ 60 → 1.0 | plan 2.0 | 4,389.00 | yes |
| occupancy_extension_surcharge | parameter — yes; multi-source | tier 2: signed extension 7e87e3ea + 63 days → 0.25 | 0 | 1,850.00 | yes |
| trial_stay_credit_share | parameter — yes; cross-difficulty respite | tier 2: respite_ledger 11b8c40e, 5 nights → 0.5 | 0 | 2,539.00 | yes |
| internal_move_rounding | method (label borderline, O-14) | tier 1: independent 966716c3 active, move-in 2024-03-11, 30 months | stands to the cent | 4,716.25 | yes |

- Stamps: `occupancy_extensions_used` = 1 on the agreement records the extension fact itself, not the surcharge outcome. It agrees with the request row, and the tier also needs the notice days, so it is not an outcome stamp. No field names a tier outcome.
- Near-misses:
  - respite_payment `3d64da29…` 725.00 (a payment, not a nightly charge). Summing all respite ledger amounts would give share-adjusted credit 725.00 and a fee of 2,176.00 (5,078.75 − 725.00 = 4,353.75, halved and floored).
  - IL reservation `270a1bda…` cancelled, closed 2026-09-02 (tier-2 evidence, excluded by tier 1, same date on this world).
- Cross-difficulty rows present in the seed: respite_stays `0a6e4b1b…` + respite_ledger `11b8c40e…`; independent_residencies `966716c3…`, `270a1bda…`. These are consistent with the respite charter: trial stay at 145.00/night × 5 = 725.00.
- Survivors: 5 factors (3 parameter, 2 method), within bounds.

Computation B — refund_amount, gold-blind 38,477.69; whole-baseline (baseline.rule: money received less processing fee) **38,272.00** ≠ 38,477.69.

| factor | effect | tier taken / records | baseline | result under baseline | bears weight |
| --- | --- | --- | --- | --- | --- |
| escrow_deposit_rate | parameter | tier 1: deposit c2f87e7e 40,630.00 ≥ 40,000 → 2.05 | 0 (no escrow interest) | 38,290.28 | yes |
| escrow_term_bonus | parameter | tier 2: 86 days held → 0.20 | 0 | 38,459.41 | yes |
| deposit_funds_availability | method | tier 1: payment_method `check` → 81 days | days held (86) | 38,490.39 | yes |
| escrow_bank_day_count | method | tier 1: Willow Creek → /360 | /365 | 38,474.87 | yes |

- Stamps: none.
- Near-miss: the 2026-09-02 dates (pending request, IL reservation closure) as a candidate "cancellation date". The rule's "to the cancellation date" (= termination_date of the signed cancellation) excludes them. They would drop the term bonus.
- No cross-difficulty factor in this computation; the task's cross-difficulty requirement is met by computation A.
- Survivors: 4 factors (2/2), within bounds.
- Task-level: multi-source ≥ 1 (occupancy_extension_surcharge) and cross-difficulty ≥ 1 (trial_stay_credit_share, internal_move_rounding) are both met.

Frozen blind verdict (pre-reveal):
- Policy self-consistency PASS for this task. The charter-global F-1 to F-5 have no consequence on this world.
- Problem tree PASS.
- Factors PASS.
- Unique solution PASS: processing_fee 2,358.00 and refund_amount 38,477.69.

## source_gt_comparison

Reveal time 2026-10-05T09:13Z, after both task files' frozen sections were on disk. Freeze hashes at reveal: task_0.md 430f37e0e09034be4680aa6d8a39fb3fa9e6f9f79f84be078e39f556b4ba3be7, task_1.md 904b0025677dc33c91138914c37c1e46bb2a1c124e5f208e5c1b72665dfb8135, _difficulty.md 60bad74f5e7d9776974cae6e312a1455fc4101df40f1bd13881d299c22d6a69f. Read: `tasks/entrance_fee_contracts_and_refunds/tasks/0.json` (all masked fields).

| item | blind | GT | same? |
| --- | --- | --- | --- |
| need / authorisation / timing | resident, for herself; refund now by check; she signs the cancellation | request_alignment "wants the money she paid … refunded"; step 9 owner user | same |
| now / wait / refuse | act now | act now (steps 9, 11) | same |
| identity | verify e51cfd93…, DOB 1952-03-17, SSN 7342 | step 2, same arguments | same |
| object | agreement b3873efc…, request c9083c26… | same ids | same |
| read set | customer, agreement, entrance ledger, entrance requests, IL residencies, respite ledger | the same plus `find_respite_stays` (reads are not scored writes) | same in substance |
| write 1 | `sign_pre_occupancy_cancellation_25852637`, user, processing_fee 2358.00 | step 9, user, processing_fee 2358.0 | same |
| write 2 | `pay_pre_occupancy_refund_45806fa1`, agent, refund_amount 38477.69 | step 11, agent, 38477.69 | same |
| order | cancellation → refund | resolution_order [cancellation_processing_fee, pre_occupancy_refund] | same |
| terminal | cancelled 2026-10-02, fee 2,358.00, refund 38,477.69, balance −205.69 | same effects by replay | same |

Problem tree vs `prerequisite_closure`, value by value:
- root entrance_ext_pre_occupancy_refund = root;
- edge → cancellation_processing_fee, value_input, gate `fee_retained`, form state, policy_source verbatim the same sentence;
- why-false evidence: status reserved, request c9083c26 pending_signature, only ledger row c2f87e7e (same three rows);
- skipped effect: 40,835.69 vs 38,477.69 (GT "40,630.00 + 205.69 = 40,835.69"; blind 40,835.69) — same;
- tools_do_not_block — same reading of both bodies.

`factor_weight` vs `computations[].factor_sensitivity` / `baseline_result`, figure by figure:
- processing_fee: expected 2358.0 = blind 2,358.00. cancellation_notice_date 3373.0 = 3,373.00; notice_fee_percentage 4389.0 = 4,389.00; occupancy_extension_surcharge 1850.0 = 1,850.00; trial_stay_credit_share 2539.0 = 2,539.00; internal_move_rounding 4716.25 = 4,716.25; baseline_result 8126.0 = 8,126.00. Tiers taken identical.
- refund_amount: expected 38477.69 = 38,477.69. escrow_deposit_rate 38290.28; escrow_term_bonus 38459.41; deposit_funds_availability 38490.39; escrow_bank_day_count 38474.87; baseline_result 38272.0 — all equal to the blind figures. Tiers identical.

Closest candidates excluded by policy/world evidence (not by GT's choice): see the frozen section's "Closest alternatives excluded". GT's rationale lists the same near-misses for computation A plus one more (the signed extension request is not a cancellation request). It lists none for computation B; the blind one (2026-09-02 as a candidate cancellation date) stands.

Proof-field assertions checked word for word: design_rationale factor cards, factor_trace lines, prerequisite_closure why-false/flips/skipped_effect, and solvability_contract stage_provenance. Every world assertion recomputes (MONTHS(2024-03-11, 2026-10-02) = 30; DAYS 33 + 30 = 63; 86 days held; 81 accrual days; 205.69 interest). No false assertion found.

Verdict, task 0:
- Policy self-consistency **PASS**. Charter F-1 to F-5 have no consequence on this world.
- Problem tree **PASS**.
- Factors **PASS**.
- Unique solution **PASS**.
- Overall **PASS**.

## findings

- No RED for task 0.
- Observations carried for this task:
  - O-3: the refundable balance ends at −205.69 on a cancelled agreement that the lifecycle never closes.
  - O-14: internal_move_rounding's `method` label and its tenure-dependent rounding direction.
  - The internal-move halving rests on any active Larkspur IL rental, including one at a non-Life-Plan campus (Juniper Point); the rule says so expressly, so this is not ambiguous.
- Relation to previous revisions: first revision.

## revision_2

### source_derivation_frozen (revision_2)

- Freeze time 2026-10-05T10:00Z (wall clock), before the round-2 task JSONs were opened.
- Inputs: `task_0.view.json` c9256f57…7c38 (unchanged since round 1); `entrance.extended.yaml` 056b1ff6…a599cb (changed); `task_tools.py` unchanged.
- Fields permitted and masked are as in revision_1.
- contamination_disclosure: the round-1 GT of this task (processing_fee 2358.0, refund_amount 38477.69, the full evaluation_criteria) is known to the auditor from round 1. The round-2 derivation below re-evaluates the round-2 charter's compute over the unchanged view and re-checks every changed sentence. It does not rely on the round-1 GT, but it cannot be called blind to it.
- Why task 0 is re-derived although its view is unchanged: its two policies are part of the changed charter. cancellation_processing_fee is identical. pre_occupancy_refund changed in rule text (scope, carve-out, deadline, prerequisite sentence) but not in compute.

### policy_self_consistency (revision_2, this task)

- Cites `_difficulty.md` § revision_2. F-2 is closed at charter level. This cancellation is the resident's own (Lorraine signs; termination_reason pre_occupancy_cancellation), so it is squarely inside the narrowed refund rule ("This refund rule covers only a cancellation signed by the resident or the resident's financial agent").
- The restated deadline ("paid no later than pre_occupancy_refund_days calendar days after the cancellation") permits payment on 2026-10-02.
- Handling time and the no-wait argument are unchanged from revision_1.

### problem_chain (revision_2)

- Same tree:
  - root pre_occupancy_refund ← cancellation_processing_fee, value_input `fee_retained`.
  - The prerequisite sentence is now "A refund on a resident's own cancellation before occupancy is not paid until the agreement stands in cancelled status and its ledger carries the processing fee retained on that cancellation."
  - At the opening: status `reserved`, no processing-fee entry. Still unmet.
  - The resolving write is still the signed cancellation (owner=user).
- Load-bearing run unchanged: 40,835.69 without the fee vs 38,477.69.
- Tools are unchanged and do not judge.
- The persona is unchanged and raises only the root.

### task_independent_derivation (revision_2)

- Write sequence:
  1. verify (e51cfd93…, 1952-03-17, 7342);
  2. `sign_pre_occupancy_cancellation_25852637`(e51cfd93…, b3873efc…, c9083c26…, **2358.00**) — user;
  3. `pay_pre_occupancy_refund_45806fa1`(b3873efc…, **38477.69**) — agent.
- Recomputed with the round-2 charter: identical intermediates (63 notice days, 1.0 % + 0.25, 5,078.75, credit 362.50, internal move to 2,358.00; then 2.05 % + 0.20, 81 accrual days, /360 → 205.69).
- Terminal state as in revision_1.

### factor_weight (revision_2)

- processing_fee: all baselines 3,373.00 / 4,389.00 / 1,850.00 / 2,539.00 / 4,716.25; whole baseline 8,126.00.
- refund: 38,290.28 / 38,459.41 / 38,490.39 / 38,474.87; whole baseline 38,272.00.
- Every factor bears weight, and the near-misses and cross-difficulty rows are unchanged.

Frozen verdict (pre-reveal, revision_2): policy self-consistency PASS; problem tree PASS; factors PASS; unique solution PASS — no regression.

### source_gt_comparison (revision_2)

- Reveal time 2026-10-05T10:01Z, after all three revision_2 sections were frozen (sha256 at reveal: _difficulty.md a9d0da6b…6f5f, task_0.md 3dc588f8…b341, task_1.md 30505594…2a47).
- Read `tasks/…/tasks/0.json` (sha256 85d444ae…030f).
- Item by item, every item is the same:
  - verify (e51cfd93…, 1952-03-17, 7342);
  - user `sign_pre_occupancy_cancellation_25852637` (… c9083c26…, processing_fee 2358.0) = blind 2,358.00;
  - agent `pay_pre_occupancy_refund_45806fa1` (b3873efc…, 38477.69) = blind 38,477.69;
  - order cancellation → refund;
  - `charter_scope` = blind scope;
  - closure edge value_input `fee_retained`;
  - skipped effect 40,835.69 = blind.
- Factor sensitivities 3373.0 / 4389.0 / 1850.0 / 2539.0 / 4716.25 (baseline 8126.0) and 38290.28 / 38459.41 / 38490.39 / 38474.87 (baseline 38272.0) equal the blind figures one for one.
- Verdict (revision_2, task 0): policy self-consistency **PASS**; problem tree **PASS**; factors **PASS**; unique solution **PASS**. **PASS — no regression.**

### findings (revision_2)

- No RED.
- Charter F-2, which carried no consequence here in round 1, is closed at charter level. The narrowed refund rule still covers this resident's own cancellation.
- O-3 and O-14 remain as observations.
- Relation to revision_1: verdict unchanged (PASS).

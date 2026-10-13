# Policy-task audit — sender_verification_and_limits / charter-global

## charter_global_frozen

- Written before any task GT was revealed; contains nothing derived from a revealed GT.
- Freeze time: 2026-10-04T16:36Z. Auditor: independent erl-task-policy-audit agent (did not author the artifacts).
- Frozen inputs (sha256, verified against the source files and against VIEW_MANIFEST.txt):
  - `account.extended.yaml` af1be87074c8bb756f32e0d6c4eed997039906f6de652e137f2c3e5d0ac41cd8 (view copy == source)
  - `task_tools.py` 1dd82022d7f192b4cb494eb7fbfcc77e2c9b5bba4a62aa572a6a5866759e875a (view copy == source)
- Permitted: `blueprint/` (blueprint.yaml, db_schema.json, share_tools.py, products/*.yaml), the two files above, and the masked views `/tmp/erl0030_views/policy_task/sender_verification_and_limits/tasks/{0,1}.json` (frozen_time, user_scenario, initial_state only).
- Masked / unread at freeze: evaluation_criteria, computations, design_rationale, db_closure*, solvability_contract, prerequisite_closure, charter_scope, required_documents of both tasks; every worklog.md; any prior audit (none exists — this is revision 0).
- Entry conditions (Step 0): gate snapshot supplied in the brief and in `/tmp/erl0030_gates/sender_verification_and_limits.txt` — check_extended EXTENDED OK, check_task_tools TASK TOOL CONTRACT OK, replay_tasks REPLAY OK, check_solvability SOLVABILITY OK, check_compute COMPUTE OK, check_grounding GROUNDING OK, check_cache_diff INFO, check_cross_fire SCOPE OK; check_traceability not run (needs the published KB). Masked views and hashes supplied. Input complete.
- Base-copy check: lines 1–1580 of `account.extended.yaml` are byte-identical to `blueprint/products/account.yaml` (`diff` shows only the appended 6-line extended banner comment). Base copy verbatim.
- Method note: the compute DSL evaluator (`within_months`, `MONTHS`, `DAYS`, `X*`, `NOW`) is not in `erlbench/` and lies outside the read domain; every compute binding was read by its `compute_basis` prose (window "an entry dated on the same calendar day N months earlier or before it no longer counting", customer-scoped cross-category reads, date-level `NOW`), and the supplied COMPUTE OK / REPLAY OK gates are cited for executability.

### policy_conflict_scan

Five extended policies, all on category `account`:

| id | subject | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- | --- |
| P1 account_ext_review_decision_window | account_limit_review_requested | lodge_limit_review_54a88584 (user) | decision_window_business_days | [] |
| P2 account_ext_limits_callback_window | account_callback_scheduled (topic limits and levels) | schedule_limits_callback_7588c2a7 (agent) | callback_window_business_days | P1, value_input, state |
| P3 account_ext_upgrade_refresh_interval | account_level_upgraded | apply_level_upgrade_725c1de1 (agent) | review_interval_months | [] |
| P4 account_ext_statement_delivery_window | account_statement_requested | request_account_statement_ee1d8031 (user) | delivery_window_business_days | P3, value_input, state |
| P5 account_ext_fees_callback_window | account_callback_scheduled (topic refunds and fees) | schedule_fees_callback_4571f432 (agent) | callback_window_business_days | P4, value_input, state |

- Overlapping subjects: P2 and P5 share `account_callback_scheduled`; they are partitioned by topic ("governs callbacks on limits and levels only" / "governs callbacks on refunds and fees only") and by distinct target tools whose topic is fixed in the tool body (`callback_topic="limits_and_levels"` / `"refunds_and_fees"`). No overlap in conclusions.
- Both P2 and P5 supersede the same base sentence ("Its callback_due_date is the request date plus the level's callback_sla_business_days ..."), each with a topic-scoped replacement; merged semantics for the two scored topics are unique (see observation D-O3 on other topics).
- Triggers: all `on_request`. Eligibility/state: every extended policy inherits its base eligibility (active / not closed / not pending_verification, limit-review next-level, cooldown, frequency, undecided-request dedup; upgrade documents/age/transfers; statement history, statements_per_12m cap). No extended rule weakens any of them.
- Time anchors: all windows are counted back from the request/upgrade date with an exclusive "same calendar day N months earlier" boundary; every result is counted forward in Paloma business days (P1, P2, P4, P5) or whole calendar months (P3); the tools implement exactly that arithmetic and nothing more.
- Cross-category reads: bank/cash/wallet ledgers and cases, read-only history; declared per policy.
- Terminal states: each tool writes one row (P1, P2, P4, P5 → `sender_account_events`) or updates the account (P3 → `variant_name`, `level_effective_date`, `next_review_due_date`). No two policies write the same field of the same row.
- Scope partition (inferred from the prerequisite graph and from the root each `user_scenario` raises, not from the masked `charter_scope`): task 0 = {P2 root, P1}; task 1 = {P5 root, P4, P3}. Pairwise disjoint and jointly complete over the five extended policies.
- Conflicts found: one undeclared override (D-F1, below). Otherwise no conflict.

### rule_compute_equivalence

Check 2, sentence by sentence, both directions.

- P1: every binding has a verbatim `compute_basis` quotation; windows 24 / 6 / 1 / 12 months with the exclusive same-day boundary in prose match `within_months` filters; tiers of seasoning (30 / 180 days), declines (decline ∧ RFI; decline ∧ ¬RFI; none), sending (8000 / 20000 USD over bank_payout_sent + cash_payout_made + wallet_credit_sent), fresh documents (1 / 3), cash reliance (4 / 8), escalation (2 / 4 recipients; round up to multiple of 5; + ceil(half)) are each a rule sentence and a branch of the binding. `(counted_window + 1) // 2` = "half of it, that half rounded up". Sweep back: no compute term without a rule sentence. One drift in form only: `requested_review_days` keys on the **current** `variant_name` (Verified Plus→3, Enhanced→5, Premier→7) while the rule keys on "the level requested"; under the inherited base gate "the requested level must be exactly one level above the current level" the two coincide on every admissible request (observation D-O4).
- P2: all ten bindings quoted; `MX(shortest_window_days, …)` = "never fewer than shortest_window_days"; "exactly one_answer" vs `>= one_answer` is equivalent because the `>= many_answers (2)` branch is tested first; ceiling payouts compare `amount_usd` to `P('per_transfer_limit_usd')` of the level held = rule; queue step three tiers = three branches. No empty promise.
- P3: all bindings quoted; floors 12 and 3 present in rule and compute; payee spread `== single_payee_count` = "exactly single_payee_count recipient"; rejections `== rejections_one` = "exactly rejections_one"; evidence-age three tiers = three branches; "less the whole calendar months already run" = `risk_weighted_months - months_already_run`.
- P4: all bindings quoted; allowance "reaches" = `>=`, "more than half" = `*2 >`; open notices "notices on record less the error decisions on record" per method, no window, = compute; consolidation 3 / 2 / ≤1 methods = branches.
- P5: all bindings quoted; net fees = charged − refunded per method over 12 months; preparation tier 1 (≥1 fees callbacks in 12 months) precedes tier 2 (none ∧ period > 12 whole months) in both faces.
- Every declared factor's ladder (`factors[].ladder`) is stated tier by tier in the rule and is a branch of its `decides` binding; no tier lives only in one face.
- Verdict: equivalent in both directions. `inputs.history` lists are incomplete for P4/P5 (e.g. P5 lists only the cash fee-refund count, P4 omits the `*_error_decided` counts) — descriptive metadata, no effect on compute (observation D-O7).

### action_binding_and_uuids

- `(target_tool, computes)` pairs are all distinct; P2 and P5 both compute `callback_window_business_days` but on different tools. Each tool is claimed by exactly one policy.
- Docstrings: each describes one atomic write, its arguments and its receipt; none names another tool, none states a sequence position, none carries before/after/first relative to another action ("today itself not counted" is date arithmetic). No confirmation, review or wait is added.
- Tool bodies: pure writes — `ctx.find` only to copy `customer_id`; no status check, no refusal, no prerequisite validation, no hint (all five read in full).
- uuid8s: 54a88584, 7588c2a7, 725c1de1, ee1d8031, 4571f432 — pairwise distinct, no shared prefix or tail, not sequential, not adjacent. Independent.

### prerequisite_graph

Check 7.
- `prerequisite` filled on all five (P1, P3: `[]`).
- Edges: P2→P1, P4→P3, P5→P4. Every `problem` is an extended policy id of this file, none self, none base. Acyclic (two chains: P2←P1; P5←P4←P3).
- `policy_source` verbatim in the blocked policy's own `rule`: P2 first sentence, P4 first sentence, P5 first sentence — all located verbatim.
- `form: state` on all three; no `fallback_reason` (correctly absent).
- `kind: value_input`, `gate` names a real binding: P2 `decision_gap_days`, P4 `allowance_days`, P5 `statement_gap_days` — all exist in the blocked policy's compute.
- `resolved_by` = depended-on policy's `target_tool` in all three (lodge_limit_review_54a88584, apply_level_upgrade_725c1de1, request_account_statement_ee1d8031); each tool's effect makes the state hold (an undecided request row dated today; `variant_name` raised; a statement row dated today).
- `condition`: P4 and P5 match their sentences. P2's `condition` adds "dated the handling date" to a sentence that only requires "a limit review request that compliance has not yet decided" — strengthened (observation D-O1).
- No authoring-viewpoint phrasing ("the handling date" is general).

### prerequisite_sentences

Check 6, four-point test per edge.

1. P2 ← P1: "A callback on limits and levels is not booked until the account history carries a limit review request that compliance has not yet decided." — ordering connective "not … until" joins P2's own result (the callback booked) to a record-visible state (account history row: limit review request with no decision); no tool, id or snake_case; scope "a … request" (open) matches an undecided-request check. Writes that bring the state about: only `lodge_limit_review_54a88584` (no other tool of this difficulty writes `account_limit_review_requested`). Derivation: reader sees no undecided request → finds in P1/base `account_evt_limit_review` the write that lodges one → that write is the customer's own (owner=user) → single reading.
2. P4 ← P3: "The delivery window of a statement is fixed only after the account holds a level whose statement history reaches back to the first day of the period requested." — "only after"; state = `sender_accounts.variant_name` at a level whose `statement_history_months` covers the period start; no tool or id. Only `apply_level_upgrade_725c1de1` raises the level in this difficulty (the limit-review route raises a level only by a compliance decision, which no tool here writes). The level is then fixed by base `account_evt_level_upgrade` "the agent applies the highest qualifying level whose review_required_for_entry is false". Single reading.
3. P5 ← P4: "A callback on refunds and fees is not booked until the account history carries a statement request dated the day the callback is requested." — "not … until"; state = statement-request row dated today; only `request_account_statement_ee1d8031` writes it. Single reading.
- Each blocked rule carries its dependency once; P1, P3, P4 (as depended-on rules) do not restate the sentences of their dependants; no rule names a tool or another policy id in prose (P1 names none; base `account_sending_limits` names base policy ids, base text, not extended).
- Base-rule cross-problem orders ("a document that is missing … must be submitted again before the request"; "an open transfer must first finish … before closure"; review-gated upgrade only by an approved decision) ground no declared edge and no tree of this difficulty rests on them (observation D-O5).
- No undeclared cross-problem order in any extended rule.

### override_declarations

Check 1, finding half, sentence by sentence against each `base_policy_refs` entry.

- P1 vs `account_evt_limit_review`: decision_due_date sentence — declared superseded. All other sentences (active only; next level exactly; documents logged; cooldown; no undecided request; frequency; outcomes) followed/inherited. vs `account_sending_limits`: not touched.
- P2 vs `account_evt_service_entitlements`: callback_due_date sentence — declared superseded. Sentence "A level with dedicated_support_line true is called back from the priority line, and a level with relationship_manager_assigned true is called back by the named relationship manager; neither changes the due date." — **contradicted and not declared** (P2 queue tier 2 halves the window when "the level the account holds has a dedicated support line"). → D-F1. "A callback can be scheduled for any account that is not closed." — P2's prerequisite sentence adds a further gate for limits-topic callbacks only; it narrows, does not weaken, and is the mechanism of a declared state-form edge (no conflict on a scored quantity; noted only).
- P3 vs `account_evt_level_upgrade`: next_review_due_date sentence — declared superseded. Level choice, documents, age, transfers, active-only — inherited. vs `account_sending_limits`, `account_evt_funding_entitlements`: not touched.
- P4 vs `account_evt_service_entitlements`: delivery_due_date sentence — declared superseded. History limit and statements_per_12m cap inherited. Allowance step counts its own 12-month window with an exclusive boundary while the cap's measure `account_msr_statements_12m` is inclusive of the same day 12 months earlier — two counts for two different purposes, the scored tier governed explicitly by P4's own sentence (observation D-O2).
- P5 vs `account_evt_service_entitlements`: callback_due_date sentence — declared superseded; no priority-line tier in P5, so the "neither changes the due date" sentence does not conflict with P5.
- Disguised forms: no anonymous intermediate, no 0/1 multiplier on a base amount, no dropped base branch found.

### factor_ladders

| policy | factor | effect | decides | tiers | multi-source tier | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | level_seasoning | parameter | seasoning_days | 3 (2/1/0) | no | — |
| P1 | earlier_declines | parameter | redecision_days | 3 (2/1/0) | yes (declined decision ∧ RFI / ∧ ¬RFI: two event types) | — |
| P1 | recent_sending | parameter | volume_days | 3 (2/1/0) | sum over three ledgers | bank (also cash, wallet) |
| P1 | fresh_documents | parameter | document_days | 3 (2/1/0) | no | — |
| P1 | cash_reliance | parameter | cash_days | 3 (2/1/0) | no | cash |
| P1 | review_escalation | method | escalated_window | 3 (round to ×5 / +ceil half / as is) | no | — |
| P2 | decision_distance | parameter | decision_distance_days | 3 (2/1/0) | no | — |
| P2 | account_age | parameter | account_age_days | 3 (2/1/0) | no | — |
| P2 | answered_transfer_information | parameter | answer_days | 3 (2/1/0) | no | bank |
| P2 | new_payees | parameter | payee_days | 3 (2/1/0) | no | — |
| P2 | ceiling_payouts | parameter | ceiling_cut_days | 3 (−3/−2/0) | ledger amount vs level parameter | bank |
| P2 | callback_queue | method | queued_callback_days | 3 (+ceil half / ceil half / as is) | yes (no earlier callback due ∧ dedicated line) | — |
| P3 | refresh_cash_reliance | parameter | cash_cut_months | 3 (6/3/0) | no | cash |
| P3 | payee_spread | parameter | payee_cut_months | 3 (6/3/0) | yes (bank principal ∧ recipients added) | bank |
| P3 | rejected_documents | parameter | rejection_cut_months | 3 (6/3/0) | no | — |
| P3 | evidence_age_start | method | months_already_run | 3 (from ID / from selfie / from upgrade) | yes (ID age ∧ selfie age) | — |
| P4 | yearly_statement_allowance | parameter | allowance_days | 3 (2/1/0) | history ∧ level parameter | — |
| P4 | statement_transfer_volume | parameter | volume_days | 3 (2/1/0) | sum over three ledgers | bank (also cash, wallet) |
| P4 | open_error_notices | parameter | notice_days | 3 (2/1/0) | notices − decisions, three methods | bank (also cash, wallet) |
| P4 | compliance_release | parameter | release_days | 3 (2/1/0) | no | — |
| P4 | ledger_consolidation | method | consolidated_days | 3 (round to ×5 / +ceil half / as is) | three ledgers | wallet (also bank, cash) |
| P5 | statement_wait | parameter | statement_wait_days | 3 (2/1/0) | no | — |
| P5 | fee_refunds | parameter | refund_days | 3 (2/1/0) | three ledgers | cash |
| P5 | fees_paid | parameter | fees_paid_days | 3 (2/1/0) | charged − refunded, three ledgers | bank |
| P5 | specialist_preparation | method | prepared_fees_callback_days | 3 (ceil half / +ceil half / as is) | yes (no fees callback ∧ long statement period) | — |

- Counts: P1 6 (5 parameter, 1 method); P2 6 (5, 1); P3 4 (3, 1); P4 5 (4, 1); P5 4 (3, 1). All within 4–6, ≥2 parameter, ≥1 method.
- Per task (scope above): task 0 {P1, P2} — multi-source earlier_declines, callback_queue; cross-difficulty recent_sending, cash_reliance, answered_transfer_information, ceiling_payouts. Task 1 {P3, P4, P5} — multi-source payee_spread, evidence_age_start, specialist_preparation; cross-difficulty refresh_cash_reliance, payee_spread, statement_transfer_volume, open_error_notices, ledger_consolidation, fee_refunds, fees_paid.
- Binding sets disjoint within each policy; every `decides` is an input to `result`, never `result` itself.
- Ladders: every ladder has three pairwise-disjoint tiers including the fall-through; no two tiers of one ladder select the same value or method; every fall-through equals the policy baseline (0 added / counted window as is / nothing already run), and every factor's `baseline` binding encodes exactly that.
- Labels: `parameter` factors change a number added/subtracted; `method` factors change the algorithm (round to a multiple, add a rounded half, halve, or move the interval's starting point) — honest. Each method is stated in the charter's own rule.
- Realism: conditions (time at level, earlier declines with/without RFIs, recent volume, fresh documents, cash reliance, new payees, answered RFIs, ceiling hits, queued callbacks, stale ID evidence, rejected documents, statement allowance use, open error notices, recent RFIs, multi-ledger reconciliation, fee refunds, net fees, recent fees callbacks, long statement periods) are each something a regulated remitter's compliance, KYC or service desk weighs for that quantity; none holds of every customer reaching its write (in particular P2 decision_distance and P5 statement_wait have reachable fall-throughs: an Enhanced review or a 3-day statement window can fall under 7 calendar days). Fall-through treatments (standard SLA / standard 36-month refresh) are the published base values — not straw men.
- Baselines: each `baseline.rule` is self-sufficient (P1: review time of the requested level; P2/P5: callback_sla of the level held; P3: 36 months; P4: statement_delivery of the level held), every sentence of it is in the `rule`, and `baseline.params` names exactly its default keys.

### findings

**D-F1 — SOURCE-POLICY RED (undeclared override). Bears on task 0 (P2 is in its scope); task 1's file records why it does not bear there.**
- Symptom: P2's queue step changes a callback's due date for a level with a dedicated support line; base says the dedicated line never changes it.
- Root cause: P2's `overwrite` names only the base callback_due_date sentence, not the base sentence that also governs the due date.
- Evidence: base `account_evt_service_entitlements.rule` (account.extended.yaml base section, also blueprint/products/account.yaml): "A level with dedicated_support_line true is called back from the priority line, and a level with relationship_manager_assigned true is called back by the named relationship manager; neither changes the due date." vs P2 `rule`: "when no earlier callback is still due and the level the account holds has a dedicated support line, the priority line takes it and the limits callback window is half the counted limits callback window, rounded up to a whole business day". P2 `overwrite[0].superseded_clause` quotes only "Its callback_due_date is the request date plus the level's callback_sla_business_days Paloma business days …".
- Demonstrated consequence (same situation, two conclusions): a Paloma Premier account (dedicated_support_line true, callback_sla 1), no earlier callback still due, counted limits window W = 4 → base sentence: the priority line does not change the due date, window 4; P2: window ceil(4/2) = 2. Two different callback_due_date values for one booking.
- Affected: account.extended.yaml P2 `overwrite` / P2 `rule` queue step; `compute.queued_callback_days` branch 2; any task world with a dedicated-line level and no still-due earlier callback.
- Previous revisions: none (revision 0).

**Observations (no consequence demonstrable on a scored value; not grounds for rework)**
- D-O1: P2 `prerequisite[0].condition` adds "dated the handling date" to a sentence that is met by any undecided request; in a world with an older undecided request, the sentence is met while the condition says unmet (and base forbids a second request). Neither task seeds an undecided request at the opening.
- D-O2: statements-in-12-months counted inclusively by base `account_msr_statements_12m` (cap) and exclusively by P4's allowance step; diverges only when a statement request sits exactly 12 months before the request date. Task 1 seeds none on that day.
- D-O3: P2 and P5 each supersede the base callback_due_date sentence with a topic-scoped replacement; callbacks on any other topic (e.g. `verification_documents`) are left without a due-date sentence in force. No task books such a callback.
- D-O4: P1 `requested_review_days` keys on the current level instead of the requested level; equal under the inherited next-level gate.
- D-O5: base cross-problem orders (documents before a limit review, open transfers before closure) ground no edge; no tree of this difficulty rests on them.
- D-O6: compute DSL semantics read from prose; evaluator source outside the read domain.
- D-O7: `inputs.history` lists of P4/P5 incomplete relative to compute.
- D-O8: the blueprint claims `account_unlocked`, `account_document_received`, `account_closed_by_customer`, `account_appeal_lodged` for this difficulty, but no extended policy or task tool covers them; outside the four relationships of these two tasks.

## closing_checklist

Written after both tasks' frozen derivations and post-reveal comparisons were on disk (reveal 2026-10-04T16:40:08Z). Everything above this heading was written before the reveal and is unchanged.

- Per-task files correspond one to one with tasks: 0.md and 1.md, next to this file. This is revision 0; there are no older revisions.
  - Comparison verdicts: task 0 has SOURCE-POLICY RED (D-F1) with tree, factors and unique solution PASS. Task 1 passes all four relationships.
- Coverage and scope:
  - The five extended policies are covered exactly. Task 0 covers {P1, P2}. Task 1 covers {P3, P4, P5}. This matches each task's `charter_scope` as revealed.
  - The scopes are disjoint across the whole problem trees.
  - The task tools and the GT writes are closed: every task tool is called exactly once, by its policy's task.
  - The uuid8s are independent.
- Problem trees:
  - Task 0 has 1 prerequisite problem and 1 value_input edge. Task 1 has 2 prerequisite problems and 2 value_input edges.
  - Each tree has a customer-owned write: the lodge in task 0, the statement in task 1.
  - The difficulty-wide graph has edges P2→P1, P4→P3 and P5→P4, and is acyclic.
- Factors:
  - Every computation has 4 to 6 factors, with at least 2 parameter and at least 1 method.
  - Each task has a multi-source factor and a cross-difficulty factor.
  - Every factor bears weight against an honest baseline.
  - Every policy's baseline alone gives a definite number different from gold: 3/14, 2/8, 36/7, 3/11, 3/4.
- Gates: this auditor did not re-run them, because the artifacts were not changed (the hashes of `account.extended.yaml`, `task_tools.py` and both task files equal the frozen hashes). The supplied snapshot stands.
- **Difficulty status: NOT CLOSED.**
  - Charter-global SOURCE-POLICY RED D-F1 is open. The undeclared override of the base sentence "neither changes the due date" by P2's priority-line tier sits in the scope of task 0.
  - All other relationships pass for both tasks.

## revision_2

### charter_global_frozen (revision 2)

- Written 2026-10-04 at about 17:09Z, before any round-2 GT field was opened. Nothing in this section is derived from a round-2 GT. Auditor: the same independent auditor as revision 0. Revision 0 text above is left untouched.
- Inputs:
  - `account.extended.yaml`: 04782c2f85258f23e7dc7adb88803effe2e50d465d9225f274560be266c40499. This is **changed** from revision 0 (af1be870…). The view copy equals the source.
  - `task_tools.py`: 1dd82022…9875a, unchanged. The view equals the source, confirmed by `diff`.
  - `blueprint/products/account.yaml`: lines 1–1580 of the new extended charter are byte-identical to it. The base copy is still verbatim.
- Re-derivation rule: the charter hash changed, so every charter-global section below is re-derived in full, not carried forward. The tool module is unchanged, so `action_binding_and_uuids` is carried forward on the unchanged hash 1dd82022….
- Gate snapshot `/tmp/erl0030_gates/sender_verification_and_limits.r2.txt`: all eight gates exit 0. Results: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (0.json 17 acts 81/81, 1.json 21 acts 80/80), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK. check_traceability is deferred. The entry conditions are met.
- contamination_disclosure (round 2): the auditor read the round-1 GT of both tasks at the revision-0 reveal (16:40:08Z). The round-2 charter checks below rest only on the charter, base, schema and tools. The per-task re-derivations in 0.md and 1.md cannot be blind to round-1 GT, and are recorded there as re-verifications.

### What changed in the charter

Every extended policy was re-read field by field. Changes found:

- **P1 `rule` and `baseline.rule`.** The standard-window sentence now keys on the level held: "…the compliance review time of the level requested, which is the level directly above the level the account holds: review_days_enhanced business days when the account holds Paloma Verified Plus and so requests Paloma Enhanced, …". The `compute_basis.requested_review_days` quote is updated to match. The compute is unchanged.
- **P2 `overwrite`.** A second entry was added. It supersedes the base sentence "A level with dedicated_support_line true is called back from the priority line, and a level with relationship_manager_assigned true is called back by the named relationship manager; neither changes the due date." It replaces it with "For a callback on limits and levels, a level with a dedicated support line is called back from the priority line and a level with a named relationship manager by that manager, and the priority line changes the due date of the callback as the queue step states."
- **P2 `rule`.** That replacement sentence is now a sentence of the rule.
- **P2 `prerequisite[0].condition`.** It now reads "…a row of event_type account_limit_review_requested with no account_limit_review_decided row pointing back to it." The strengthening "dated the handling date …" is removed.
- **P4 and P5 `inputs.history`.** These now list every compute read: P4 adds the three `*_error_decided` counts. P5 adds the bank and wallet fee-refund counts, the three fee-refund sums, and `statement_period_end`.
- **Everything else is unchanged.** This covers P3 entirely, and the rule, compute, compute_basis, factors, baselines, params, prerequisite sentences and cross_category of P1, P2, P4 and P5 except as listed. It was checked by re-reading each field against the revision-0 transcription.

### policy_conflict_scan (revision 2)

- The subjects, target tools, triggers, eligibility inheritance, time anchors, cross-category reads and terminal states of P1–P5 are as in revision 0.
- Scope partition: task 0 = {P2 root, P1}; task 1 = {P5 root, P4, P3}. It is unchanged, pairwise disjoint and jointly complete.
- The new P2 sentence conflicts with no other extended policy:
  - P5 has no priority-line tier, so the due date of a fees callback is unaffected by the line under any reading.
  - The superseding entry is declared on P2 and its replacement is scoped "For a callback on limits and levels".
- No new conflict.

### rule_compute_equivalence (revision 2)

- The check was re-run mechanically and then read.
  - Every `compute_basis` quotation of every policy is verbatim in that policy's `rule`.
  - Every compute binding has a `compute_basis` entry, except the `result` aliases of P1, P4 and P5. Those are plain aliases (`result: escalated_window` / `consolidated_days` / `prepared_fees_callback_days`), as in revision 0.
  - Every `baseline.rule` sentence is in its `rule`.
- **P1.** The rule now names the held-level to requested-level mapping. It is exactly the `requested_review_days` branches: Verified Plus → 3, Enhanced → 5, Premier → 7, else 0. Equivalence now holds literally, not only through the next-level gate.
- **P2.** The added sentence promises a due-date change only "as the queue step states". Its only computational content is branch 2 of `queued_callback_days`, which the rule's queue step already states. The relationship-manager clause carries no due-date effect, and no compute binding is given for it. Both directions hold, with no empty promise and no invented basis.
- **P3, P4, P5.** Unchanged and equivalent (revision 0 conclusions re-confirmed on the re-read text). The `inputs` lists now match compute; they are descriptive.

### action_binding_and_uuids (revision 2)

- Carried forward on the unchanged `task_tools.py` hash 1dd82022…. The `(target_tool, computes)` pairs in the charter are unchanged: the five target tools and five `computes` values were re-read.
- Each pair is still claimed once. The uuid8s are 54a88584, 7588c2a7, 725c1de1, ee1d8031 and 4571f432; they are independent.

### prerequisite_graph (revision 2)

- The edges are P2→P1, P4→P3 and P5→P4. All are value_input and state form, with no fallback. The gates (decision_gap_days, allowance_days, statement_gap_days) exist in compute. Each `resolved_by` is the depended-on policy's target tool. The graph is acyclic.
- Each `policy_source` was re-verified mechanically and is verbatim in its own `rule`.
- The `condition` fields:
  - P2: "…a row of event_type account_limit_review_requested with no account_limit_review_decided row pointing back to it." This now matches the sentence exactly. D-O1 is closed.
  - P4: unchanged and matching.
  - P5: unchanged and matching ("dated the day the callback is requested" = "whose event_date is the handling date").

### prerequisite_sentences (revision 2)

- The three sentences are unchanged. The four-point test, the single-write test and the single-reading derivations of revision 0 hold as written there.
- The new P2 sentence is not a cross-problem order. It relates the callback to the level's support line, which is a parameter of the level held. It names no tool and no policy id. It grounds no edge and needs none.
- No depended-on rule restates a dependant's sentence. No undeclared cross-problem order is found in any extended rule.

### override_declarations (revision 2)

Re-run sentence by sentence against every `base_policy_refs` entry.

- **P1 vs `account_evt_limit_review`:** the decision_due_date sentence is declared. All other sentences are inherited. The new P1 wording of the standard window restates the base next-level rule and contradicts no base sentence.
- **P2 vs `account_evt_service_entitlements`:**
  - The callback_due_date sentence is declared.
  - The dedicated-line / relationship-manager sentence is **now declared** (overwrite[1]). Its `superseded_clause` is verbatim in base. Its `replaced_by` is verbatim in P2's rule.
  - Merged semantics for a limits callback are unique. The priority line changes the due date only through queue tier 2, and the relationship manager changes nothing.
  - Revision-0 demonstration situation, re-run: a Paloma Premier account with no earlier callback still due and counted window 4. The base sentence no longer stands for limits callbacks, so the only reading left is P2's: ceil(4/2) = 2. **D-F1 is closed.**
  - "A callback can be scheduled for any account that is not closed." This is narrowed for limits callbacks by P2's prerequisite sentence, as in revision 0. It is not a conflict on a scored quantity.
- **P3, P4, P5:** as in revision 0 (declared overrides only; D-O2 is unchanged).
- **Residual effect of the new supersession, recorded as observation D-O3 (extended).** P2 supersedes a base sentence of a shared base policy, with a replacement scoped to the limits topic. A callback on any other topic is left with no sentence stating whether the priority line or the relationship manager serves it or changes its due date. P5 (refunds and fees) defines its own window without a priority tier, so its due date is fixed either way. Callbacks on other topics, such as `verification_documents`, are booked by no tool of this difficulty. No scored value is affected.
- Disguised forms: none found.

### factor_ladders (revision 2)

- Factors, labels, `decides`, bindings, ladders, baselines and `cross_difficulty` are unchanged for all five policies. They were re-read; the revision-0 table holds unchanged.
- Counts: P1 6 (5 parameter, 1 method), P2 6 (5, 1), P3 4 (3, 1), P4 5 (4, 1), P5 4 (3, 1).
- The per-task multi-source and cross-difficulty factors are as in revision 0.
- Realism, label honesty and baseline self-sufficiency hold. The new P1 baseline wording is still self-sufficient: a definite review time per held level.

### findings (revision 2)

| round-1 item | rework claim | verified status |
| --- | --- | --- |
| D-F1 (SOURCE-POLICY RED, undeclared override) | closed | **Closed.** Declared in P2 overwrite[1], and the replacement is a sentence of P2's rule. The two clauses no longer fight over the limits-callback due date. |
| D-O1 (strengthened condition) | acted on | **Closed.** The condition now equals the sentence's state. |
| D-O2 (12-month boundary, base cap vs P4 allowance) | unchanged | **Unchanged.** The observation stands. |
| D-O3 (other callback topics left without a due-date sentence) | unchanged | **Unchanged and widened.** Other topics now also lack the dedicated-line / relationship-manager sentence. No scored write is affected. |
| D-O4 (P1 compute keyed on held level) | acted on | **Closed.** The rule now states the held-level mapping. |
| D-O5 (base cross-problem orders) | unchanged | **Unchanged.** The observation stands. |
| D-O6 (DSL evaluator unread) | unchanged | **Unchanged.** The observation stands. |
| D-O7 (incomplete inputs lists) | acted on | **Closed.** P4 and P5 list every read. |
| D-O8 (claimed event types without tools) | unchanged | **Unchanged.** The observation stands. |

- New charter-global defects: **none.**
- Regressions: **none.** P3 is untouched. The P1, P2, P4 and P5 changes alter no compute, factor, threshold, prerequisite sentence or tool.

### closing_checklist (revision 2)

Written after both tasks' revision-2 comparisons, following the reveal at 17:09:29Z. Everything above this heading in revision_2 was written before the reveal.

- **Audit files.** `0.md` and `1.md` each carry revision 0 and revision 2, and the older text is untouched. Both revision-2 comparisons are PASS on all four relationships.
- **Scope and coverage.**
  - The five extended policies are covered exactly once: task 0 {P1, P2}, task 1 {P3, P4, P5}. This equals each task's revealed `charter_scope`.
  - Scopes are disjoint, and the task tools and GT writes are closed.
  - The uuid8s are independent; the tool module is unchanged.
- **Trees.**
  - Task 0 has 1 prerequisite problem and 1 value_input edge.
  - Task 1 has 2 prerequisite problems and 2 value_input edges.
  - Each task includes the customer's own write.
  - The difficulty-wide graph is acyclic.
- **Factors.**
  - Every computation has 4–6 factors, with at least 2 parameter and at least 1 method.
  - Each task has a multi-source and a cross-difficulty factor.
  - Every factor bears weight against an honest baseline.
  - Each baseline alone gives a definite non-gold number: 3, 2, 36, 3 and 3 against gold 14, 8, 7, 11 and 4.
- **Gates.** These were re-run on the final form by the coordinator (`/tmp/erl0030_gates/sender_verification_and_limits.r2.txt`), and all exit 0. The audited artifact hashes now equal those the gates ran on: extended 04782c2f…, tools 1dd82022…, 0.json ddab8201…, 1.json 98b15b64…. check_traceability is deferred to the KB stage.
- **Round-1 RED.** D-F1 is genuinely closed. D-O1, D-O4 and D-O7 are closed. D-O2, D-O3 (widened, with no scored effect), D-O5, D-O6 and D-O8 remain observations.
- **New defects and regressions:** none.
- **Difficulty status: CLOSED.** The source-layer audit passes. Policy self-consistency, problem tree, factor weight and unique solution are PASS for both tasks.

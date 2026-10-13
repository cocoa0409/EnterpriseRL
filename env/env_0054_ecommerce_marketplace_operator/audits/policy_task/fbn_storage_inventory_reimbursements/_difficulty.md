# Policy-task audit — fbn_storage_inventory_reimbursements / charter-global

## charter_global_frozen

- Freeze time: 2026-10-11T04:58Z (written before any task's GT was revealed; nothing below derives from a revealed GT).
- Auditor: independent policy-task auditor (erl-task-policy-audit), M=2 (tasks 0 and 1).
- Frozen inputs (sha256, recomputed by the auditor and equal to HASHES.txt):
  - `tasks/fbn_storage_inventory_reimbursements/fulfill.extended.yaml` ea5a56f10b4969f7d29a2554ad34d1d01f60d255660c17a75e812aa8af46e028
  - `tasks/fbn_storage_inventory_reimbursements/task_tools.py` 87d67070f1d6e944b6e8543a4ea3635c33c410ffece9d10313ca9b57a6046adc
  - source `tasks/0.json` b99a7f40…e304, source `tasks/1.json` ce70e934…a686 (match HASHES.txt); views `0.view.json` 2d175c8d…e3, `1.view.json` 89df60e5…4f (match).
- Permitted: blueprint (`blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/fulfill.yaml`, and the cross-read charters `selling.yaml`, `payout.yaml`(not opened), `standing.yaml`), the extended charter, `task_tools.py`, the masked views (frozen_time, user_scenario, initial_state), the coordinator's gate snapshot `gates.r1.txt` and `claim.txt`, and the instantiation gate's DSL evaluator (`skills/erl-task-instantiate/scripts/check_compute.py`, used only to evaluate the charter's own `compute`).
- Masked / unread until every task froze: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`. No recursive search was run over `env/` or `tasks/`.
- Entry conditions (Step 0): gate snapshot present with commands and actual output lines — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK (all rc=0); check_traceability deferred by the coordinator until the KB is published. Masked views and hashes supplied and verified. Entry conditions met.
- Base-copy check: every base key of `fulfill.extended.yaml` (category … policies) is equal to `blueprint/products/fulfill.yaml` (parsed equality, and a line diff shows only the appended `extended_policies` header). Base copy verbatim.

### policy_conflict_scan

Five extended policies, all `base_policy_refs: [fulfill_reimbursement_terms]`, all `subject: [fulfill_reimbursement]`:

| policy | computes | target_tool (owner) | case kind it acts on | prerequisite |
| --- | --- | --- | --- | --- |
| fulfill_ext_lost_claim_units | units_claimed | amend_lost_inventory_claim_06dd83f3 (user) | open lost_in_warehouse case | [] |
| fulfill_ext_lost_case_approval | units_approved | approve_lost_inventory_case_b95e2fef (agent) | open lost_in_warehouse case | ← lost_claim_units (value_input, state) |
| fulfill_ext_shortage_claim_units | units_claimed | amend_inbound_shortage_claim_fdee09ae (user) | open inbound_shortage case | [] |
| fulfill_ext_damaged_case_approval | units_approved | approve_damaged_inventory_case_556f0f6d (agent) | open damaged_in_warehouse case | [] |
| fulfill_ext_shortage_case_approval | units_approved | approve_inbound_shortage_case_dfebd527 (agent) | open inbound_shortage case | ← shortage_claim_units (value_input, state); ← damaged_case_approval (value_input, state) |

- Overlapping subjects are partitioned by case kind (`reimbursement_type` filter in every `compute` LATEST): no two policies decide the same quantity on the same case. Triggers all `state_due`. Cross-category reads: selling (variant_name, opened_date), payout (status), standing (variant_name, violation_points, status) — each declared in that policy's `cross_category` and matching the CFIELD calls.
- Two base-vs-extended conflicts surfaced by the scan are recorded under `override_declarations` / `findings` (F1).
- Scope: the claimed scope (`claim.txt`) is the whole fulfill reimbursement surface; the five extended policies split naturally into two trees — {lost_claim_units → lost_case_approval} and {shortage_claim_units, damaged_case_approval → shortage_case_approval}. Pairwise disjoint and jointly complete over the five policies if task 0 owns the first tree and task 1 the second (confirmed against each world blind: task 0's only open case is lost_in_warehouse, task 1's open cases are one damaged_in_warehouse and one inbound_shortage case). The per-task `charter_scope` is compared after reveal in each task file.

### rule_compute_equivalence

Swept binding by binding against `compute_basis` and back, sentence by sentence against each `rule`.

- fulfill_ext_lost_claim_units: every binding has a verbatim basis; the span convention ("fewer than that number of whole months … a span of zero months holds no record") is implemented by the evaluator's `0 <= MONTHS(d, NOW) < n` (check_compute.py `_within`) and `MONTHS` (day-of-month rollback). Lookback ladder, store bonus ladder, search-hold ladder, find-window ladder and ceiling-share ladder each appear in prose in the rule and as the branch of their `decides` binding. Observation O1 (naming): the ceiling sentence reads "the **standard** claim ceiling share of the units of the SKU on inbound receipts…", while the ladder sentence defines "**The** claim ceiling share is the high … the low … and the standard claim ceiling share …"; `claim_ceiling` uses the laddered `ceiling_share`. The link from the ladder to the ceiling rests on the reader treating the named default as one tier of the ladder (the same baseline-in-rule pattern as O2).
- fulfill_ext_lost_case_approval: equivalent, with Observation O3: the rule restricts the denied count to "FBN **reimbursement** cases denied among the cases opened inside the case-history span", but `denied_cases = COUNT('fulfill_cases', within_months=K('history_span'), date_field='created_at', case_status='denied')` has no `case_type` filter, so a denied `fee_dispute` case (a valid `fulfill_cases.case_type`) would count in compute and not under the rule. No fee-dispute case exists in either task world (task 0: 5 cases, task 1: 5 cases, all `reimbursement_claim`), so no scored consequence is demonstrable → observation.
- fulfill_ext_shortage_claim_units: equivalent. `other_shortage_cases = COUNT(... reimbursement_type='inbound_shortage') - 1` implements "no other inbound-shortage case inside the case-history span" assuming the open case is inside the 6-month span (true whenever the correction gate holds). The correction-time window sentence ("The case may be corrected only for a line whose receipt date is at least the inbound reconciliation wait and no more than the inbound shortage claim window before the handling date") is an eligibility gate with no compute binding (Observation O4; it holds in task 1: receipt 2026-08-28, handling 2026-10-09 = 42 days, within [15, 60]).
- fulfill_ext_damaged_case_approval: equivalent.
- fulfill_ext_shortage_case_approval: equivalent, with O3 again (`inbound_denied` has no `case_type` filter against "FBN reimbursement cases denied") and O1-style naming: the baseline sentence "The verification holdback is the standard inbound verification holdback in units" and the order sentence "first the verification holdback …" use "verification holdback", while the ladder sentence defines "The **inbound** verification holdback is …"; likewise "The line approval ceiling is the standard line ceiling share …" vs ladder "The line ceiling share is …".
- O2 (charter-wide, framework-mandated): every policy's rule states its baseline sentences unconditionally ("The warehouse-loss lookback is the standard lookback base.", "The approval share is the standard approval share.", …) and then the conditional ladder for the same quantity. Read literally these are two definitions of one quantity; the ladder sentences are the more specific and the skill requires baseline sentences to be in the rule, so this is recorded as an observation and not a red light. Where a specific task's second reading is worth recording it is noted in that task's file.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are unique: (06dd83f3, units_claimed), (b95e2fef, units_approved), (fdee09ae, units_claimed), (556f0f6d, units_approved), (dfebd527, units_approved). Each tool is the target of exactly one policy.
- Docstrings name no other tool and state no position in a sequence. "Afterwards the seller's case shows …" and "the reimbursement payment itself is then issued by Northloop's reimbursement run" describe the call's own effect and an off-surface system run, not an order among tools (Observation O5, no consequence).
- Tool bodies: each is a single `ctx.update("fulfill_cases", case_id, …)`; the three approve tools also set `case_status="approved"` and overwrite `units_claimed` with `units_approved`. No tool validates status, case kind, ownership, prerequisite or arithmetic (module docstring: "performs no eligibility, ownership, status or arithmetic judgement of its own"). Tool layer judges no prerequisite.
- uuid8s 06dd83f3, b95e2fef, fdee09ae, dfebd527, 556f0f6d: no shared prefix/suffix, no sequence, no visible derivation; independent.
- No share tool writes `fulfill_cases` (share_tools.py writes only `verification_log` and `handoff_log`); no withdraw/deny tool exists.

### prerequisite_graph

- `prerequisite` present on all five policies (three `[]`). Edges: lost_case_approval→lost_claim_units; shortage_case_approval→shortage_claim_units; shortage_case_approval→damaged_case_approval. All `problem` ids are extended policies of this file, none self, none base. Acyclic (depth 1).
- `policy_source` verbatim in the blocked policy's own rule (whitespace-normalised substring test: True for all three).
- `form: state` on all three; no `fallback_reason` (correctly absent).
- `gate`/binding existence: `claimed_units` (lost approval compute), `inbound_claimed`, `inbound_approved` (shortage approval compute) — all exist; `kind: value_input` on all three.
- `resolved_by` equals the depended-on policy's `target_tool` in all three; each effect is real: amend rewrites `units_claimed` (feeds `claimed_units` / `inbound_claimed`); approve_damaged sets `case_status='approved'` (feeds `inbound_approved` via `COUNT(... case_status='approved')`).
- `condition` wording matches the sentence's strength ("carries, as its units claimed, the claimable … at handling time"; "No damaged-in-warehouse case of the shortage case's SKU that was opened before the shortage case has case_status submitted"). "at handling time" is the charter's general term (the rules use "handling date"), not authoring-viewpoint phrasing.

### prerequisite_sentences

Four-point test on each edge:

1. "The units approved on a warehouse-loss case are fixed only after the units claimed on that case equal the claimable lost units of its SKU." — connective "only after"; waited-on = a record-visible state (`fulfill_cases.units_claimed` equal to a quantity the lost-claim rule names in business words); no tool, id or snake_case; strength = condition. Derivation: sentence → the claimed units must equal "the claimable lost units of its SKU" → fulfill_ext_lost_claim_units' own rule: "the claimable lost units, the figure a seller enters as the units claimed when correcting their own open warehouse-loss case" → the seller's correction of their own case (amend_lost_inventory_claim, owner=user). One write brings the state about (the approve tool also writes `units_claimed`, but it is the blocked write itself). Single reading. PASS.
2. "The units approved on an inbound shortage case are not fixed until the units claimed on that case equal the claimable shortage of its shipment line." — "not … until"; same analysis → shortage-claim rule "the figure a seller enters as the units claimed when correcting their own open inbound-shortage case" → amend_inbound_shortage_claim (user). PASS.
3. "An inbound shortage case is decided only after no warehouse-damage case of the same SKU opened before it still stands submitted." — "only after"; state of `fulfill_cases.case_status` named in record words; no tool/id. Which write ends "stands submitted" for a damage case: only the damage policy's decision (approve_damaged_inventory_case, whose rule is "the units the support desk approves when it decides a seller's open warehouse-damage case"); no deny/withdraw write exists in this difficulty or the share layer, and the other two approve tools are bound by their policies/docstrings to warehouse-loss and inbound-shortage cases. Single reading. PASS.

- No depended-on rule restates its blocker's sentence; no rule carries a second wording, tool name or other problem id. No other cross-problem order is stated in any extended rule. Base rules state no cross-problem order that a task's tree rests on.
- Observation O6 (realism of edge 3): the dependency is a desk ordering convention (decide earlier same-SKU cases first) whose only effect on the blocked figure is through the approved-case count of the verification holdback; plausible as FIFO case handling, not a causal business dependency.

### override_declarations

Sentence-by-sentence against `fulfill_reimbursement_terms` (12 sentences):

| base sentence | lost_claim_units | lost_case_approval | shortage_claim_units | damaged_case_approval | shortage_case_approval |
| --- | --- | --- | --- | --- | --- |
| S1 "Northloop reimburses units lost or damaged in its custody." | follows | **declared overwrite** (units approved formula) | follows | **declared overwrite** | **declared overwrite** |
| S2 auto-reimburse after auto-reimburse days | not the scored quantity | same | n/a | same (see O7) | n/a |
| S3 "A warehouse loss claim is filed no later than the warehouse loss claim window counted in calendar days from the inventory adjustment date." | **declared overwrite** (replaced by the lost-in-warehouse claimable-units sentence) | covered via its prerequisite (claimed = claimable lost units) | n/a | **inherited, not declared; extended approves claimed units without it — see F1** | n/a |
| S4 inbound shortage: wait and window from receipt date | n/a | n/a | **declared overwrite**; the rule restates a correction-time gate | n/a | covered via its prerequisite |
| S5–S6 customer-return / removal-lost claims | n/a | n/a | n/a | n/a | n/a |
| S7 valuation at declared unit cost, capped | not touched (units only) | not touched (approval sets units; "the reimbursement run pays them") | not touched | not touched | not touched |
| S8 units already reimbursed on the same source object never reimbursed again | follows ("never claimed again"; lookback reimbursements subtracted) | follows (through claimed) | follows ("less the units already reimbursed as inbound shortage on the same shipment and SKU") | no explicit subtraction; no damage reimbursement in task 1's world | follows (through claimed) |
| S9 found reversal | not contradicted (found units netted; reversal unaffected) | n/a | n/a | n/a | n/a |

Disguised forms: no anonymous intermediate override, no 0/1 multiplier, no dropped branch found beyond F1. No author note calls base's output a wrong value.

### factor_ladders

| policy | factor | label | decides | tiers (fall-through = baseline) | multi-source? | cross_difficulty | honest label? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| lost_claim_units | lookback_base | parameter | lookback_base_months | 6 / 4 / **2** | no (program + activation date, one enrollment row) | — | yes |
| | store_lookback_bonus | parameter | store_bonus_months | 2 / 1 / **0** | no (plan + opened date, one selling row) | selling | yes |
| | search_hold | parameter | search_hold_months | 2 / 0 / **1** | no | — | yes |
| | find_matching_window | **method** | find_window_months | tenure+1 / 12 / **= lookback** (months) | yes (payout status + fulfill found rows) | payout | **no — see F2** |
| | claim_ceiling_share | parameter | ceiling_share | 0.06 / 0.025 / **0.04** | no | standing | yes |
| lost_case_approval | shrinkage_allowance_method | method | shrinkage_allowance | none / per-incident × adjustment count / **share × received, floored** | yes (program + standing level) | standing | yes |
| | allowance_cap | parameter | allowance_cap | 3 / 5 / **8** | no | — | yes |
| | verification_holdback_method | method | verification_holdback | share × claimed floored / 0 / **1 unit** | yes in tier 2 (denied + approved counts, same table) | — | yes (proportional vs fixed) |
| | compliance_holdback | parameter | compliance_holdback | 0 / 3 / **1** | tier 1: points + status (one standing row) | standing | yes |
| | approval_limit | parameter | approval_limit | 40 / 20 / **10** | no | selling | yes |
| | limit_uplift | parameter | limit_uplift | 10 / 5 / **0** | no | — | yes |
| shortage_claim_units | netting_scope | method | netted_shortage | whole shipment / same-cost lines / **line alone** | yes (placement-fee row + receipt rows) | — | yes |
| | carry_span | parameter | carry_span_months | 12 / 6 / **0** | no | — | yes |
| | tolerance_units | parameter | tolerance_units | 0 / 3 / **1** | tier 1: case history + enrollment tenure | — | yes |
| | tolerance_share | parameter | tolerance_share | 0.01 / 0.0 / **0.02** | no | — | yes |
| damaged_case_approval | damage_allowance_method | method | damage_allowance | none / per-incident × count / **share × received, floored** | yes (program + standing) | standing | yes |
| | damage_allowance_cap | parameter | damage_allowance_cap | 1 / 2 / **4** | no | — | yes |
| | damage_compliance_holdback | parameter | damage_compliance | 0 / 3 / **1** | one standing row | standing | yes |
| | damage_approval_limit | parameter | damage_limit | 40 / 20 / **8** | no | selling | yes |
| | damage_limit_uplift | parameter | damage_uplift | 6 / 3 / **0** | no | — | yes |
| shortage_case_approval | approval_share | parameter | approval_share | 1.0 / 0.75 / **0.9** | no | standing | yes |
| | inbound_verification_holdback | method | inbound_verification | share × claimed floored / 0 / **1 unit** | tier 2 (denied + approved counts) | — | yes |
| | inbound_compliance_holdback | parameter | inbound_compliance | 0 / 3 / **1** | one standing row | standing | yes |
| | line_ceiling_share | parameter | line_ceiling_share | 0.15 / 0.1 / **0.05** | no | — | yes |
| | inbound_approval_limit | parameter | inbound_limit | 40 / 20 / **10** | no | selling | yes |
| | inbound_limit_uplift | parameter | inbound_uplift | 10 / 5 / **0** | no | — | yes |

- Counts per policy (declared): lost_claim 5 (4 param / 1 method), lost_approval 6 (4/2), shortage_claim 4 (3/1), damage_approval 5 (4/1), shortage_approval 6 (5/1). All within 4–6, all ≥2 parameter. After F2, lost_claim_units has **0 honest method factors**.
- Every ladder has 3 pairwise-disjoint tiers, values pairwise distinct, every tier stated in the rule (condition and value/method) and implemented as a branch of its `decides` binding; fall-through = `baseline` in every factor; bindings disjoint across factors of a policy; no `decides: result`.
- Baselines: each `baseline.rule` is a sentence set of its `rule`, names the default keys listed in `baseline.params`, and alone gives a definite number (verified per task world in the task files).
- Per-task requirements (structure): tree {lost_claim, lost_approval} has multi-source factors (find window, shrinkage method) and cross-difficulty factors (selling, payout, standing); tree {shortage_claim, damage_approval, shortage_approval} has multi-source (netting, damage method) and cross-difficulty (standing, selling).
- Realism notes (observations; contestable, no demonstration of "no such business would publish"):
  - O8: find_matching_window tier 1 and the "not on hold" part of tier 2 condition on the seller's payments-account hold status. Payout holds in this world (`account_suspended`, `bank_details_invalid`, `reverification_overdue`) are not facts an FBN reconciliation desk weighs for the span over which found units net against losses, except under a general risk-scrutiny rationale.
  - O9: find-window tiers longer than the warehouse-loss lookback net found units of losses that are themselves outside the lookback (and already netted on their own adjustment), i.e. asymmetric SKU-level netting; consequence on task 0 recorded there.
  - Other ladders (program/tenure lookbacks and spans, size-tier search holds, standing-based ceilings and shares, desk approval limits by store plan, aging uplifts, receiving tolerances, same-cost/minimal-split netting) are recognisable marketplace reimbursement practice.

### findings

**F1 — SOURCE-POLICY RED (undeclared override / non-unique merged semantics of the warehouse-loss claim window). Bears on task 1 (demonstration there).**
- Symptom: the damage-approval policy approves "the units claimed on the case" with no claim-window condition, while the base window sentence still governs damaged-in-warehouse claims.
- Root cause: base S3 ("A warehouse loss claim is filed no later than the warehouse loss claim window counted in calendar days from the inventory adjustment date.") covers lost **and** damaged adjustments (`parameter_schema.warehouse_loss_claim_window_days`: "Calendar days after a lost or damaged-in-warehouse adjustment within which the seller may claim a reimbursement not issued automatically"; eligibility `warehouse_loss_window` applies_to `fulfill_reimbursement`, clock `frozen_time`). S3 is superseded only in `fulfill_ext_lost_claim_units.overwrite`, whose `replaced_by` speaks only of "the claimable lost units of a warehouse-loss case … lost-in-warehouse inventory adjustments". `fulfill_ext_damaged_case_approval.overwrite` names only S1. So after the replacement it is undetermined whether a damaged-in-warehouse claim still carries the 60-day window (S3 replaced only for lost claims) or none (S3 removed outright); and if it does, the damage approval weakens an inherited eligibility without declaring it.
- Evidence: `fulfill.extended.yaml` fulfill_ext_lost_claim_units.overwrite[0]; fulfill_ext_damaged_case_approval.overwrite[0] and rule sentence "The units approved on a warehouse-damage case are the units claimed on the case, less …"; base `fulfill_reimbursement_terms.eligibility.warehouse_loss_window`.
- Consequence: demonstrated against task 1's world in `1.md` (second reading 12 units vs 23, or refusal).
- Affected: fulfill_ext_damaged_case_approval (overwrite / rule), fulfill_ext_lost_claim_units (overwrite scope).

**F2 — SOURCE-FACTOR RED (mislabelled effect: find_matching_window is a parameter, leaving fulfill_ext_lost_claim_units with no honest method factor). Bears on task 0 (demonstration there).**
- Symptom: `find_matching_window` is labelled `effect: method`, but its three tiers only choose the integer passed as `within_months` to one unchanged aggregate: `found_matched = SUM('fulfill_events','units', within_months=find_window_months, event_type='fulfill_inventory_found', sku=case_sku)` with `find_window_months ∈ {tenure_months + 1, K('find_window_long')=12, lookback_months}`.
- Root cause: a window length is a number substituted into the same formula; the author labels the structurally identical span choices `lookback_base`, `search_hold` (this policy) and `carry_span` (shortage claim) as `parameter`.
- Consequence: counting only honest labels, the lost-claim computation has 0 `method` factors (bound: ≥1).
- Affected: fulfill_ext_lost_claim_units.factors[find_matching_window].effect; the policy's factor set.

**Observations O1–O9** as recorded in the sections above (naming of baseline vs ladder terms; framework baseline-sentence pattern; denied-case filter wider in compute than in rule; correction-time gate without a compute binding; docstring "Afterwards/then"; FIFO edge realism; base auto-reimburse vs seeded un-reimbursed adjustments — O7: in both worlds lost/damaged adjustments older than the 30 auto-reimburse days stand un-reimbursed, which base S2 says happens automatically; the base window sentence contemplates "a reimbursement not issued automatically", so no scored consequence; payout-hold condition realism; asymmetric found netting).

## closing_checklist

Written after both reveals (2026-10-11T05:01Z onward); the charter-global section above is unchanged since its pre-reveal hash c273dbde5bc96105c8be3c21709011727765fe3d56463b70bd05b70d34c7695a.

- Per-task files: `0.md`, `1.md`, one per task, alongside this file; first revision (no older revisions). Each carries a frozen derivation and a `source_gt_comparison`. **Not every comparison carries a PASS** → the difficulty does **not** close.
- Coverage and scope: revealed `charter_scope` — task 0 {fulfill_ext_lost_claim_units, fulfill_ext_lost_case_approval}, task 1 {fulfill_ext_damaged_case_approval, fulfill_ext_shortage_claim_units, fulfill_ext_shortage_case_approval}: pairwise disjoint, jointly cover all five extended policies and all five task tools. Task tools and GT are closed; uuid8s independent (`action_binding_and_uuids`).
- Problem trees: task 0 — 1 prerequisite, 1 value_input, 1 customer write; task 1 — 2 prerequisites, 2 value_input, 1 customer write; difficulty-wide graph acyclic. PASS.
- Factors: every computation has 4–6 factors with ≥2 parameter; every factor bears weight against an honest baseline on its world; every baseline alone gives a definite number ≠ gold (5/10; 8/31/10). Fails: lost_claim_units has 0 honest method factors (F2 → task 0 SOURCE-FACTOR RED); task 1's standing row read by the compliance factors contradicts the standing charter (task 1 SOURCE-FACTOR RED).
- Policy self-consistency: F1 (warehouse-loss claim window superseded only for lost-in-warehouse claims; damage approval inherits it undeclared) → task 1 SOURCE-POLICY RED with a second value 12 vs 23 for the scored damage approval.
- Gates: not re-run by the auditor (the skill assigns gate runs to the coordinator); the difficulty does not reach the final-form re-run because it does not close.

| task | SOURCE-POLICY | SOURCE-CHAIN | SOURCE-FACTOR | SOURCE-TASK |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | **RED** (T0-1 / F2) | PASS |
| 1 | **RED** (T1-1 / F1) | PASS | **RED** (T1-2) | second value on step 8 is the F1 consequence |

## revision_2

### charter_global_frozen (revision 2)

- Written 2026-10-11T06:53Z (system clock), before any round-2 task GT was read; contains nothing derived from a round-2 reveal. Auditor: same independent auditor as round 1.
- Inputs (sha256 recomputed, equal to the round-2 HASHES.txt): `fulfill.extended.yaml` b2a83ff2925786ca17a04a8656eb908b65b66379d4e2d3b3bc79c6a0927f4881 (round 1: ea5a56f1…e028 — **changed**), `task_tools.py` 2bdcb79576126bc8f6f2565522f613c77b312705a88e01a0aac5cb5bc3f35fec (round 1: 87d67070…6adc — **changed**); source `tasks/0.json` 2e36867a…78f6, `tasks/1.json` 4d300ca1…7212; views `0.view.json` 43ae0c11…e01c, `1.view.json` 6a5a810d…799b. Both shared inputs changed, so every charter-global section is re-derived below in full (round-1 text above left untouched).
- Blueprint unchanged since before round 1 (all `blueprint/` files mtime ≤ 02:12Z); base section of the extended charter still parses equal to `blueprint/products/fulfill.yaml`.
- Entry conditions: `gates.r2.txt` carries the commands and actual output lines; EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (0.json 11 acts, 1.json 13 acts), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK, all rc=0. Masked views rebuilt with the same masked key list. Met.
- Masked until both round-2 derivations froze: as in round 1. No recursive search was run.

### policy_conflict_scan (r2)

The five policies, their computes, target tools, owners and the prerequisite graph are unchanged from round 1. Changes found:
- fulfill_ext_lost_claim_units: the find-matching window factor and the payout read are gone (found units now netted over the warehouse-loss lookback). The claim-ceiling share ladder is now `claim_ceiling_method`, which waives the ceiling for Top Rated/Preferred Partner sellers, uses the largest single lost-in-warehouse adjustment ever recorded for Below Standard/Developing sellers, and uses the standard share of received units otherwise. A new `claim_unit_cap` ladder sets 60/30/15 by program and 12-month tenure. `cross_category` is now selling and standing.
- fulfill_ext_damaged_case_approval: a second `overwrite` now supersedes base S3 for warehouse-damage cases ("the warehouse loss claim window is replaced by the damage claim span: only damaged-in-warehouse adjustments dated inside the damage claim span, counted back from the handling date, can be approved…"). New param `damage_claim_span: 2` and bindings `timely_damage_units` / `damage_start_units = MN(damage_claimed, timely_damage_units)`.
- lost/shortage approvals: the denied and approved counts now filter `case_type='reimbursement_claim'`, and the rule says "no denied reimbursement case … approved FBN reimbursement cases". In the shortage approval the term is now "inbound verification holdback" throughout, and the baseline sentence reads "the line ceiling share being the standard line ceiling share".
- task_tools.py: docstring wording only ("On success …", "issued separately by …"); bodies and uuid8s are unchanged.
- No new overlap: case kinds still partition the subjects; cross-category reads match the CFIELD calls (lost claim: selling, standing; lost approval / damage / shortage approval: standing, selling; shortage claim: none).

### rule_compute_equivalence (r2)

- Every `compute_basis` sentence of all five policies is a verbatim sentence of its rule (sentence-split substring test: no misses). Every `overwrite.replaced_by` is verbatim in its rule.
- lost_claim_units: `remainder_units = MX(0, counted_lost - found_matched - reimbursed_in_lookback)` and `result = MN(claim_ceiling, claim_unit_cap, remainder_units)` implement "a negative remainder counts as zero, and that remainder is then capped at the warehouse-loss claim ceiling and at the claim unit cap, whichever is lower". The "waived" ceiling is `claim_ceiling = remainder_units`, which is equivalent. "Largest single lost-in-warehouse inventory adjustment ever recorded for the SKU" is `MAX(...)` with no window. Round-1 O1 (ceiling named "standard … share" against a ladder for "the … share") is **closed**: the ladder sentence now defines "The warehouse-loss claim ceiling" itself.
- lost/shortage approvals: round-1 O3 is **closed**; rule and compute now agree on reimbursement cases. The shortage-approval naming half of O1 is **closed**.
- damaged_case_approval: "the units claimed on the case, limited to the units on the damaged-in-warehouse inventory adjustments of its SKU dated inside the damage claim span" maps to `MN(damage_claimed, timely_damage_units)` with `within_months=K('damage_claim_span')`. The span convention sentence now names "the damage review span or the damage claim span". Equivalent.
- O4 (shortage-claim correction gate has no compute binding) is unchanged; it is answered without change and remains an observation.
- O2 (baseline sentences stated unconditionally before their ladders) is unchanged by design; it remains an observation.

### action_binding_and_uuids (r2)

- Same five `(target_tool, computes)` pairs, each claimed once; the uuid8s are unchanged and independent.
- Tool bodies are byte-for-byte the round-1 bodies (one `ctx.update`; the approve tools set `case_status="approved"`). There is no validation in the tool layer.
- Round-1 O5 is **closed**: "Afterwards" and "then issued" are replaced by "On success" and "issued separately"; no docstring states a position in a sequence or names another tool.

### prerequisite_graph (r2)

Unchanged: three state-form value_input edges (lost approval ← lost claim; shortage approval ← shortage claim; shortage approval ← damage approval), acyclic. Each `policy_source` is verbatim in its blocked rule, each `resolved_by` is the depended-on `target_tool`, and the gates `claimed_units`, `inbound_claimed` and `inbound_approved` exist. PASS.

### prerequisite_sentences (r2)

All three sentences are unchanged and pass the four-point test as in round 1. No depended-on rule restates its blocker's sentence. The new damage-claim-span sentence states no cross-problem order (it limits which adjustments a damage case can approve). Edge 3 is still resolved only by the damage decision, since no deny or withdraw write exists. PASS. O6 (edge 3 is a FIFO convention) is answered without change and remains an observation.

### override_declarations (r2)

Base S3 ("A warehouse loss claim is filed no later than the warehouse loss claim window…") is now superseded by two declarations, one for each kind of warehouse claim:
- fulfill_ext_lost_claim_units, replaced by the lost-in-warehouse claimable-units sentence;
- fulfill_ext_damaged_case_approval, replaced by "For a warehouse-damage case the warehouse loss claim window is replaced by the damage claim span…".

Base S3 covers only warehouse loss claims (lost or damaged), so after both replacements no warehouse claim kind is left under S3. The merged semantics are unique. **Round-1 F1 is closed at the charter level** (the per-world check is in `1.md` revision_2). Every other row of the round-1 table is unchanged.

### factor_ladders (r2)

| policy | factors (label) | parameter / method | multi-source factors | cross_difficulty |
| --- | --- | --- | --- | --- |
| lost_claim_units | lookback_base (p), store_lookback_bonus (p), search_hold (p), **claim_ceiling_method (m)**, **claim_unit_cap (p)** | 4 / 1 | none (each ladder reads one row) | selling (bonus), standing (ceiling method) |
| lost_case_approval | unchanged 6 | 4 / 2 | shrinkage method | standing, selling |
| shortage_claim_units | unchanged 4 | 3 / 1 | netting scope | — |
| damaged_case_approval | unchanged 5 | 4 / 1 | damage method | standing, selling |
| shortage_case_approval | unchanged 6 | 5 / 1 | — (inbound verification tier 2 reads one table) | standing, selling |

- claim_ceiling_method: its three tiers are three different computations (no ceiling / the MAX of one ledger / a floored share of a SUM), so the method label is honest. Values 0.04 share / max-adjustment / none are pairwise distinct, the fall-through is the baseline, and every tier is stated in the rule. **Round-1 F2 is closed**: lost_claim_units now has one honest method factor.
- claim_unit_cap: 60 / 30 / 15, three disjoint tiers, the fall-through is the baseline (`cap_standard`), and all tiers are stated in the rule. Honest parameter.
- Per-task structure: the lost tree has a multi-source factor (shrinkage method: program + standing) and cross-difficulty factors (selling, standing). The shortage tree has multi-source factors (netting scope, damage method) and cross-difficulty factors (standing, selling).
- Realism: round-1 O8 (payout-hold condition) and O9 (asymmetric found netting) are **closed** because the find-window factor was removed. claim_ceiling_method (no ceiling for top-rated sellers; for the lowest-rated, a ceiling at the largest single loss event on record) and claim_unit_cap (per-case unit cap by program and tenure) are plausible desk controls.
- New observation O10 (realism, not a factor): the damage claim span is counted back from the **handling** date ("counted back from the handling date … units of an older damaged-in-warehouse adjustment are not approved on any case"). A timely case therefore loses units if the desk decides it late, which sits against the same policy's limit uplift for long-waiting cases. Whether this bites depends on the world (see `1.md` revision_2). It is not one of the factor ladders.

### findings (r2)

- F1 is closed (two declarations; merged semantics unique).
- F2 is closed (claim_ceiling_method is an honest method; find_matching_window removed).
- O1, O3, O5, O8 and O9 are closed.
- O2, O4 and O6 are answered without change and remain observations.
- O7 is answered without change; its per-world status is in each task file.
- New: O10 (observation).
- No new SOURCE-POLICY or SOURCE-FACTOR finding at charter level.

### closing_checklist (revision 2)

Written after the round-2 reveals (2026-10-11T06:54:34Z onward). The charter-global revision_2 section above was frozen before the reveal and is unchanged.

- Per-task files `0.md` and `1.md` each carry a revision_2 with a frozen derivation and a comparison. Revision 1 text is preserved. Both revision_2 comparisons are **PASS**.
- Coverage and scope: task 0 has {lost_claim_units, lost_case_approval}; task 1 has {damaged_case_approval, shortage_claim_units, shortage_case_approval}. The two are disjoint and cover all five policies and all five tools. uuid8s are independent and unchanged.
- Problem trees:
  - task 0: 1 prerequisite, 1 value_input edge, 1 customer write;
  - task 1: 2 prerequisites, 2 value_input edges, 1 customer write;
  - the difficulty-wide graph is acyclic.
- Factors: every computation has 4–6 factors with at least 2 parameter and at least 1 honest method. Each task has at least one multi-source factor and at least one cross-difficulty factor, and the cross-difficulty rows are seeded and consistent with their charters. Every factor bears weight, and each baseline alone gives a figure different from gold (5 / 10; 8 / 31 / 10).
- Round-1 reds F1 / T1-1, F2 / T0-1 and T1-2 are closed. No regression and no new red.
- Gates on the final form: the coordinator's `gates.r2.txt` was run on the artifacts whose hashes I verified (charter b2a83ff2…, tools 2bdcb795…, tasks 2e36867a… / 4d300ca1…). All 8 instantiation gates have rc=0. check_traceability is deferred until the KB is published.

| task | SOURCE-POLICY | SOURCE-CHAIN | SOURCE-FACTOR | SOURCE-TASK |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

The difficulty passes the source-layer audit at revision 2.

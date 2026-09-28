# Policy-task audit — pharmacy_coverage_and_exceptions / charter-global

## charter_global_frozen

- Freeze time: 2026-09-24T17:19Z (written before any task's GT was revealed; nothing below is derived from a revealed GT field).
- Auditor: erl-task-policy-audit sub-agent (independent of the authoring agent), round 1.
- Frozen inputs (sha256, recomputed by the auditor and equal to the coordinator brief):
  - `tasks/pharmacy_coverage_and_exceptions/rx.extended.yaml` = `e0d7290f0b8ae3c4b0b069029d7830b41c0b068de1776f633c7d21973fef79dc`
  - `tasks/pharmacy_coverage_and_exceptions/task_tools.py` = `e19d9d91b05ad910f1efafc49ba1726bcfa7fb836417f01c0b995599c43bc6a5`
  - masked view 0.json = `b1a5c056…c50a1`, masked view 1.json = `d92223f5…b6b2` (keys kept: frozen_time, user_scenario, initial_state; the brief says task_index was also kept, but the files actually contain only the three keys — harmless).
- Fields read: `blueprint/blueprint.yaml`, `blueprint/products/rx.yaml`, `blueprint/db_schema.json` (rx_otc_ledger / table list), `blueprint/share_tools.py` (lookups, identity, handoff), the whole of `rx.extended.yaml` and `task_tools.py`, the two masked views, and the compute DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` lines 200–415 (semantics of `within_months`, `LATEST`, `MONTHS`, `DAYS`, `XCOUNT`, `CFIELD` only; it carries no task GT).
- Fields masked and not read before the freeze: every task JSON under `tasks/pharmacy_coverage_and_exceptions/tasks/`, its `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`; the difficulty's `worklog.md`; the scenario `worklog.md`; any `__pycache__`; sibling audit directories under `audits/policy_task/`.
- Entry conditions (Step 0): the brief supplies the gate snapshot for check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding and check_cross_fire, all rc=0, and the masked views with hashes. Observation: the check_compute snapshot is truncated — it shows only the `1.json` row and the suite means, and has no `0.json` row. This is recorded as an observation about the snapshot as supplied, not rerun.
- Base copy: `diff <(sed -n 1,1660p rx.extended.yaml) blueprint/products/rx.yaml` → identical. The base section is a verbatim copy.

### policy_conflict_scan

Eight extended policies. Their `prerequisite` graph falls into two connected components, and each component is one problem tree:

- **OTC component**: `rx_ext_otc_catalog_order` (on_request, `owner=user` tool) ← `rx_ext_otc_receipt_posting` ← `rx_ext_otc_quarter_load` ← `rx_ext_otc_quarter_forfeit`. Every edge is a state-form `value_input` edge.
- **Dispensing component**: `rx_ext_lost_stolen_replacement` (on_request, `owner=user` tool) ← {`rx_ext_emergency_supply_days`, `rx_ext_transition_fill_days`, `rx_ext_vacation_supply_release`}. Every edge is a state-form `value_input` edge with gate `offcycle_adjustment`.

Overlapping subjects:
- `rx_otc_purchase` is claimed by both `rx_ext_otc_receipt_posting` (retail receipt posting, computes `allowance_charged`, tool `post_otc_receipt_a5c098d1`) and `rx_ext_otc_catalog_order` (mail-catalog order, computes `allowance_amount`, tool `place_otc_catalog_order_ca6274ae`). The channel (retail_pharmacy vs mail_catalog) and the tool keep them apart, so there is no conflict.
- `rx_fill` is claimed by the transition, vacation and replacement policies. Their fill_types are distinct (`transition_fill`, `vacation_override`, `lost_stolen_override`) and so are their tools. The replacement policy counts the other two, as its declared edges say. There is no conflict.

Cross-category read boundaries: `plan` (a difficulty: member_cost_sharing_and_renewal) is read through CFIELD and XCOUNT on `plan_memberships` and `plan_claims`. `care` (a category with no difficulty in blueprint.yaml) is read through CFIELD. Each read is declared in `cross_category`.

Terminal states: each tool writes one distinct row family. The balance-mutating OTC tools (forfeit −, load +, post −, order −) act on the single `rx_coverages.otc_balance`, and they are totally ordered by the chain, so there are no parallel writers.

Claimed task scopes: the tasks' `charter_scope` is masked. From the graph alone, the two components are disjoint and together cover all 8 policies. The comparison of the claimed scopes with this partition is deferred to the post-reveal sections.

Observation (difficulty claim vs extended subjects): the blueprint's claimed event_types for this difficulty are `rx_exception_request, rx_refill_override, rx_emergency_supply, rx_lock_in_pharmacy_change, rx_lock_in_change_log, rx_otc_purchase, rx_fill_reversal`. The extended subjects include `rx_otc_load`, `rx_otc_forfeit` and `rx_fill`, which are not in that list. `rx_exception_request`, `rx_lock_in_*` and `rx_fill_reversal` are not exercised. The whole `rx` category is claimed by this difficulty only, so no other difficulty collides and none of the four relationships is affected.

### rule_compute_equivalence

Mechanical sweep: every `compute_basis` value is a verbatim substring of its own policy's `rule` (0 misses across the 8 policies). Every `baseline.rule` and every `overwrite.replaced_by` is verbatim in the rule. No snake_case token and no tool or policy id appears in any rule.

Sentence-by-sentence reverse sweep. These are the places where compute and rule are not one-to-one:

1. `rx_ext_otc_catalog_order.posted_quarter_receipts` = `COUNT(..., within_months=3, date_field='posted_date', ..., benefit_quarter=current_quarter)`. The rule says only "where two or more retail receipts tagged to the current quarter carry a posting date". The 3-whole-month posted_date window is **invented by compute**. It changes the count only when a receipt tagged to the current quarter was posted three or more whole months ago, which can happen when "current quarter" is stale. See item 2 and the task 0 file. Observation: no consequence at handling time in either task's world (see `0.json.md`).
2. `rx_ext_otc_catalog_order.current_quarter` = `LATEST(load benefit_quarter)`. The rule uses "the current quarter" (in its prerequisite sentence, in the orders-still-open sentence and in the keep-back sentence) and **never defines it**. Compute defines it as the quarter of the latest load, while the natural reading is the calendar quarter containing today. The two coincide whenever the current calendar quarter has been loaded. Observation, because it bears on the opening-world reading of the task 0 edge. See `0.json.md`.
3. `rx_ext_otc_receipt_posting.register_total` = `SUM(amount of every retail rx_otc_purchase with posted_date='')`. The rule posts "a ... receipt ... once", one receipt. Compute sums every unposted retail receipt of the coverage, across quarters. It diverges only when two or more unposted receipts exist. Observation: task 0 has one.
4. `rx_ext_vacation_supply_release.result` = `int(MN(...))`. The rule states no rounding, but the top-up's "one half of the days on hand" tier produces half-days and compute truncates them. The rounding mode and point are invented. They bite only when days on hand is odd and between 1 and 14. Observation: in task 1, days on hand = 25, the first tier, so there is no half.
5. `rx_ext_vacation_supply_release.override_drug` keys on `drug_name`, while the rule says "The prescription is the one named on the latest vacation override". Observation: there is one prescription per drug in task 1.
6. `rx_ext_otc_catalog_order.carry_over` wraps the carry-over in `MX(0, …)`, a floor the rule does not state. Observation: the forfeit policy's `retained_carryover ≤ unused_allowance` makes the argument non-negative by construction.
7. `rx_ext_lost_stolen_replacement.base_days` third tier `MX(1, supply − elapsed)`: the "never fewer than one day" appears in the rule only for the standard replacement and for the final count, not for the "otherwise the days still on hand" tier. Observation: in task 1 the controlled tier is taken.

Every ladder named in `factors[].ladder` is a sentence of its rule and a branch of its `decides` binding, and every branch is stated in the rule (checked for all 38 factors). No tier lives only in compute.

### action_binding_and_uuids

`(target_tool, computes)` pairs: (forfeit_otc_quarter_0e0fa26e, forfeit_amount), (load_otc_quarter_30ec28e6, load_amount), (post_otc_receipt_a5c098d1, allowance_charged), (place_otc_catalog_order_ca6274ae, allowance_amount), (record_emergency_supply_c348acc4, days_supply), (book_transition_fill_6c1f1c97, days_supply), (release_vacation_supply_4890f9e9, days_supply), (request_replacement_fill_14de4074, days_supply). Each pair is claimed by exactly one policy.

`member_copay`, taken by `release_vacation_supply_4890f9e9` and `request_replacement_fill_14de4074`, is computed by no extended policy. It is governed by base `rx_evt_copay` ("Each paid fill carries the copay the pharmacy plan sets for its formulary_status"), which is in both policies' `base_policy_refs`.

uuid8s: 0e0fa26e, 30ec28e6, a5c098d1, ca6274ae, c348acc4, 6c1f1c97, 4890f9e9, 14de4074. They are pairwise distinct, share no common prefix or tail, and follow no sequence. PASS.

Docstrings: no docstring names another tool, states a position in a sequence, or uses before/after/first as an ordering between actions. Every docstring uses "Afterwards …" to describe the call's own effect, which is not a cross-tool order (observation only). No function body refuses, errors or hints on an unresolved prerequisite. Each body writes its row and adjusts the balance unconditionally. PASS.

Owners: `place_otc_catalog_order_ca6274ae` and `request_replacement_fill_14de4074` are `owner="user"`. The other six are `owner="agent"`.

### prerequisite_graph

- Every policy fills `prerequisite`: four have `[]` (forfeit, emergency, transition, vacation) and four have edges.
- Every `problem` is an extended policy id in this file, never a base id and never the policy itself.
- The graph is acyclic: the two components above are an in-tree of depth 3 and an in-star of width 3.
- Each `policy_source` is verbatim in the blocked policy's own rule (sweep: 6/6 True).
- All six edges are `form: state` and none carries `fallback_reason`, which is consistent.
- `kind: value_input` everywhere, and each `gate` names a real binding of the blocked policy's compute: `closeout_credit`, `posting_balance`, `order_balance`, and `offcycle_adjustment` three times.
- Each `resolved_by` is the depended-on policy's `target_tool`.
- No prerequisite field carries authoring-viewpoint wording ("in this task", "at the opening").

`condition` vs sentence strength: see the finding **CG-P1** below. Edges D (emergency) and E (transition) are weakened from "every" to "the latest".

### prerequisite_sentences

Four-point test, per edge:

| Edge | Sentence (own rule) | Connective | State named (record words) | Names a tool/id? | The one write that brings the state about |
|---|---|---|---|---|---|
| A load ← forfeit | "The quarter load is fixed only after the ledger carries a forfeiture entry for the latest quarter loaded before it." | only after | a forfeiture entry in the allowance ledger for the prior loaded quarter | no | `forfeit_otc_quarter_0e0fa26e` (the only tool that creates `rx_otc_forfeit`; base `rx_terminate` also triggers one, but ending coverage is no task tool) |
| B posting ← load | "A transmitted retail receipt is not posted until the ledger carries the load of the benefit quarter the receipt is tagged to." | not … until | a load entry for the receipt's quarter | no | `load_otc_quarter_30ec28e6` |
| C order ← posting | "The allowance applied to a catalog order is fixed only after every retail receipt transmitted for the current quarter carries a posting date." | only after | every current-quarter retail receipt carries a posting date | no | `post_otc_receipt_a5c098d1` (the catalog tool writes mail_catalog rows, not retail ones) |
| D replacement ← emergency | "The replacement days are fixed only after every counter rejection for prior authorization whose drug has an undecided request carries an emergency supply of that drug." | only after | an emergency-supply claim for the drug | no | `record_emergency_supply_c348acc4` |
| E replacement ← transition | "The replacement days are not fixed until every non-formulary refill rejection of a member inside the transition window carries a transition fill of that drug." | not … until | a transition fill of the drug | no | `book_transition_fill_6c1f1c97` |
| F replacement ← vacation | "The replacement days are fixed only after every vacation override granted in the last thirty days carries a released vacation fill." | only after | a released vacation fill | no | `release_vacation_supply_4890f9e9` |

Derivation, from sentence plus records plus the depended-on rule to the resolving action:
- A: the depended-on rule opens "Once a benefit quarter has closed, its unused over-the-counter allowance is settled by one forfeiture entry tagged to that quarter". That is the only rule that produces a forfeiture entry.
- B: the load rule, "Each calendar quarter's over-the-counter allowance is booked on the coverage as one load entry tagged to that quarter".
- C: the posting rule, "A retail pharmacy register receipt transmitted … and not yet posted is posted once".
- D: the emergency rule, "A drug turned away at the pharmacy counter for prior authorization is owed one emergency supply while the latest prior authorization or exception request for that drug is undecided".
- E: the transition rule, "… whose refill of a non-formulary drug was turned away at the counter is owed one transition fill of that drug".
- F: the vacation rule, "A vacation override granted for a prescription is owed one released vacation fill of that prescription".

Each reading is single. The one wording caveat is "current quarter" in C (rule_compute item 2).

No rule carries a second wording of any dependency, and no depended-on rule restates the blocked sentence. No rule states an undeclared cross-problem order.
- The forfeit rule's "The closed quarter is the benefit quarter of the latest allowance load" implies the forfeit precedes the next load. That is consistent with edge A, not an extra order.
- The catalog rule's carry-over sentence reads the forfeiture, which is transitively ordered by A→B→C.
- No base sentence grounds an edge: base `rx_transition_fill`'s "while an exception is requested" is superseded, and base `rx_emergency_supply_rule`'s "the request is pending" is an eligibility gate.

### override_declarations

Sentence by sentence against each `base_policy_refs` entry:

- **rx_ext_otc_quarter_forfeit vs rx_otc_allowance**:
  - The load-day sentence is not this policy's subject.
  - "spent only on catalog items … never exceeds otc_balance": followed.
  - Mail-order limit: not this policy's subject.
  - Active/restricted: inherited. Task 0's coverage is active.
  - "Unused allowance is forfeited on the last day of the quarter or on the coverage end date, whichever comes first, and never rolls over where otc_rollover is false": **handled differently** (a partial carry-over, forfeited once the quarter has closed). **Declared** in `overwrite`.
  - Observation: base `formula.forfeit_amount: otc_balance` is not a rule sentence and is not named, but it governs the same quantity as the superseded sentence. In a world where the balance holds an earlier carry-over it would diverge even from the extended standard. In task 0 the Q1 forfeiture left no carry-over, so otc_balance equals the closed quarter's unused allowance.
- **rx_ext_otc_quarter_load vs rx_otc_allowance**: "The OTC allowance is loaded on the first day of each calendar quarter" is **declared** superseded, and the amount becomes the allowance plus six credits. Observation: the superseded clause is a timing clause, while `replaced_by` is an amount clause. After the merge no sentence fixes when a load is booked. The extended rule's "Each calendar quarter's … allowance is booked … as one load entry tagged to that quarter" plus edge A decide it uniquely. The other base sentences are followed.
- **rx_ext_otc_receipt_posting vs rx_otc_allowance** (`overwrite: []`): "a purchase never exceeds otc_balance and the member pays the difference at the register" is followed (the charge is limited to the balance). "spent only on catalog items": the extended rule's "remaining tenth being treated as sales tax and non-catalog items" is compatible with it. There is no undeclared conflict.
- **rx_ext_otc_catalog_order vs rx_otc_allowance** (`overwrite: []`): the per-quarter mail/online limit is followed (open orders are counted from `otc_mail_orders_per_quarter`), and "never exceeds otc_balance" is followed. Observation: base is silent on how much of the balance a catalog order applies. The extended policy withholds part of the balance (keep-back, share, shipping fee), which base neither grants nor forbids.
- **rx_ext_emergency_supply_days vs rx_emergency_supply_rule**: "the pharmacy dispenses an emergency supply of emergency_supply_days, at most emergency_supply_per_request per pending request per drug, with no copay" is **declared**. Observation: the declaration also removes "at most emergency_supply_per_request per pending request per drug", and the extended rule's "owed one emergency supply while the latest … request … is undecided" restates it at request granularity, so the merge is still unique. "active or restricted status" is inherited. The Dual Wrap / Part D sentence is inherited and not reached (Children and Maternity plans).
- **rx_ext_transition_fill_days vs rx_transition_fill** and the others: the base sentence "A new member already taking a non-formulary drug receives one transition fill of up to transition_fill_days_supply within transition_fill_window_days …, recorded with fill_type transition_fill, while an exception is requested" is **declared**. Observation: the declaration drops the eligibility condition "while an exception is requested" together with the days quantity. The extended rule's eligibility (effective within the window plus a non-formulary refill turned away) governs uniquely. "A second transition fill for the same drug is never paid" is carried into the extended rule. `rx_evt_copay` "a transition fill carry[ies] no copay" is followed. `rx_monthly_limit`, `rx_dual_wrap` and `rx_opioid_safety` are not reached by the Children plan's non-controlled Intuniv.
- **rx_ext_vacation_supply_release** (`overwrite: []`): base `rx_refill_timing` "a vacation override releases at most vacation_override_max_days" is followed (the result is capped at `P('vacation_override_max_days')`). The per-drug override count is not this policy's subject: the override is already granted. `rx_evt_copay` governs `member_copay`.
- **rx_ext_lost_stolen_replacement** (`overwrite: []`): base `rx_refill_timing` "for a lost or stolen supply up to lost_stolen_override_per_12_months, counted by rx_msr_overrides_365d" is followed ("within the plan's per-drug limit"). "A lost or stolen override for a controlled substance is granted only when the member gives the police report number" is followed. Base says nothing about replacement days, so there is no conflict. `rx_evt_copay` governs `member_copay`.

No undeclared override was found. None of the three disguised forms applies: no anonymous intermediate replaces a base quantity, no 0/1 multiplier zeroes a base-fixed amount (the usage multiplier zeroes the extended carry-over only, never a base quantity), and no base branch is dropped.

### factor_ladders

Per-policy structure. Tier counts are as written, with fall-through included. "MS" means every non-fall-through tier is a conjunction over two or more distinct records.

| Policy | Factor | Label | decides | Tiers | MS | X-diff | Structural verdict |
|---|---|---|---|---|---|---|---|
| forfeit | carryover_share | parameter | carryover_share | 3 | yes (plan_memberships.variant_name ∧ plan_claims count) | plan | ok |
| forfeit | carryover_usage | parameter | usage_multiplier | 3 | no | – | ok |
| forfeit | carryover_ceiling | parameter | carryover_ceiling | 3 | no | – | ok |
| forfeit | carryover_base | method | carryover_base | 3 | yes (remote orders ∧ coverage effective date) | – | ok (selects which quantity the share acts on) |
| load | pregnancy_supply_credit | parameter | pregnancy_credit | 3 | yes | plan | ok |
| load | income_supplement | parameter | income_supplement | 3 | no | plan | ok |
| load | catalog_shipping_credit | parameter | shipping_credit | 3 | no | – | ok |
| load | late_load_credit | method | late_load_credit | 3 | no | – | ok (accrual vs flat vs none) |
| load | care_program_credit | parameter | care_program_credit | 3 | no | – (care has no difficulty) | ok |
| load | closeout_credit | parameter | closeout_credit | 3 | yes (entry exists ∧ amount) — same row family | – | ok; observation: its "carries a forfeiture entry" part holds of every load that has a previous quarter, because edge A requires it. The fall-through is legitimately reached only by a first-ever load. |
| posting | eligible_share | parameter | eligible_share | 3 | yes | plan | ok |
| posting | register_price_adjustment | parameter | price_adjustment | 3 | no | – | ok; observation on realism below |
| posting | large_receipt_rule | method | counted_total | 3 | yes (receipt total ∧ posted-receipt count) | – | ok (split vs cap vs none) |
| posting | care_cofunding | parameter | cofunding_share | 3 | no | – | ok |
| posting | low_income_relief | parameter | relief_share | 3 | no | plan | ok |
| order | order_draw_base | **method** | draw_base | 3 | yes | – | **CG-F2: mislabelled; the fall-through coincides with tier 1 on its own domain** |
| order | order_share | parameter | order_share | 3 | no | – | **CG-F1: tier 1 unreachable under every plan's parameters** |
| order | register_keep_back | parameter | register_keep_back | 3 | no | – | ok |
| order | shipping_fee | parameter | shipping_fee | 3 | yes | plan | ok |
| emergency | request_days | parameter | request_days | 3 | yes (statement flag ∧ request date) | – | ok |
| emergency | repeat_supply_adjustment | parameter | repeat_adjustment | 3 | no | – | ok |
| emergency | urgent_care_addition | parameter | urgent_addition | 3 | yes (plan_claims ∧ drug name) | plan | ok |
| emergency | weekend_roll | **method** | weekend_roll | 3 | no | – | **CG-F3: mislabelled (a constant 2/1/0 added to one formula)** |
| transition | transition_window_days | method | window_days | 3 | no | – | ok (clamp: floor / actual / cap) |
| transition | behavioral_health_continuity | parameter | continuity_days | 3 | no | plan | ok |
| transition | repeat_rejection_days | parameter | rejection_days | 3 | no | – | ok; observation on realism |
| transition | refill_alignment_days | parameter | alignment_days | 3 | no | – | ok |
| transition | established_prescriber_days | parameter | prescriber_days | 3 | no | – | ok; observation on realism |
| vacation | topup_days | **method** | topup_days | 3 | no | – | **CG-F2: mislabelled; the fall-through coincides with tier 1 on its own domain** |
| vacation | maintenance_days | parameter | maintenance_days | 3 | no | – | ok |
| vacation | waiting_days | parameter | waiting_days | 3 | no | – | **CG-F4: unreal condition** |
| vacation | refill_count_days | parameter | refill_count_days | 3 | no | – | observation on realism |
| replacement | replacement_base_days | method | base_days | 3 | no | – | ok (days-to-refill-date vs days-on-hand); observation: tiers 1 and 2 are one formula at 90% vs 75% |
| replacement | offcycle_adjustment | parameter | offcycle_adjustment | 3 | no | – | ok; observation on realism |
| replacement | continuity_days | parameter | continuity_days | 3 | yes (controlled_schedule ∧ plan_claims) | plan | ok |
| replacement | prior_replacement_adjustment | parameter | prior_adjustment | 3 | no | – | ok |
| replacement | stable_therapy_days | parameter | stable_days | 3 | no | – | ok |
| replacement | replacement_weekend_roll | **method** | replacement_roll | 3 | no | – | **CG-F3: mislabelled** |

Declared counts, as written:
- forfeit: 4 factors (3P/1M)
- load: 6 (5P/1M)
- posting: 5 (4P/1M)
- order: 4 (3P/1M)
- emergency: 4 (3P/1M)
- transition: 5 (4P/1M)
- vacation: 4 (3P/1M)
- replacement: 6 (4P/2M)

Every policy's bindings are disjoint across its factors, and every `decides` names an input binding, never `result`. Every factor's fall-through equals its `baseline`. Each `baseline.rule` is a verbatim rule sentence, and its composition equals the substitution of all factor baselines: forfeit → the whole unused allowance; load → the plan allowance; posting → 0.9 × register total, limited to the balance; order → balance − 4.95, floored at 0; emergency → plan days; transition → min(max_days, plan transition days); vacation → plan vacation maximum; replacement → max(1, days on hand).

Surviving counts once CG-F1…F4 are applied:
- order: order_share is effectively a two-tier ladder and order_draw_base is effectively a parameter. That leaves **3 ladders that pass (<4) and 0 genuine method factors**.
- emergency: 4 factors, **0 method**.
- vacation: waiting_days is struck, leaving **3 factors (<4)** with topup reclassified, so **0 method**.
- replacement: 6 factors, 1 genuine method (base_days).
- forfeit, load, posting and transition are within bounds.

Multi-source and cross-difficulty coverage per component:
- OTC component: carryover_share, pregnancy_supply_credit, eligible_share and shipping_fee are multi-source; the plan difficulty is read by 6 factors.
- Dispensing component: request_days, urgent_care_addition and continuity_days are multi-source; the plan difficulty is read by urgent_care_addition, behavioral_health_continuity and continuity_days.

Realism observations (these do not rise to a red because no demonstration beyond judgement is available):
- `offcycle_adjustment` shortens a lost or stolen controlled-substance replacement because of coverage-wide emergency, transition and vacation dispensings, including plan-owed bridge supplies of unrelated non-controlled drugs. A PBM does watch off-cycle fill patterns as a diversion signal, but counting the plan's own emergency and transition obligations for other drugs against the member is doubtful.
- `refill_count_days`: other drugs' refill counts enlarge this drug's vacation release.
- `established_prescriber_days` and `repeat_rejection_days`: prescriber familiarity and the number of counter rejections lengthen a transition fill.
- `register_price_adjustment`: a percentage discount on the allowance charge that grows with the number of earlier posted receipts.
- `eligible_share` vs `low_income_relief`/`care_cofunding` pull the allowance charge in opposite directions, and whether a lower charge is a benefit depends on who pays the remainder, which no sentence fixes.

### findings

**CG-P1 — SOURCE-POLICY RED (prerequisite `condition` weakened against its sentence; edges D and E). Bears on task 1.**
- Symptom: the prerequisite sentence and the declared `condition` quantify differently.
- Evidence: `rx_ext_lost_stolen_replacement.prerequisite[0]`:
  - sentence: "every counter rejection for prior authorization whose drug has an undecided request carries an emergency supply of that drug";
  - condition: "For the latest rx_fill_rejected row with reject_code prior_authorization_required whose drug has an undecided rx_exception_request, an rx_emergency_supply row of that drug is dated on or after the rejection."
- Evidence: `prerequisite[1]`:
  - sentence: "every non-formulary refill rejection of a member inside the transition window carries a transition fill of that drug";
  - condition: "For the latest rx_fill_rejected row with reject_code non_formulary …, an rx_fill row with fill_type transition_fill of that drug exists."
- Demonstration, same constructed situation: two drugs X (PA-rejected on day 1, undecided request, no supply) and Y (PA-rejected on day 2, undecided request, emergency supply on day 2). The condition looks only at the latest rejection (Y), so it holds and the replacement may be fixed. The sentence ("every") does not hold, because X carries no supply, so the replacement is not yet fixed and an X supply must be written first. The two passages reach different conclusions on the same state. Edge E is the same, with two non-formulary drugs.
- Root cause: `condition` narrowed "every" to "the latest".
- Affected: `rx.extended.yaml` → `rx_ext_lost_stolen_replacement.prerequisite[0..1].condition`.
- Per-task consequence: see `1.json.md`. In task 1's world only one drug per edge qualifies, so both readings select the same single write.

**CG-F1 — SOURCE-FACTOR RED (unreal ladder: a tier no customer can reach). Bears on task 0.**
- Symptom: `rx_ext_otc_catalog_order.order_share` ladder tier 1 is "three or more mail catalog or online orders still open in the current quarter" → one half.
- Evidence: `open_orders = P('otc_mail_orders_per_quarter') − (orders already tagged)`. The seven variants set `otc_mail_orders_per_quarter` to Dual Wrap 0, Expansion Adult 1, Adult 1, Children 1, Maternity 2, Complex Care 2 and Long-Term Care 0 (rx.yaml variants). The maximum is 2, so `open_orders ≤ 2` in every world of this scenario.
- Demonstrated consequence: the ladder has two reachable tiers (0.6 at exactly two open, 1 below two). It is below the three-tier floor and does not count as a factor.
- Root cause: the tier threshold is set above every plan's parameter.
- Affected: `rx_ext_otc_catalog_order.factors[order_share]`, its rule sentence "The order share is one half where three or more such orders are still open", and the `order_share` compute binding.

**CG-F2 — SOURCE-FACTOR RED (mislabelled effect and a vacuous fall-through). Bears on tasks 0 and 1.**
- Symptom: `order_draw_base` (catalog order) and `topup_days` (vacation release) are labelled `method`, but their tiers substitute a coefficient into one formula.
- Evidence, draw_base: `balance − 1·carry` (carry > 0, open ≥ 2) / `balance − ½·carry` (carry > 0, open < 2) / `balance` (no carry). The fall-through is reached only when carry = 0, where `balance − k·carry = balance` for every k. So its "method" is tier 1's formula at a zero input, and the ladder is one formula `balance − k·carry` with k ∈ {1, ½}.
- Evidence, topup: `max − 1·on_hand` (on_hand ≥ 15) / `max − ½·on_hand` (1–14) / `max` (on_hand = 0). The same shape with k ∈ {1, ½}.
- Demonstrated consequence: each is a `parameter` factor (the tier selects a rate) with two distinct tiers. The catalog order computation then has **no genuine method factor**, and together with CG-F1 only three passing ladders (register_keep_back, shipping_fee, draw_base as a parameter). The vacation release has **no genuine method factor**.
- Root cause: rate substitution written as three prose "methods".
- Affected: `rx_ext_otc_catalog_order.factors[order_draw_base]`, `rx_ext_vacation_supply_release.factors[topup_days]`.

**CG-F3 — SOURCE-FACTOR RED (mislabelled effect). Bears on task 1.**
- Symptom: `weekend_roll` (emergency supply) and `replacement_weekend_roll` (replacement) are labelled `method`.
- Evidence: `result = counted_days + weekend_roll` with `weekend_roll ∈ {2, 1, 0}` selected by the weekday index. One convention (run the supply to Monday) is applied uniformly, and the tiers are only the constant it adds for Saturday, Sunday or a weekday.
- Demonstrated consequence: these are parameter factors. The emergency-supply computation then has **0 method factors** (request_days, repeat_supply_adjustment and urgent_care_addition are parameters). The replacement keeps `replacement_base_days` as its one method, so its count holds, but the mislabel stands.
- Root cause: a date roll written as a method ladder.
- Affected: `rx_ext_emergency_supply_days.factors[weekend_roll]`, `rx_ext_lost_stolen_replacement.factors[replacement_weekend_roll]`.

**CG-F4 — SOURCE-FACTOR RED (unreal ladder condition). Bears on task 1.**
- Symptom: `rx_ext_vacation_supply_release.waiting_days`: "The waiting days are two where the override was granted two or more calendar days before today, one where it was granted the day before, and nothing where it was granted today."
- Evidence: the same rule already measures supply from the latest paid refill as of today ("that refill's days supply less the calendar days since it was filled"). So the days that passed since the grant are already consumed in `days_on_hand`, and adding them again credits the same elapsed days twice. No pharmacy benefit sizes a vacation early-refill release by how long ago the override was keyed.
- Demonstrated consequence: the condition is one that no business in the line weighs for this quantity. The factor is struck, leaving the vacation release with three factors (<4).
- Root cause: an invented condition.
- Affected: `rx_ext_vacation_supply_release.factors[waiting_days]` and its rule sentence.

Observations, charter-level, not grounds for rework on their own: rule_compute items 1–7; the override-declaration observations above; the realism observations above; the truncated check_compute snapshot; the docstrings' "Afterwards"; and the realism of the OTC loads and forfeitures. The last point: a quarterly load and forfeiture are batch events in real plans, but here they are synchronous agent tools with `trigger: state_due`, so no waiting is involved.

## closing_checklist

Written after both reveals, at 2026-09-24T17:28Z. Nothing above this heading was edited after a reveal.

**Status: the difficulty does NOT close.** Not every task passes all four relationships.

- Audit files: there is one per task (`0.json.md`, `1.json.md`), with `_difficulty.md` alongside. This is round 1, so there are no earlier revisions. Each comparison section is present. Neither task carries four PASSes.
- Scope:
  - `charter_scope` (revealed) for 0.json is forfeit, load, posting and order. For 1.json it is emergency, transition, vacation and replacement. The two are pairwise disjoint and together cover all 8 extended policies. Each scope spans its whole tree.
  - Tools and GT are closed: each task calls exactly its four tools.
  - The uuid8s are independent (§ action_binding_and_uuids).
- Trees:
  - Task 0 is a chain of 3 prerequisites with 3 value_input edges. Task 1 is a star of 3 prerequisites with 3 value_input edges.
  - Each has one `owner=user` root.
  - Neither has a cycle. The whole graph is two disjoint acyclic components, and no task references the other.
- Factors:
  - Every declared factor bears weight on its task's world against an honest baseline.
  - Each computation's all-baseline number is definite and differs from gold. The pairs (all-baseline vs gold) are:
    - forfeit 9.46 vs 3.46
    - load 50.00 vs 75.75
    - posting 79.74 vs 60.92
    - order 15.88 vs 5.90
    - emergency 3 vs 13
    - transition 30 vs 26
    - vacation 34 vs 20
    - replacement 14 vs 13
  - The ladder tests fail for:
    - the catalog order (CG-F1, CG-F2): 3 surviving factors, 0 method;
    - the emergency supply (CG-F3): 0 method;
    - the vacation release (CG-F2, CG-F4): 3 surviving, 0 method;
    - the replacement: roll mislabelled (CG-F3), bounds still met.
- Policy: CG-P1 (edge D/E `condition` is weaker than its sentence) is SOURCE-POLICY RED. It has no consequence on task 1's world.
- Gates: this auditor did not re-run the instantiation-stage gates. Per Step 0 the auditor only cites the coordinator's snapshot, and the re-run is due on the final form after rework. The snapshot supplied had a truncated check_compute section (no 0.json row).

Per-task summary:
- **0.json**: policy PASS · tree PASS · factors **SOURCE-FACTOR RED** (catalog order: CG-F1, CG-F2) · unique solution PASS. The independent derivation equals GT on all four writes (3.46 / 75.75 / 60.92 / 5.90).
- **1.json**: policy **SOURCE-POLICY RED** (CG-P1, charter-global, no world consequence) · tree PASS · factors **SOURCE-FACTOR RED** (emergency CG-F3; vacation CG-F2 and CG-F4; replacement roll CG-F3) · unique solution PASS. The independent derivation equals GT on all four writes (13 / 26 / 20 / 13).

---

## revision_2

### charter_global_frozen (revision 2)

- Freeze time: 2026-09-24T18:10Z. Auditor: the same erl-task-policy-audit sub-agent as round 1. This section was written before either round-2 task's GT was revealed.
- Inputs (sha256 recomputed and equal to the round-2 brief):
  - `rx.extended.yaml` = `3c1dff4be57cb787055fbe9dc83f8ac4def998b7294fb97ad07c45fdf73d67e0`. It changed from round 1's `e0d7290f…`, so every charter-global section is re-derived in full below.
  - `task_tools.py` = `e19d9d91…c6a5`, unchanged.
  - Masked views `round2/0.json` = `81e1838b…5a2f` and `round2/1.json` = `548f5bd0…b5b7`. Keys: frozen_time, user_scenario, initial_state.
- Base copy: `diff <(sed -n 1,1660p rx.extended.yaml) blueprint/products/rx.yaml` is still identical.
- Gate snapshot: the round-2 brief carries all 7 gates with rc=0. The check_compute section is now complete, with rows for both 0.json and 1.json, so the round-1 truncation observation is closed.
- **contamination_disclosure**: this auditor revealed the round-1 GT of both tasks during round 1, after that round's freeze. So it knows the round-1 gold values, argument formats and gold ids, and the round-2 worlds are the round-1 worlds plus a few seed rows (task 0: one Q2 retail receipt and a new balance; task 1: a fluticasone refill, a vacation override and a vacation fill). It has not seen any round-2 GT field before this freeze. Every round-2 scored value is recomputed from the round-2 rule text and the round-2 world. Where a round-2 value equals a round-1 GT value, the equality is re-derived rather than assumed. This is disclosed as a limit on blindness, not concealed. The round-2 derivations are not voided on this ground, because no round-2 scored value or GT field was contacted.

### re-derived charter checks (revision 2)

**Mechanical sweep**, over all 8 policies:
- Every `compute_basis` value is verbatim in its own rule, and every compute binding has a basis.
- Every `baseline.rule`, every `replaced_by` and every prerequisite `policy_source` is verbatim in its own rule.
- No snake_case token appears in any rule.
- Every factor's fall-through equals its `baseline`.

**policy_conflict_scan**: the two components are unchanged. The OTC chain is forfeit → load → posting → catalog order (user). The dispensing star is emergency, transition, vacation → replacement (user). There are still six state-form `value_input` edges, the graph is acyclic, and no new overlapping subject exists.

New ordering sentences:
- Posting rule: "where several transmitted receipts await posting, the one with the largest register total is posted first". This is an order within one problem (successive posting writes), so it is not a cross-problem order and grounds no edge.
- Catalog rule: "The catalog order allowance is worked out in this order…". This is arithmetic order, not a cross-problem order.

**override_declarations**: unchanged in substance. The declared overrides are forfeit, load, emergency (the superseded sentence is the same; `replaced_by` now names "the day-count convention") and transition. Posting, order, vacation and replacement carry `overwrite: []`. The vacation release still follows base `rx_refill_timing` "a vacation override releases at most vacation_override_max_days": the result is capped at that parameter and floored at 1. No undeclared override was found. The round-1 observations stand, since the reworker left them unchanged: forfeit formula `otc_balance`, the timing clause replaced by an amount clause, the dropped "while an exception is requested", and the claimed event list vs the extended subjects.

**rule_compute_equivalence**, the round-1 items re-checked:
1. Keep-back 3-month window: **closed**. `posted_quarter_receipts` now counts retail rows tagged to the current quarter minus those with an empty posted_date, with no window. The new rolling windows (two whole months, one whole month) are stated in the rule ("the retail receipts posted in the last two whole months are counted"), and `within_months=2/1` implements them.
2. "Current quarter" undefined: **closed in the rule.** The rule now says "The current quarter is the calendar quarter that contains today."
   - Residual observation: compute still implements it as `LATEST('rx_otc_ledger', 'benefit_quarter', date_field='benefit_quarter')`, the highest quarter tag on any ledger row. That coincides with the calendar quarter only when some row is tagged to today's quarter and none to a later quarter.
   - On the task 0 world it coincides: the transmitted receipt is tagged 2026-Q3 at the opening, and so is the gold load (see `0.json.md` revision_2).
3. Unposted receipts summed: **closed.** The rule now says "where several transmitted receipts await posting, the one with the largest register total is posted first", and compute takes `MAX` of the unposted retail amounts.
4. Vacation rounding: **closed.** "fractions dropped" is stated for the on-hand measure.
5. Vacation drug vs prescription: **closed.** "The drug is the one named on the latest vacation override granted on the coverage".
6. Carry-over floor: **closed.** "never below zero".
7. Replacement third tier floor: **closed.** "otherwise the days still on hand, never fewer than one day".
- Transition wording: **closed.** "the transition fill answers that latest rejection".

**action_binding_and_uuids**: `task_tools.py` is unchanged (same hash). The 8 `(target_tool, computes)` pairs are still one per policy, and the uuid8s are unchanged and independent. The "Afterwards" docstring wording is still observation-only. The tool bodies still judge no prerequisite.

**prerequisite_graph / prerequisite_sentences**: the six sentences are verbatim-unchanged and pass the four-point test as in round 1. Conditions:
- **CG-P1 closed.** Edge D's condition is now "For every rx_fill_rejected row with reject_code prior_authorization_required whose drug has an undecided rx_exception_request, an rx_emergency_supply row of that drug is dated on or after that rejection". Edge E's is now "For every rx_fill_rejected row with reject_code non_formulary and fill_type refill on a coverage whose effective date is within the transition window, an rx_fill row with fill_type transition_fill of that rejection's drug exists". Both match their sentences' "every", and E's "fill_type refill" matches the sentence's "non-formulary refill rejection".
- Edge C's condition now names "the calendar quarter containing today", which matches the new rule definition.
- The edge C `effect` now cites the keep-back count and the withheld carry-over condition, and both are real bindings of the order's compute.

### factor_ladders (revision 2)

Changed policies only. Forfeit, load, posting and transition factors are unchanged from round 1 and are carried forward by reference to round-1 § factor_ladders; their rules and computes are identical text.

| Policy | Factor | Label | Tiers (fall-through last) | Structural verdict |
|---|---|---|---|---|
| order | withheld_carryover | parameter | whole carry-over / one half / nothing | ok. **CG-F2 (order) closed**: relabelled `parameter`. The fall-through is now "no retail receipt of the current quarter carries a posting date", which is reachable with a positive carry-over, so it is no longer vacuous. The three values are distinct. Multi-source: posted receipt ∧ open orders. |
| order | order_share | parameter | 0.6 (≥2 open ∧ forfeited-quarter usage ≥ ¾) / 0.8 (≥2 open ∧ usage < ¾) / 1 (<2 open) | ok. **CG-F1 closed**: every tier is reachable under Maternity and Complex Care (2 orders per quarter), and the fall-through is reachable under every plan. Multi-source. |
| order | keep_back_count_window | method | receipts posted in the last two whole months (plan allows ≥2 ∧ forfeited quarter has a remote order) / posted in the last whole month (plan allows ≥2 ∧ none) / current-quarter receipts carrying a posting date | ok as a method: the fall-through changes the counting basis from a rolling posted-date window to a calendar-quarter tag. Observation: tiers 1 and 2 are one rolling-window rule with window length 2 vs 1. This is the same shape round 1 accepted for `replacement_base_days`. |
| order | shipping_fee | parameter | unchanged | ok |
| emergency | day_count_convention (replaces weekend_roll) | method | business days with weekend pairs added (member started the request) / calendar days rolled to Monday (pharmacy started it) / calendar days as counted (prescriber started it) | ok. **CG-F3 (emergency) closed**: business-day counting vs calendar-day counting are genuinely different algorithms. Observation (realism): who started the request selects the counting convention. No demonstration beyond judgement is available, so it stays an observation, consistent with round-1 treatment. |
| vacation | on_hand_measure (replaces topup_days) | method | days to the controlled refill date / days to the ordinary refill date (non-controlled, refill ≥28 days) / raw days on hand; each floored at 0 | ok. **CG-F2 (vacation) closed**: the fall-through (raw supply less elapsed) is a different measure from the refill-date tiers and is not vacuous. Observation: tiers 1 and 2 differ by the refill percent, the same accepted shape as `replacement_base_days`. |
| vacation | maintenance_days / refill_count_days | parameter | unchanged | ok; the refill_count_days realism observation stands (left unchanged by the reworker) |
| vacation | override_history_adjustment (new) | parameter | −5 (≥3 vacation overrides of any drug in 12 months, the current one included) / −3 (exactly 2) / 0 (only the current one) | ok. Three distinct values, and the fall-through is reachable. A per-drug base measure (`rx_msr_overrides_365d`) exists, so counting "any drug" is a genuine rule-reading distinction. |
| vacation | waiting_days | — | removed | **CG-F4 closed** |
| replacement | replacement_weekend_roll | parameter (was method) | +2 / +1 / 0 | **CG-F3 (replacement) closed** by relabel. The replacement keeps `replacement_base_days` as its one method. |

Declared counts:
- forfeit: 4 (3P/1M)
- load: 6 (5P/1M)
- posting: 5 (4P/1M)
- order: 4 (3P/1M)
- emergency: 4 (3P/1M)
- transition: 5 (4P/1M)
- vacation: 4 (3P/1M)
- replacement: 6 (5P/1M)

All eight are within 4–6 factors with ≥2 parameter and ≥1 method factors, and every ladder has three distinct reachable tiers.

Baseline composition: substituting every factor's baseline reproduces each `baseline.rule`.
- Order: "whole allowance balance less the register keep-back and less the standard shipping fee … where the standard register keep-back is five dollars for each retail receipt tagged to the current quarter that carries a posting date, at most ten dollars". This equals withheld 0, share 1, the calendar-quarter count, and $4.95.
- Emergency: "the plan's emergency supply days, counted in calendar days from today". This equals request_days P, the adjustments 0, and dispensed as counted.
- Vacation: "most extra days supply … less the days still on hand …, never below zero". This equals the raw on-hand measure with the other factors 0.
  - Observation: compute additionally floors the final figure at 1 day, from the extended rule's own "never fewer than one day". The baseline sentence says "never below zero". These differ only when the days on hand reach the maximum.

Multi-source and cross-difficulty coverage per component is unchanged or improved. The OTC component adds order_share and withheld_carryover as multi-source. The dispensing component keeps request_days, urgent_care_addition and continuity_days, and its plan reads are unchanged.

### findings (revision 2)

- Round-1 REDs: **CG-P1 closed**, **CG-F1 closed**, **CG-F2 closed** (both the order and the vacation release), **CG-F3 closed** (both the emergency supply and the replacement), **CG-F4 closed**. The evidence for each is in the sections above.
- New charter-level defects: none that reaches a red.
- New observations:
  - The catalog order's `current_quarter` compute is a highest-tag proxy for "the calendar quarter that contains today" (residual of item 2).
  - Realism: the emergency supply's requester-selected day-count convention.
  - Realism: the keep-back count window's conditions (whether the plan allows two remote orders, and whether the last forfeited quarter had a remote order) select the counting window.
  - Keep-back tiers 1 and 2 differ only in window length.
  - The vacation baseline says "never below zero" while compute floors the result at 1.
- Carried observations, left unchanged by the reworker as claimed: the realism concerns (off-cycle adjustment, refill_count_days, established_prescriber_days, repeat_rejection_days, register_price_adjustment, eligible_share against relief and co-funding), the override-declaration notes, the claimed event list, and the "Afterwards" docstrings.

### closing_checklist (revision 2)

Written after both round-2 reveals, at 2026-09-24T18:14Z.

**Status: the difficulty does NOT close.** Task 0 carries a new SOURCE-TASK RED.

- Round-1 REDs are closed and verified against the round-2 GT: CG-P1, CG-F1, CG-F2, CG-F3 and CG-F4. The rule_compute items 1–7 are closed, with one observation left on item 2's compute proxy. The rationale wording and the gate-snapshot truncation are closed. Nothing regressed.
- **New defect, R2-T1 (task 0, SOURCE-TASK RED).** The receipt-posting price adjustment tier depends on whether RCPT-0219-11842, posted 2026-02-19, falls "in the last six months" at 2026-08-19. No rule fixes whether the window includes its anniversary date.
  - The seed row RCPT-0628-19027, added in the rework, moved the count to the tier boundary: 2 receipts give 2% and 3 give 5%.
  - That yields W3 60.92 vs 59.06 and W4 2.90 vs 4.01. GT's own trace relies on "six whole months", which the posting rule does not state.
  - Details are in `0.json.md` § revision_2 findings.
- Scopes are disjoint and complete (the charter_scope is re-confirmed as the same two 4-policy sets). The trees are chains or stars of 3 prerequisites, each with ≥2 value_input edges and a user-owned root, and the graph is acyclic. Every factor bears weight against an honest baseline, and every all-baseline figure differs from gold. The factor counts are within bounds for all 8 policies.
- Gates: the coordinator's round-2 snapshot is fully green. This auditor did not re-run the gates.

Per-task (revision 2):
- **0.json**: policy PASS · tree PASS · factors PASS · unique solution **SOURCE-TASK RED (R2-T1)**
- **1.json**: PASS on all four relationships.

---

## revision_3

### charter_global_frozen (revision 3)

- Freeze time: 2026-09-24T18:17Z. Auditor: the same sub-agent. This section was written before either task's round-3 GT was revealed.
- Inputs (sha256 recomputed and equal to the round-3 brief):
  - `rx.extended.yaml` = `23c36c70a4f41d3bdc68024e4876783051978a1f105891a796005212a361a09c`, changed from round 2's `3c1dff4b…`.
  - `task_tools.py` = `e19d9d91…c6a5`, unchanged.
  - `round3/0.json` = `60053a55…f51f`, changed.
  - `round3/1.json` = `548f5bd0…b5b7`, byte-identical to round 2 (`cmp`).
- Base copy: still verbatim-identical to `blueprint/products/rx.yaml`.
- Gate snapshot in the round-3 brief: all 7 gates rc=0, with full rows for both tasks.
- contamination_disclosure: this auditor has seen the round-1 and round-2 GT of both tasks, each after its round's freeze. No round-3 GT field was contacted before this freeze. The same limit on blindness as revision 2 applies.

### what changed (revision 3)

I produced a structured dump of every policy's compute, factors, ladders, baselines and cross-category reads and diffed it against the round-2 dump. The compute bindings of all 8 policies are **unchanged**. The only text changes are these:

1. `rx_ext_otc_receipt_posting` rule: a definition sentence is added, "A date falls in the last six whole months when fewer than six whole calendar months have passed from that date to today, a month counting as whole only once today's day of the month has reached that date's day of the month."
   - The three six-month phrases in this rule now read "in the last six whole months": eligible share, price adjustment and large receipt. The factor ladders are updated to match.
   - The definition is the `compute_basis` of `posted_retail_receipts`. It is exactly the DSL's `within_months=6` with `MONTHS` semantics (MONTHS(d, today) < 6, with the month decremented while today's day is below d's day).
2. `rx_ext_otc_receipt_posting` factor ladder texts: "last six months" becomes "last six whole months".
3. `rx_ext_vacation_supply_release` rule and baseline: the baseline now ends "…never below zero, and the release is never fewer than one day". It now matches compute's `MX(1, …)` floor, so the **revision-2 observation is closed**.

Mechanical sweep, re-run over all 8 policies:
- Every `compute_basis` value is verbatim in its rule, every baseline and edge sentence is verbatim, and there are no snake_case tokens.
- Factor counts, labels, tiers and fall-throughs equal revision 2. The revision-2 `factor_ladders` table is therefore carried forward by reference, grounded on the unchanged compute and factor structure (diff above).
- The prerequisite graph, sentences and conditions are unchanged from revision 2, so CG-P1 stays closed. The override declarations are unchanged.

Round-1 REDs, checked for regression: CG-P1, CG-F1, CG-F2, CG-F3 and CG-F4 remain closed. The relevant compute, factors and conditions are byte-unchanged in the dump diff.

### findings (revision 3)

- R2-T1 at charter level: **closed**. The posting rule now fixes the six-month boundary as an exclusive whole-month count. The task 0 seed also moved; see `0.json.md` § revision_3.
- New observation: the whole-months definition lives only in the posting rule. Other rules still say "in the last six months" / "in the six months before …", "last two / three months", "last month" and "last twelve months" with no stated boundary convention:
  - forfeit, load and order preventive-claim counts;
  - transition and replacement behavioural-health counts;
  - emergency supply ER claims and repeat supplies;
  - replacement off-cycle and prior-override counts;
  - vacation refill and override counts.
  The same anniversary-date ambiguity would re-open in any world with a record on such a boundary. Neither round-3 world has one (see each task file), so this is an observation, not a red.
- Carried observations, unchanged as the reworker claimed:
  - the current-quarter compute proxy;
  - realism of the day-count convention and the keep-back window conditions;
  - the keep-back first-two-tier shape;
  - the realism notes carried from rounds 1 and 2;
  - the override-declaration notes;
  - the claimed event list;
  - the "Afterwards" docstrings.

### closing_checklist (revision 3)

Written after both round-3 reveals, at 2026-09-24T18:18Z.

**Status: the difficulty closes at the source layer.** Both tasks pass all four relationships in revision 3.

- Audit files: one per task, with `_difficulty.md` alongside. Revisions 1, 2 and 3 are all preserved, and each has its own frozen section and comparison.
- Every red is closed:
  - round-1 reds CG-P1, CG-F1, CG-F2, CG-F3 and CG-F4 are closed and have not regressed;
  - round-2 red R2-T1 is closed (a rule definition plus the seed row moved off the anniversary);
  - the revision-2 vacation-baseline observation is closed.
- Coverage and scope:
  - all 8 extended policies are covered;
  - the task scopes are pairwise disjoint (task 0 is the OTC chain, task 1 the dispensing star), and each scope spans its whole tree;
  - the tools and GT are closed;
  - the 8 uuid8s are independent and unchanged.
- Trees:
  - each task has 3 prerequisite problems, all edges value_input, and one `owner=user` root;
  - the whole graph is acyclic and no task references the other.
- Factors:
  - every computation has 4–6 factors with ≥2 parameter and ≥1 method factors;
  - each task has multi-source and cross-difficulty (plan) factors;
  - every ladder has three distinct, reachable tiers stated in its rule;
  - every factor bears weight against an honest baseline;
  - every all-baseline figure is definite and differs from gold: 6.22 / 50.00 / 79.74 / 10.88 and 3 / 30 / 9 / 14.
- Gates: the coordinator's round-3 snapshot shows all 7 gates green on the final form. The auditor cites it and did not re-run the gates.
- Open observations (not grounds for rework):
  - month windows outside the posting rule have no stated anniversary convention, though no record in either world sits on a boundary;
  - the current-quarter compute proxy;
  - realism notes: the day-count convention, the keep-back window conditions, off-cycle, refill_count_days, prescriber and rejection days, register price adjustment, and the direction of eligible share against relief;
  - the keep-back first-two-tier shape;
  - the override-declaration notes and the claimed event list;
  - the "Afterwards" docstrings;
  - task 1's two confirmation reads.

Per-task (revision 3):
- **0.json**: PASS
- **1.json**: PASS

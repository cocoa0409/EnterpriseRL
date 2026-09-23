# Policy-task audit — member_equity_desk / charter-global

## charter_global_frozen

- freeze time: 2026-09-18 (audit session), written **before** any task's GT fields were read.
- auditor: independent policy-task auditor (did not author these artifacts).
- frozen inputs and their hashes (sha256[:16]):
  - `env/env_0003_farm_supply_and_grain_cooperative/tasks/member_equity_desk/patronage.extended.yaml` = `1d9268dcd1e6b384`
  - `env/env_0003_farm_supply_and_grain_cooperative/tasks/member_equity_desk/task_tools.py` = `3f5661ad2dbded2d`
- fields permitted for this section: the blueprint (`blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/patronage.yaml`), the extended charter in full, the tool module in full.
- fields explicitly masked and not read while writing this section: every task file's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`. The per-task work used only the orchestrator's masked views
  (`0.json` masked_view sha256[:16]=`155b5b050c81ac6c`, `1.json` = `b96ad164de581f4f`; kept keys = frozen_time, user_scenario, initial_state).
- entry conditions (Step 0): the brief supplied the instantiation-stage gate snapshot with its actual output lines
  (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire — all green, run 2026-09-18T08:55), the masked views and their hashes. check_traceability is declared not run (KB not yet published). Entry conditions are **complete**; the gates were not re-run by the auditor at this stage and are cited, not relied on as proof of correctness.

### policy_conflict_scan

Scope of the scan: the 11 base policies copied into `patronage.extended.yaml` (lines 691–1030) plus the 6 extended policies (lines 1032–2330).

1. **Base copy is verbatim.** `diff <(head -1030 tasks/member_equity_desk/patronage.extended.yaml) <(head -1030 blueprint/products/patronage.yaml)` returns only the trailing blank line. The base section has not been rewritten.
2. **Subjects/target tools are disjoint.** The six extended policies bind one event subject and one tool each:
   `patronage_ext_year_end_unit_accrual` → `patronage_units_accrued` / `book_qualifying_units_5a905387`;
   `patronage_ext_allocation_restatement` → `patronage_allocation_adjusted` / `restate_allocation_notice_7a44a997`;
   `patronage_ext_capital_retain` → `patronage_retain_withheld` / `record_capital_retain_31b65d0b`;
   `patronage_ext_membership_transfer_valuation` → `patronage_membership_transferred` / `transfer_membership_equity_359bd53a`;
   `patronage_ext_cycle_revolvement` → `patronage_equity_revolved` / `record_equity_revolvement_d16ad296`;
   `patronage_ext_estate_retirement` → `patronage_membership_retired` / `retire_estate_equity_f4a8a7dc`.
   No two policies compute the same quantity on the same subject.
3. **Time anchors.** All six evaluate on `NOW` = the task's `frozen_time`; windows are stated in months/days and implemented with `within_months` / `MONTHS` / `DAYS`. No policy anchors on a future date; no policy requires an event that has not happened at the opening.
4. **Cross-category read boundaries.** Declared `cross_category` blocks name grain / agronomy / energy / feed and match the `EXISTS/CFIELD/XSUM` calls in each `compute`; no policy reads a category it does not declare.
5. **Claimed scopes of the M tasks** (derived from the policy surface and the two masked worlds, not from `charter_scope`): task 0's tree is {transfer valuation, capital retain, allocation restatement, year-end unit accrual}; task 1's tree is {estate retirement, cycle revolvement}. The two sets are **pairwise disjoint** and **jointly cover all six** extended policies.
6. **Conflicts found:** two base/extended conflicts on a scored quantity, neither declared in `overwrite` — see `### override_declarations` findings F-1 and F-2. They bear on task 0 only.

### rule_compute_equivalence

Check 2 run over all six extended policies. Every `compute` binding carries a `compute_basis` quotation, and every quotation is a verbatim sentence or clause of that policy's own `rule` (checked line by line). The sweep back (rule → compute) found each stated tier implemented as a branch of the named binding. Residual defects:

- **E-1 (observation).** Three ladders carry a conjunct in `compute` that no sentence of the `rule` states: the guard `notice_volume > 0` / `notice_units > 0` on the first tier of
  `patronage_ext_year_end_unit_accrual.compute.already_accrued`
  (`"accrual_volume if (accrual_volume > notice_volume and notice_volume > 0) else ..."`) and of
  `patronage_ext_allocation_restatement.compute.restated_grain_units`
  (`"accrual_sum if (accrual_sum > notice_units and notice_units > 0) else ..."`).
  The rule states only *"Where the accrual rows recorded for the year on the grain basis carry more volume than the notice was posted on…"*. On a world where no notice stands for the year (notice = 0) and accrual rows do stand, the rule selects tier 1 and the compute selects tier 3 — two different volumes. Neither task's world has notice = 0 (task 0: 38 500 bu on PN-441225; task 1: 58 900 bu on PN-446825), so **no consequence is demonstrable here** and this is recorded as an observation, not a red.
- **E-2 (observation).** `patronage_ext_capital_retain.compute.retain_rate` carries the conjunct `membership_years > 0`, which no sentence of the rule states (*"where retain rows stand on the equity ledger from an earlier fiscal year and the rate on the latest of them stands above nothing, the rate taken is that rate"*). The conjunct is true of every membership with a joining date in the past, so it changes no value and no consequence can be demonstrated.
- **E-3 (observation).** Two ladders count **rows** where the rule counts **years**:
  `patronage_ext_capital_retain.compute.allocated_years = COUNT('patronage_ledger', event_type='patronage_allocation_posted')` against the rule's *"allocation notices stand on the equity ledger for twelve or more years"*, and
  `patronage_ext_membership_transfer_valuation.compute.certificate_rows = COUNT('patronage_ledger', event_type='patronage_retain_withheld')` against *"capital retain lines stand on the equity ledger for ten or more years"*.
  A year that carries three notice lines (as fiscal 2025 does on both memberships) counts three times. On both worlds the two readings select the same tier, so no consequence is demonstrable.
- **E-4 (observation).** `patronage_ext_capital_retain`'s prose ladder for `retain_volume` is **not pairwise disjoint as stated**: tier 1 is *"Where the accrual rows recorded for the year on the grain basis carry more volume than the notice was posted on"* and tier 2 is *"where no allocation notice stands posted for the year most recently allocated but accrual rows stand for it on the grain basis"* — both are true when no notice stands and accrual rows do. Only the compute's unstated `notice_units > 0` guard resolves the overlap (see E-1). Not live on either task's world.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (table in `policy_conflict_scan` item 2). No tool is the target of two policies; no policy names two tools.
- Tool docstrings state no sequence: `grep -Ei '\b(before|after|first|prior to|then|next|once)\b' task_tools.py` returns three hits, all non-ordering — *"the next equity statement"*, *"before any split between cash and equity"* (a description of the amount), *"From then on the account is closed"*. No docstring names another tool, a policy id, or a position in a sequence.
- uuid8s: `5a905387`, `7a44a997`, `31b65d0b`, `359bd53a`, `d16ad296`, `f4a8a7dc`. Six distinct values, no shared prefix, no sequence, no adjacent values, no common tail; each is frozen with its function name and is used consistently in the policies' `target_tool` and `prerequisite.resolved_by`.
- No tool body adds a confirmation, a review, a wait, or any procedure outside the policy: each is a single `ctx.create` or `ctx.update` pair plus a confirmation sentence.

### prerequisite_graph

Check 7 over the whole graph. Five edges are declared; every policy has the field filled in (`prerequisite: []` on `patronage_ext_year_end_unit_accrual` and `patronage_ext_cycle_revolvement`).

| blocked policy | problem | kind | gate | form | resolved_by | acyclic |
| --- | --- | --- | --- | --- | --- | --- |
| `patronage_ext_allocation_restatement` | `patronage_ext_year_end_unit_accrual` | value_input | `accrual_sum` | state | `book_qualifying_units_5a905387` | ✓ |
| `patronage_ext_capital_retain` | `patronage_ext_year_end_unit_accrual` | value_input | `accrued_grain` | state | `book_qualifying_units_5a905387` | ✓ |
| `patronage_ext_membership_transfer_valuation` | `patronage_ext_capital_retain` | value_input | `retain_credits` | state | `record_capital_retain_31b65d0b` | ✓ |
| `patronage_ext_membership_transfer_valuation` | `patronage_ext_allocation_restatement` | value_input | `restated_allocation` | state | `restate_allocation_notice_7a44a997` | ✓ |
| `patronage_ext_estate_retirement` | `patronage_ext_cycle_revolvement` | value_input | `revolved_out` | state | `record_equity_revolvement_d16ad296` | ✓ |

- Every `problem` points at another extended policy id in this file; none points at a base policy or at itself. The graph is a DAG (accrual → {restatement, retain} → transfer; revolvement → estate retirement); no cycle, and no cross-task reference creates one.
- Every `gate` names a binding that genuinely exists in the blocked policy's `compute`: `accrual_sum` (restatement, line 267), `accrued_grain` (retain, line 64 of its compute), `retain_credits` and `restated_allocation` (transfer), `revolved_out` (estate). Every `kind` is `value_input` and each gate is an input to the computed quantity, not an eligibility flag — consistent with `kind`.
- Every `resolved_by` is the depended-on policy's own `target_tool`, and each `effect` sentence is a true statement about this charter's bindings (verified by recomputation on both worlds; the per-task files carry the figures).
- `form: state` on all five, so no `fallback_reason` is required and none is present — correct.
- No `condition` is strengthened or weakened relative to its `policy_source` (see the next section), and no `prerequisite` field carries authoring-viewpoint phrasing ("in this task", "at the opening", "the current world").

### prerequisite_sentences

Check 6, four-point test per edge. Each `policy_source` was located verbatim in the **blocked** policy's own `rule`.

1. `patronage_ext_allocation_restatement` ← accrual — *"A notice is restated only after every parcel of that year's qualifying business stands accrued on the equity ledger."* Ordering connective **only after**; what it waits on is a record-visible state (*"stands accrued on the equity ledger"*) in the words the ledger uses, with no performer and no tool; no snake_case token, no policy id, no row id. Scope matches the `condition` (*"the accrual rows standing on the equity ledger for the year restated carry the whole of that year's qualifying business on each basis"*).
2. `patronage_ext_capital_retain` ← accrual — *"The capital retain for a year is worked out only once the equity ledger carries the whole of that year's qualifying volume on the streams the class lists."* Connective **only once**; state form; scope matches.
3. `patronage_ext_membership_transfer_valuation` ← capital retain — *"The equity signed over is fixed only after the equity ledger carries the capital retain owed for the year most recently allocated."* Connective **only after**; state form; scope matches.
4. `patronage_ext_membership_transfer_valuation` ← restatement — *"Before the equity signed over is worked out, the allocation standing for the year most recently allocated must be the allocation that year's own volume earns."* Connective **Before**; state form (an allocation standing on the ledger), no performer, no tool.
5. `patronage_ext_estate_retirement` ← revolvement — *"The equity settled to an estate is fixed only after the equity ledger carries the revolvement payment due on the fiscal year the membership records as eligible."* Connective **only after**; state form; scope matches.

- **One write per waited-on state.** `patronage_units_accrued` rows are written only by `book_qualifying_units_5a905387` (the only policy whose subject is that event); `patronage_retain_withheld` only by `record_capital_retain_31b65d0b`; `patronage_allocation_adjusted` only by `restate_allocation_notice_7a44a997`; `patronage_equity_revolved` only by `record_equity_revolvement_d16ad296`. No state-form edge has two candidate writes, so each hop resolves in exactly one reading: prerequisite sentence → the ledger rows the sentence names → the one extended policy whose own rule describes writing them.
- **No second wording.** Neither the depended-on policies' rules nor any docstring restates any of these five sentences; no rule carries a second wording, another problem's tool name, another policy id, or an aggregated chain.
- **No undeclared cross-problem order.** Sweeping all six extended rules, the only sentences that join one policy's result to another problem are the five above. No **base** rule sentence grounds any of the five edges (each edge rests on an extended sentence of its own).

### override_declarations

Check 1's finding half, sentence by sentence against each policy's `base_policy_refs`. Three of the six policies carry an `overwrite` entry; three carry `overwrite: []`.

| extended policy | base refs | verdict |
| --- | --- | --- |
| `patronage_ext_year_end_unit_accrual` | `patronage_evt_unit_accrual` | the one departure (which settlements fall in the closed year) is declared, naming the base sentence *"Grain marketed accrues on settled bushels…"* and replacing it. The direct-ship participation share and the conditioning allowance add new content where that replaced sentence stood; no surviving base sentence fixes the grain volume, so no conflict. **OK** |
| `patronage_ext_allocation_restatement` | `patronage_adjustment`, `patronage_cash_payment` | the `patronage_cash_payment` sentence is declared. The `patronage_adjustment` sentence governing the **rate** is contradicted and **not declared** → **F-1, SOURCE-POLICY RED** |
| `patronage_ext_capital_retain` | `patronage_retain` | `overwrite: []`, yet three base provisions on the scored retain are handled differently → **F-2, SOURCE-POLICY RED** |
| `patronage_ext_membership_transfer_valuation` | `patronage_equity_transfer` | the departure from face-value-plus-fee is declared and the `replaced_by` sentence covers the offset, the recording charge, the certificate charge, the stock redeemed and the cash carried in. Base provisions not hit by the overwrite (signed registered instruction, board approval, transferee class, no pledging) are inherited and not weakened. **OK** |
| `patronage_ext_cycle_revolvement` | `patronage_agg_equity_across_classes`, `patronage_revolvement` | `overwrite: []`. Base fixes neither the base amount nor the percentage determinately (*"The pool is a percentage of unrevolved equity fixed each year by the board"*), so the base clause yields no determinate rival number and no conflict is demonstrable → **observation O-1** |
| `patronage_ext_estate_retirement` | `patronage_retirement` | `overwrite: []`. Base states no estate settlement formula: `patronage_retirement.params.per_tier` binds `estate_open` and `estate_notice_days` but **no** estate discount, and the base rule's amount sentence is about **age** retirement only. Base provisions that do apply (application within the notice period, documentation lodged, board approval) are inherited and satisfied. **OK** |

**F-1 — undeclared override of the restatement rate (SOURCE-POLICY RED).**
- Base sentence, `patronage_adjustment.rule` (extended file line 288–289): *"A restatement takes the units off the membership and posts the allocation afresh at the rate declared for the year restated, **never at this year's rate**."*
- Extended `patronage_ext_allocation_restatement` reaches a different rate for two of the three bases it sums, and its own baseline reaches this year's rate for all three:
  - `rule`: *"where a crop input account stands on the early pay prepay programme with a prepay balance still standing on it and a crop input account stands active, the crop input rate is **two cents in the dollar**"* (`K('input_rate_prepay') = 0.0200`);
  - *"where a refined fuels account stands on the contract gallon pre-buy programme with contracted gallons still owed on it …, the refined fuels rate is **three cents in the gallon**"* (`K('energy_rate_contract') = 0.0300`);
  - `baseline.rule`: *"The rate for each basis is **the class's own declared allocation rate** for that basis"* → `P('allocation_rate_input_per_dollar_usd')`, i.e. the rate standing **today**, which is exactly what the base sentence forbids.
- `overwrite` for this policy names only `patronage_cash_payment`'s *"The cash portion is paid once per allocation notice…"*. The `patronage_adjustment` sentence is neither named nor replaced, and `patronage_adjustment` is in this policy's own `base_policy_refs`.
- Bears on: **task 0** (the restatement is a scored write of that task; see `0.md` for the two numbers).

**F-2 — undeclared override of the capital retain (SOURCE-POLICY RED).**
- Base `patronage_retain.rule`: *"The per-unit capital retain is taken separately **at the class's retain rate on the qualifying units of the streams the class lists**, and it is taken whether or not the board declares any allocation at all that year"*, with the base's own binding `formula.retain_amount: round(patronage_units * per_unit_retain_rate_usd, 2)`.
- `patronage_ext_capital_retain` declares `overwrite: []` and departs in three independent ways, each of which alone changes the scored `retain_amount`:
  1. **the rate**: `retain_rate` tier 1 takes *"the rate on the latest of"* the ledger's earlier retain rows instead of `per_unit_retain_rate_usd` (an **anonymous intermediate**: no new parameter name appears, the class rate is simply not used);
  2. **the streams**: `input_share` tier 1 is `K('past_due_share') = 0.00`, a **0/1 multiplier** applied to `accrued_input`, which removes the `input_dollars` stream that `per_unit_retain_applies_to` lists for Class A and Class B — base takes the retain *on the qualifying units of the streams the class lists*, without qualification;
  3. **a weighting base has no room for**: `result = RND(raw_retain * standing_share, 2)` with `standing_share ∈ {0.90, 1.10, 1.00}`, where base's formula ends at `round(units × rate, 2)`.
- Bears on: **task 0** (the capital retain is a scored write of that task; see `0.md` for the two numbers).

**O-1 (observation) — revolvement basis.** `patronage_ext_cycle_revolvement` pays 15 % or 12 % of the credits carrying one eligibility year, doubles it where a death is recorded, and adds a preferred dividend, while base `patronage_agg_equity_across_classes` says *"Revolvement is paid out of a single annual pool the board fixes as a percentage of unrevolved equity"* and base `patronage_revolvement` says *"the board then revolves that year's equity out of the annual pool"*. The two base sentences disagree with each other about the base amount (unrevolved equity vs that year's equity) and neither fixes the percentage, so the base clause yields **no determinate rival number**; recorded as an observation rather than a red. No base sentence forbids the dividend or the offset the extended adds.

**O-2 (observation) — inherited allocation-hold sentence.** Base `patronage_adjustment.rule`: *"While a restatement or a disputed volume is being worked the membership is put under an allocation hold, which stops allocation being posted but does not stop qualifying business accruing"*. It is not overwritten and it is inherited. The lifecycle marks `active → allocation_hold` as a **system** transition and no task tool sets it, so the record stays `active`; the tier conditions that read `F('status')` therefore resolve on the record. Recorded as an observation; the arithmetic consequence it would have on task 0 is set out in `0.md`.

### factor_ladders

Structure only (weight is per task). Counts per computation:

| policy | factors | parameter | method | multi-source tiers | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| `patronage_ext_year_end_unit_accrual` | 4 | 2 | 2 | yes (`late_settlement_reach` tiers 1–2) | grain ×3 |
| `patronage_ext_allocation_restatement` | 5 | 4 | 1 | yes (`input_allocation_rate`, `energy_allocation_rate`, `unpriced_bushel_holdback`) | grain, agronomy, energy |
| `patronage_ext_capital_retain` | 4 | 3 | 1 | yes (`input_spend_participation`, `retain_rate_for_year`) | agronomy |
| `patronage_ext_membership_transfer_valuation` | 6 | 4 | 2 | yes (`owed_balance_offset`, `undelivered_cash_carry`) | agronomy |
| `patronage_ext_cycle_revolvement` | 6 | 4 | 2 | yes (`revolvement_pool_share`, `estate_priority_weighting`, `fuel_arrears_offset`) | energy |
| `patronage_ext_estate_retirement` | 6 | 5 | 1 | yes (`preferred_dividend_arrears`, `estate_balance_offset`) | feed |

Every computation is inside 4–6 factors with ≥2 `parameter` and ≥1 `method`. Every ladder has three tiers; `decides` is always an intermediate binding, never `result`; binding sets are disjoint within each policy; each tier's value or method is drawn from that policy's `params` or from a `variants` parameter; every tier — fall-through included — is stated in the policy's own `rule` and implemented as a branch of the named binding (the fall-through is usually the baseline sentence: e.g. *"The payment carries no weighting for the member's standing."*, *"Nothing is taken off for what the member owed the cooperative"*, *"No dividend arrears are carried on the settlement."*). No two tiers of one ladder select the same value or method, checked against the six variants' parameters (e.g. `revolvement_annual_pool_pct` is 8.0/10.0 on the two classes in play, never 15.0 or 12.0; `dividend_rate_pct` is 4.50 on Class B, never 6.00 or 3.00).

Structural defects found:

**F-3 — two ladders whose third tier is unreachable (SOURCE-FACTOR).**
- `patronage_ext_membership_transfer_valuation.factors.transfer_recording_charge`: tiers 1 and 2 both open with *"a signed transfer instruction stands registered and approved"*, and the fall-through is `P('transfer_fee_usd')`. Base `patronage_equity_transfer.rule` gates the write itself on that very fact — *"only on a signed transfer instruction the equity desk has registered"* and *"Where the class requires board approval, the transfer is not recorded until the board has approved it"* — and `transfer_board_approval_required` is `true` on **every one of the six classes**. The conjunct therefore holds of every customer who reaches this write, the fall-through can never be selected, and the declared three-tier ladder has two live tiers ($25 / $10, split on equity against the class minimum).
- `patronage_ext_estate_retirement.factors.estate_settlement_discount`: identically shaped. Tiers 1 and 2 both open with *"a signed estate application stands registered and approved"*; base `patronage_retirement.rule` makes the application and its documentation a precondition of the write (*"the estate's application is considered only once the class's required estate documentation is lodged and recorded"*) and `board_approval_required_for_retirement` is `true` on all six classes. The fall-through `P('estate_retirement_discount_pct')` is unreachable — and is `0.0` on all six classes in any event.
- Consequence: in both ladders the condition of the first conjunct restates the policy's own scope rather than dividing its customers, so each ladder tests one distinction, not two. Both factors still bear weight on their task's world (see `0.md`, `1.md`), so the defect is the ladder's shape, not its weight.

**F-4 — one `method` label that only substitutes a number (SOURCE-FACTOR).**
- `patronage_ext_membership_transfer_valuation.factors.undelivered_cash_carry` is labelled `effect: method`, but its three tiers all compute the same quantity — the gap between cash declared and cash delivered — scaled by a different number: `cash_gap`, `RND(cash_gap * P('revolvement_annual_pool_pct') / 100, 2)`, `K('no_carry') = 0.00`. No tier changes which rows are read or how the quantity is derived.
- The charter itself contradicts the label: `patronage_ext_estate_retirement.factors.undelivered_cash_settlement` carries the **identical** ladder (whole difference / difference at the pool share / nothing) and is labelled `effect: parameter`.
- Consequence: the transfer computation's declared `method` count (2) is really 1. It still meets the ≥1 `method` floor through `equity_valuation_basis`, which genuinely changes which ledger rows are summed, so no count bound is breached.

**O-3 (observation).** Several ladders divide their customers by a class switch (`equity_certificate_issued` in `certificate_reissue_charge` and `estate_settlement_charge`, `dividend_paid_on_preferred` in `preferred_dividend_rate` and `preferred_dividend_arrears`). For a member of one class the fall-through is then unreachable, but the switch does divide the cooperative's six classes, so this is not the F-3 defect.

**O-4 (observation).** `patronage_ext_estate_retirement.factors.estate_settlement_charge` charges the estate **more** ($60 vs $25) the longer the application has stood registered — i.e. partly for the cooperative's own delay in working the file. The rule's justification (*"follows the work the file has taken"*) is a treatment a cooperative could publish, so this is not recorded as an unreal outcome.

### findings

| id | class | where | bears on |
| --- | --- | --- | --- |
| F-1 | SOURCE-POLICY RED | `patronage_ext_allocation_restatement` — undeclared override of `patronage_adjustment`'s *"never at this year's rate"* | task 0 |
| F-2 | SOURCE-POLICY RED | `patronage_ext_capital_retain` — `overwrite: []` against three provisions of `patronage_retain` | task 0 |
| F-3 | SOURCE-FACTOR | `transfer_recording_charge`, `estate_settlement_discount` — third tier unreachable | task 0, task 1 |
| F-4 | SOURCE-FACTOR | `undelivered_cash_carry` mislabelled `method` | task 0 |
| E-1…E-4 | observation | rule/compute guards, rows-vs-years counts, overlapping prose tiers | neither task's world makes them live |
| O-1…O-4 | observation | revolvement basis, inherited allocation-hold sentence, class-switch ladders, estate charge | see text |

## closing_checklist

Written after both tasks' `source_gt_comparison` sections. **The difficulty does not close out**: Step 4 requires all four relationships to PASS on every task, and task 0 carries SOURCE-POLICY, SOURCE-CHAIN and SOURCE-FACTOR reds while task 1 carries a SOURCE-FACTOR red.

| Step 4 item | state |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks; `_difficulty.md` alongside them | **yes** — `0.md`, `1.md`, `_difficulty.md`; this is revision 1, so there are no old revisions to preserve |
| every comparison section carries a PASS | **no** — `0.md`: SOURCE-POLICY + SOURCE-CHAIN + SOURCE-FACTOR (unique solution PASS); `1.md`: SOURCE-FACTOR (the other three PASS) |
| extended policies fully covered; the M tasks' scopes pairwise disjoint, each spanning its whole tree | **yes** — task 0 = {accrual, restatement, capital retain, transfer valuation} with four tools; task 1 = {cycle revolvement, estate retirement} with two tools; disjoint, and together all six policies and all six tools |
| task tools and GT closed; each uuid8 independently generated and frozen | **yes** — see `### action_binding_and_uuids` |
| every tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` problem, no cycle | **yes** — task 0: 3 problems, 4 `value_input` edges (floor 2), user write at the root; task 1: 1 problem, 1 `value_input` edge (floor 1), user write at the root |
| the difficulty's `prerequisite` edges together are a DAG, with no cycle from cross-task references | **yes** — two disjoint components, accrual → {restatement, retain} → transfer and revolvement → estate retirement |
| every computation: self-sufficient baseline, 4–6 factors (2 `parameter`, 1 `method`; per task ≥1 multi-source, ≥1 cross-difficulty), ladders of ≥3 tiers stated in full in the rule, tiers distinct in outcome, conditions and outcomes ones the business holds | **partly** — counts, baselines, tier statements and distinctness all hold (`### factor_ladders`); **F-3** breaks the "conditions the business weighs" test on two ladders and **F-4** breaks the honesty of one label |
| every factor proved to bear weight against an honest baseline, the baseline alone giving a definite number ≠ gold | **yes** — all 31 declared factors across the six computations bear weight on their task's world; every whole-computation baseline (10 200.00 / 4 530.20 / 528.45 / 15 272.26 / 1 986.81 / 25 459.29) is definite and differs from gold |
| instantiation-stage gates re-run once on the final form | **yes, all green**, re-run 2026-09-18 from the repository root on the unchanged artifacts: `check_extended` EXTENDED OK; `check_task_tools` TASK TOOL CONTRACT OK; `replay_tasks` REPLAY OK (0.json 19 acts, 1.json 14 acts, det/nonvac true, 0 errs, closure matches); `check_solvability` SOLVABILITY OK; `check_compute` COMPUTE OK (branches 49.50, steps 16.50, history_rows_max 88, branches_max 61); `check_grounding` GROUNDING OK; `check_cross_fire` SCOPE OK. The gates do not see any of F-1 … F-4 or the two false proof figures, which is the point of the manual pass. |

**Summary of verdicts.**

- task 0 — policy self-consistency **SOURCE-POLICY RED**; problem tree **SOURCE-CHAIN RED** (the tree holds; a figure in its proof does not); factors **SOURCE-FACTOR RED** (all bear weight; two ladder/label defects and two false proof figures); unique solution **PASS**.
- task 1 — policy self-consistency **PASS**; problem tree **PASS**; factors **SOURCE-FACTOR RED** (all bear weight; one unreachable tier); unique solution **PASS**.

Both tasks' scored solutions were reproduced independently, figure for figure, from the policy, the clock and the seed alone before any GT field was read: 6 504.40 / 48 304.40 / 4 930.44 / 121.73 / 12 164.40 on task 0, and 2015 / 235.46 / 17 429.25 on task 1, together with all 31 factor-sensitivity figures and all six baseline results. No fix is proposed and no audited artifact was edited.

### disclosure — the gate re-run rewrote the two task files

Honest record of a side effect of the Step 4 re-run, which this audit did not intend and did not author by hand:

- `skills/erl-task-instantiate/scripts/replay_tasks.py` runs with `write_back` on and, at line 303, re-serialises each task file after regenerating `db_closure` and `db_closure_matches_initial_state` (`open(tp, "w").write(json.dumps(rebuilt, …))`). Re-running it as Step 4 requires therefore rewrote `tasks/member_equity_desk/tasks/0.json` and `1.json` (mtime 2026-09-18 09:21:21).
- Nothing in this audit edited an audited artifact by hand. The only writes this auditor made are the three files in `env/env_0003_farm_supply_and_grain_cooperative/audits/policy_task/member_equity_desk/`.
- The rewrite is content-neutral for everything this audit rests on: `frozen_time`, `user_scenario` and `initial_state` of both task files are **byte-for-byte identical to the masked views** the brief supplied (`0.json` masked_view sha256[:16] = `155b5b050c81ac6c`, `1.json` = `b96ad164de581f4f` — both recomputed and matching the brief), and the closure the re-run wrote is the same size as the brief's snapshot (70 rows against 70 for task 0, 54 against 54 for task 1, `match = True` in both runs).
- `patronage.extended.yaml` (`1d9268dcd1e6b384`) and `task_tools.py` (`3f5661ad2dbded2d`) are unchanged and still match the brief's hashes.
- One thing this auditor cannot verify after the fact: the brief's `full_task` hashes (`fb73a1ecbe4984d3`, `ff63a72ce0631e6e`) do not reproduce under raw-file or canonical-JSON hashing of the present files, and no snapshot of the files as they stood at 08:55 was taken before the re-run, so whether they already differed from the masking-time state is not determinable here. It does not touch the blind derivations, which rest on the masked views alone and whose hashes do match.

## revision_2

Re-audit round 2, 2026-09-18. Revision 1 above is untouched; everything below is new.

### revision_2 / re-derivation grounds

| input | round 1 | round 2 | treatment |
| --- | --- | --- | --- |
| `patronage.extended.yaml` | `1d9268dcd1e6b384` | **`cd949ffcdd8aab77`** (changed) | every charter-global section **re-derived in full** |
| `task_tools.py` | `3f5661ad2dbded2d` | `3f5661ad2dbded2d` (unchanged) | the tool-module half of `action_binding_and_uuids` (uuid8 generation, docstring silence, function bodies) is **carried forward by reference** on the strength of the identical hash; the `(target_tool, computes)` claims were re-checked against the new charter |
| task 0 masked view | `155b5b050c81ac6c` | **`a435f8e7cf7989fa`** (changed) | task 0's per-task sections re-derived in full in `0.md` → `revision_2` |
| task 1 masked view | `b96ad164de581f4f` | `b96ad164de581f4f` (unchanged) | task 1's world is identical; its figures were nevertheless recomputed against the new charter, see `1.md` → `revision_2` |

This round is **not a blind derivation**: round 1's GT was already revealed, and that is disclosed here rather than concealed. What is verified below is whether each round-1 red is genuinely closed, whether anything that passed has regressed, and whether the rework introduced new defects.

Entry conditions: the difficulty-wide gate block was re-run by the orchestrator at 2026-09-18T09:52 and is green (EXTENDED, TASK-TOOL-CONTRACT, REPLAY 19/14 acts with closure 71/71 and 54/54, SOLVABILITY, COMPUTE, GROUNDING, SCOPE); `check_traceability` still deferred. The auditor did not re-run `replay_tasks.py` this round, since it write-backs the task JSONs (see the revision-1 disclosure).

### revision_2 / what changed in the charter

Diffed against the round-1 text (the base copy is still verbatim identical to `blueprint/products/patronage.yaml`: `diff` of the first 1 030 lines returns only the trailing blank line):

- `patronage_ext_year_end_unit_accrual` — prose only: the `already_accrued` ladder's first tier and its `compute_basis` now state the guard the compute always carried (*"Where **an allocation notice stands posted for the year on the grain basis** and the accrual rows recorded for the year on that basis carry more volume than it was posted on"*). Figures unmoved.
- `patronage_ext_allocation_restatement` — a second `overwrite` entry against `patronage_adjustment`; the grain rate reverted to a plain read of the notice (`notice_grain_rate` used directly in `gross_allocation`, the `grain_rate_for_year` factor deleted); the crop input and refined fuels fall-throughs changed from `P('allocation_rate_*')` to `notice_input_rate` / `notice_energy_rate`; `baseline.rule` now reads *"The rate for each basis is the rate the notice for the year restated carries for that basis"* and `baseline.params` shrinks to `[holdback_none]`; a new factor `input_volume_basis` (method, cross_difficulty agronomy) nets `agronomy_discount_granted` rows off the crop input volume; a new sentence pins which stream the restatement row is recorded against.
- `patronage_ext_capital_retain` — one `overwrite` entry against `patronage_retain`; the always-true `membership_years > 0` conjunct deleted from `retain_rate`; "allocation notices … for twelve or more years" → "twelve or more **allocation lines**"; the `retain_volume` first tier now names the notice, making tiers 1 and 2 disjoint as stated.
- `patronage_ext_membership_transfer_valuation` — `transfer_recording_charge` re-keyed from the approved instruction to the instruction's age (`instruction_days`, 40.00/25.00/`P('transfer_fee_usd')`); `undelivered_cash_carry` relabelled `parameter` with `value` tiers and re-keyed from `F('status')` to `F('tax_reporting_status')`; certificate prose "years" → "lines".
- `patronage_ext_cycle_revolvement` — one `overwrite` entry against `patronage_agg_equity_across_classes`; a new sentence distinguishing the return paid on equity being revolved from the class's standing preferred dividend. Compute untouched.
- `patronage_ext_estate_retirement` — `estate_settlement_discount` re-keyed from the approved application to holding size + `retain_lines`; `estate_applications` removed from the compute. `overwrite: []` retained.

### revision_2 / policy_conflict_scan

Re-run over the new charter. Base copy verbatim; the six `(subject, target_tool, computes)` triples are unchanged and still claimed by exactly one policy each; time anchors still all on `frozen_time`; declared `cross_category` blocks still match the `EXISTS/CFIELD/XSUM` calls (the restatement's agronomy block now also declares `agronomy_invoices.discount_amount`, which the new `XSUM` reads); task scopes still pairwise disjoint and jointly complete. **No conflict remains on any overlapping subject.**

### revision_2 / rule_compute_equivalence

Re-swept. **E-1, E-2, E-3 and E-4 are closed**, each verifiable in the text quoted above. Two residues and one new check:

- **E-5 (observation, new).** `patronage_ext_allocation_restatement.compute.input_discounts` = `XSUM('agronomy','agronomy_invoices','discount_amount', event_type='agronomy_discount_granted')` carries no fiscal-year or date filter, and the rule's tier says only *"discounts stand granted on the member's crop input invoices"* — so the two faces agree, but a rebate granted in any year would reduce the crop input volume of the year being restated. On task 0's world exactly one such row exists (IN-4412488, 2025-12-10, 2 410.00, on the member's own prepay account), so no consequence is demonstrable.
- **E-6 (observation, new).** `transfer_recording_charge` reads `instruction_days = DAYS((LATEST(...) or NOW), NOW)`, so a world with no registered instruction would read nought days and take the "thirty days or fewer" tier, which the rule's prose does not describe. Base `patronage_equity_transfer` makes a registered instruction a precondition of the write, so the case cannot arise; no consequence.
- Base `patronage_retain.formula.retain_amount: round(patronage_units * per_unit_retain_rate_usd, 2)` still states the arithmetic the round-2 `overwrite` retires. The overwrite names the **rule clause** the formula implements, which is the granularity check 1 prescribes, and the merged semantics are unique; recorded as an observation only.

### revision_2 / action_binding_and_uuids

`task_tools.py` is byte-identical (`3f5661ad2dbded2d`), so the uuid8 findings, the docstring-silence sweep and the function-body reading are carried forward from revision 1 by reference. Re-checked against the new charter: each `(target_tool, computes)` pair is still claimed by exactly one policy, and every `prerequisite.resolved_by` still names the depended-on policy's `target_tool`.

### revision_2 / prerequisite_graph and prerequisite_sentences

Re-verified mechanically against the new rules: all five edges' `policy_source` strings are still verbatim locatable in the **blocked** policy's own `rule` (whitespace-normalised substring match, 5/5); every `gate` still names a binding that exists in that policy's compute (`accrual_sum`, `accrued_grain`, `retain_credits`, `restated_allocation`, `revolved_out`); every `resolved_by` still equals the depended-on policy's `target_tool`; all five are `form: state`, `kind: value_input`, with no `fallback_reason`; the graph is the same acyclic pair of components. No rule acquired a second wording, a tool name or another problem's id, and no new cross-problem order appears in any rule. **No regression.**

### revision_2 / override_declarations

All six `overwrite` entries were checked mechanically: in every case the `superseded_clause` is a verbatim substring of the named **base** policy's rule and the `replaced_by` sentence is a verbatim sentence of the **extended** rule, so a reader of the published policy meets the replacement.

- **F-1 CLOSED.** `patronage_ext_allocation_restatement` now carries a second entry naming `patronage_adjustment`'s *"posts the allocation afresh at the rate declared for the year restated, never at this year's rate"* and replacing it with *"Where the member's own programme standing earns a rate on a basis, that programme rate stands in place of the rate the notice carries for it."* The remaining departure is exactly the two programme ladders that sentence describes; every other rate — grain, and all three fall-throughs — is now the rate the notice for the year restated carries, which is what the base clause required. The rival reading of round 1 (4 608.11) no longer exists: following base and following the extended now agree except where the declared override speaks.
- **F-2 CLOSED.** `patronage_ext_capital_retain` now names *"taken separately at the class's retain rate on the qualifying units of the streams the class lists"* and replaces it with a single sentence covering all three departures (the crop input share, the ledger rate, the standing weighting). The replacement is in the extended rule, and the merged semantics are unique. The rival 557.86 reading is retired by declaration.
- **O-1 CLOSED** (beyond what the round-1 finding asked): `patronage_ext_cycle_revolvement` now declares the basis departure against `patronage_agg_equity_across_classes`.
- **O-2 CLOSED**: no computation of this charter now reads `patronage_memberships.status`, so the inherited allocation-hold sentence no longer bears on any scored tier.
- `patronage_ext_estate_retirement` keeps `overwrite: []`; re-checked sentence by sentence against `patronage_retirement` — that base policy still fixes no estate settlement amount (its `per_tier` binds `estate_open` and `estate_notice_days`, not the estate discount) and its surviving provisions (application inside the notice period, documentation lodged, board approval) are inherited and satisfied. Correct as it stands.

### revision_2 / factor_ladders

| policy | factors | parameter | method | tiers | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| year_end_unit_accrual | 4 | 2 | 2 | 3,3,3,3 | grain ×3 |
| allocation_restatement | 5 | 3 | 2 | 3,3,3,3,3 | agronomy ×2, energy, grain |
| capital_retain | 4 | 3 | 1 | 3,3,3,3 | agronomy |
| membership_transfer_valuation | 6 | 5 | 1 | 3,3,3,3,3,3 | agronomy |
| cycle_revolvement | 6 | 4 | 2 | 3,3,3,3,3,3 | energy |
| estate_retirement | 6 | 5 | 1 | 3,3,3,3,3,3 | feed |

All within 4–6 with ≥2 `parameter` and ≥1 `method`; every ladder still three tiers, stated in full in its own rule and implemented in compute; no two tiers of any ladder select the same value or method (checked against the six variants' parameters — 40/25/50 on the recording charge, 3/8/0 on the estate discount, and the class figures are 50.00 and 0.0 respectively).

- **F-3 CLOSED.** Neither `transfer_recording_charge` nor `estate_settlement_discount` now opens a tier with the write's own precondition. The recording charge divides on the age of the registered instruction against a thirty-day line, with both tiers additionally requiring equity above the class minimum ($25.00 on Class A), so the fall-through fires for a membership at or below it; the estate discount divides on the holding against ten times the class minimum ($1 000.00 on Class B) and on the count of retain lines, so the fall-through fires for a holding of $10 000 or less. Both fall-throughs are reachable, and both conjuncts are conditions this line of business genuinely weighs.
- **F-4 CLOSED.** `undelivered_cash_carry` is now `effect: parameter` with `value` tiers, matching `undelivered_cash_settlement` in the estate policy, and its tiers now divide on `tax_reporting_status` (`qualified` / `nonqualified` / else), which `db_schema.json` declares as an enum of `qualified`, `nonqualified`, `mixed` — so the fall-through the prose names is a state the schema admits.
- **F-5 (observation, new).** The new `input_volume_basis` is labelled `method` and earns it: its tiers change which records the crop input volume is drawn from (the year's accrual rows / the notice less the discount rows / the notice), not merely a number.
- **O-3 and O-4 stand unchanged**, as the reworker states: ladders that divide by a class switch (`equity_certificate_issued`, `dividend_paid_on_preferred`) still make their fall-through unreachable for a member of one class while dividing the cooperative's six classes, which is not the F-3 defect; and the estate settlement charge still rises with the time the file has stood registered.

### revision_2 / findings

| id | class | where | bears on |
| --- | --- | --- | --- |
| F-1, F-2, F-3, F-4 | **closed** | see above | — |
| E-1…E-4, O-1, O-2 | **closed** | see above | — |
| E-5, E-6, F-5 | observation (new) | unfiltered discount read; `instruction_days` default; the new method label | neither task's world makes E-5/E-6 live |
| O-3, O-4 | observation (carried, unchanged by design) | class-switch ladders; estate settlement charge | — |
| **R2-1** | **SOURCE-TASK RED (new)** | `patronage_ext_allocation_restatement.rule` — the sentence that pins the restatement row's stream now admits two readings, because the rework made a second stream's volume a restated quantity | task 0 (demonstration in `0.md` → `revision_2`) |
| **R2-2** | **SOURCE-FACTOR RED (new)** | `tasks/0.json` `design_rationale` — two counterfactual figures left at their round-1 values after the ladders that produced them were re-keyed | task 0 (demonstration in `0.md` → `revision_2`) |
| **R2-3** | observation (new) | three `factor_sensitivity.tier_taken` strings and one `factor_trace` phrase in `tasks/0.json` still quote the round-1 ladder wording; one `design_rationale` line in `tasks/1.json` still says the estate application decides the discount tier | tasks 0 and 1 |

## revision_2 / closing_checklist

The difficulty **still does not close out**. Round 1's four charter-global reds and all six of its observations on the charter are genuinely closed, and every figure of both tasks was reproduced independently; but task 0 acquired two new defects in the rework.

| Step 4 item | state |
| --- | --- |
| per-task files one-to-one with the tasks, old revisions preserved | **yes** — revision 1 is untouched in all three files; revision 2 is appended |
| every comparison section carries a PASS | **no** — `0.md` revision 2: SOURCE-TASK + SOURCE-FACTOR; `1.md` revision 2: all four PASS |
| policies covered, scopes pairwise disjoint, tools and GT closed, uuid8s frozen | **yes**, unchanged (tool module hash identical) |
| trees: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` problem, no cycle, DAG across the difficulty | **yes**, unchanged and re-verified against the new rules |
| baselines self-sufficient; 4–6 factors with 2 `parameter` and 1 `method`; ≥1 multi-source and ≥1 cross-difficulty per task; ladders of three distinct, business-real tiers; every factor load-bearing against an honest baseline | **yes** — 31 factors, all load-bearing on their task's world, every whole-computation baseline definite and ≠ gold (10 200.00 / 4 433.95 / 528.45 / 15 272.26 / 1 986.81 / 25 459.29) |
| instantiation gates re-run on the final form | **yes, green**, re-run by the orchestrator 2026-09-18T09:52 and cited rather than re-run here, because `replay_tasks.py` write-backs the task JSONs |

**Round-2 verdicts.** Task 0 — policy self-consistency **PASS** (F-1 and F-2 closed); problem tree **PASS** (the round-1 SOURCE-CHAIN figure is corrected and all four edge figures re-derived); factors **SOURCE-FACTOR RED** (R2-2 only: every factor bears weight and the ladders are sound, but two counterfactual figures in the dossier are stale); unique solution **SOURCE-TASK RED** (R2-1). Task 1 — all four relationships **PASS**.

### revision_2 / disclosure follow-up

`replay_tasks.py` was **not** run this round, so no audited artifact was touched by this audit. Confirmed by hash after the round-2 write-up: `tasks/0.json` = `f90f8cd3b89264fb` and `tasks/1.json` = `1dfd2e589e716d37`, exactly the `full_task` hashes the round-2 brief supplied, and `patronage.extended.yaml` = `cd949ffcdd8aab77`, `task_tools.py` = `3f5661ad2dbded2d`. This also settles the question revision 1's disclosure left open: the round-1 `full_task` mismatch was caused by that round's Step 4 gate re-run rewriting the files, not by any earlier drift. The auditor's writes remain confined to the three files in `env/env_0003_farm_supply_and_grain_cooperative/audits/policy_task/member_equity_desk/`.

## revision_3

Re-audit round 3, 2026-09-18. Revisions 1 and 2 above are untouched.

### revision_3 / re-derivation grounds

| input | round 2 | round 3 | treatment |
| --- | --- | --- | --- |
| `patronage.extended.yaml` | `cd949ffcdd8aab77` | **`0cb618864cd602dd`** (changed) | charter-global sections re-derived |
| `task_tools.py` | `3f5661ad2dbded2d` | `3f5661ad2dbded2d` (unchanged throughout) | tool-module half of `action_binding_and_uuids` carried forward by reference on the identical hash; the `(target_tool, computes)` claims re-checked against the new charter |
| task 0 masked view | `a435f8e7cf7989fa` | `a435f8e7cf7989fa` (**unchanged**) | neither world moved this round; both tasks' figures were nevertheless recomputed from the new rules |
| task 1 masked view | `b96ad164de581f4f` | `b96ad164de581f4f` (unchanged) | as above |

Not a blind derivation (GT was revealed in round 1); disclosed rather than concealed. Entry conditions: the orchestrator's difficulty-wide gate block of 2026-09-18T10:26 is green and is **cited, not re-run** — `replay_tasks.py` write-backs the task JSONs, and the round-1 disclosure showed what that costs. The task-file hashes after this audit are `a0c4028ae0b5c4a0` and `01224da1be63b813`, exactly the `full_task` hashes the round-3 brief supplied, so no audited artifact was touched.

### revision_3 / what changed in the charter

Only two policies moved; the file is the same length, the base copy is still verbatim (`diff` of the first 1 030 lines returns the trailing blank line alone), and `patronage_ext_capital_retain`, `patronage_ext_cycle_revolvement` and `patronage_ext_estate_retirement` are unchanged apart from a line-number shift (all their round-2 fixes re-verified in place: the `membership_years > 0` guard still gone, "twelve or more allocation lines" still in the retain rule, `undelivered_cash_carry` still `parameter` reading `tax_reporting_status`, `estate_settlement_discount` still bound to `[retain_lines, discount_pct]` with `estate_applications` absent from the estate compute, the revolvement's one `overwrite` still present).

- `patronage_ext_allocation_restatement` — the round-2 pinning sentence is replaced by *"A restatement is occasioned by a volume that turns out to have been understated, so the row is recorded against the stream whose volume the year's accrual rows have overtaken, and where the accrual rows have overtaken more than one stream's volume it is recorded against the stream whose overtaking adds most to the allocation. The volume recorded on the row is that stream's volume as restated, and the amount recorded is the whole allocation the year now earns across every basis."*; and the discount read gains a window — `params.discount_window_months: 17`, `input_discounts` now `XSUM(..., within_months=K('discount_window_months'), date_field='invoice_date', ...)`, with *"in the seventeen months up to today"* carried in the rule, the `compute_basis` and the `input_volume_basis` tier alike.
- `patronage_ext_membership_transfer_valuation` — a new `instruction_count` binding (`COUNT('patronage_requests', request_type='equity_transfer')`) guarding the recording charge, and a new rule sentence *"Where no transfer instruction stands registered on the membership at all, the class's own transfer fee applies, since there is no file whose age could tell against it."* quoted by `compute_basis.instruction_count`.

### revision_3 / charter-global checks, re-run

- **policy_conflict_scan** — base copy verbatim; the six `(subject, target_tool, computes)` triples unchanged and each claimed by one policy; task scopes still disjoint and jointly complete; no conflict on any overlapping subject.
- **rule_compute_equivalence** — re-swept over both changed policies. **E-5 CLOSED**: the discount read's window is now stated in all three faces and matches `within_months=17`, the same window the accrual uses. **E-6 CLOSED**: the no-instruction case is now a stated branch rather than a silent default. No new unstated conjunct: every branch condition of `input_volume`, `input_discounts`, `recording_charge` and `instruction_count` has a sentence in its own rule.
- **action_binding_and_uuids** — carried forward on the identical `task_tools.py` hash; pairs re-checked and still one-to-one.
- **prerequisite_graph / prerequisite_sentences** — re-verified mechanically against the changed rules: 5/5 `policy_source` strings still verbatim in the blocked policy's own rule (the restatement's rule was edited around its prerequisite sentence and still carries it word for word), every `gate` still a binding of that policy's compute, every `resolved_by` still the depended-on policy's `target_tool`, all `form: state` / `kind: value_input`, graph still the same acyclic pair of components. The new pinning sentence states no cross-problem order and names no tool, policy id or route.
- **override_declarations** — all six `overwrite` entries re-checked mechanically: superseded clause verbatim in the named base rule, replacement sentence verbatim in the extended rule. F-1, F-2 and O-1 remain closed.
- **factor_ladders** — 4 / 5 / 4 / 6 / 6 / 6 factors, `parameter` 2/3/3/5/4/5 and `method` 2/2/1/1/2/1, every ladder three tiers with distinct outcomes, every tier stated in its own rule and implemented in compute, cross-difficulty factors 3/4/1/1/1/1. **F-3 is not reintroduced on `transfer_recording_charge`** — see the specific check below.

**The `instruction_count` guard, checked specifically (the coordinator asked).** The guard is `recording_charge = (ladder) if instruction_count > 0 else P('transfer_fee_usd')`. It is **not** a tier condition: the ladder's two live tiers are unchanged from round 2 and still divide on the file's age against thirty days and on the equity standing against the class minimum; neither opens with a conjunct that holds of every customer who reaches the write. The fall-through value `P('transfer_fee_usd')` is reachable by two routes that agree — the ladder's own "otherwise" (an instruction stands, equity at or below the class minimum) and the guard (no instruction stands) — and the guard's branch is stated by a sentence of the rule and quoted in `compute_basis`, so both faces carry it and no tier is present in one face and absent from the other. The defect F-3 named (a tier conjunct that restates the write's own precondition, leaving the fall-through unreachable) is therefore not reintroduced.

### revision_3 / findings

| id | class | state |
| --- | --- | --- |
| R2-1 | SOURCE-TASK RED (round 2) | **CLOSED** — demonstration in `0.md` → `revision_3` |
| R2-2 | SOURCE-FACTOR RED (round 2) | **CLOSED** — demonstration in `0.md` → `revision_3` |
| E-5, E-6 | observations (round 2) | **CLOSED** (above) |
| R2-3 / `0.md` Obs D, Obs E; `1.md` Obs F | observations (round 2) | **CLOSED** — no `factor_sensitivity.tier_taken` string in either task now fails to match a `when:` of its ladder; the `factor_trace` phrase reads "allocation lines"; the breadth count reads nine with a per-policy breakdown that matches the nine `cross_difficulty` factors and the gate's `xfac=9`; task 1's dossier line now says the discount tier no longer rests on the application |
| F-1, F-2, F-3, F-4, E-1…E-4, O-1, O-2 | rounds 1–2 | **still closed**, re-verified against the new charter |
| F-5, O-3, O-4, the `patronage_retain.formula` note | observations | unchanged by design, with reasons given; none was a red |
| **R3-1** | observation (new) | the new pinning sentence presupposes at least one overtaken stream; the policy's own ladders admit a world where a restatement is due with none (a prior restatement standing, or a rebate alone), and there the sentence names no stream. Neither task's world is such a world — on task 0 exactly one stream is overtaken — so no consequence is demonstrable |
| **R3-2** | observation (new, residual) | `tasks/0.json` `design_rationale`, "WHY EACH CLASS OF SEED ROW EXISTS", still calls the standing-weighting evidence *"fifteen notices"*. Fifteen is the count of allocation **lines**; the ledger carries thirteen distinct notices (PN-441213…PN-441225). The charter's tier and the `factor_trace` were both corrected to "lines" this round; this narrative aside was not. The tier taken and every figure are unaffected |

## revision_3 / closing_checklist

**The difficulty closes out.** All four relationships now PASS on both tasks.

| Step 4 item | state |
| --- | --- |
| per-task audit files one-to-one with the tasks, `_difficulty.md` alongside, old revisions traceable | **yes** — revisions 1, 2 and 3 appended in place, none rewritten |
| every comparison section carries a PASS | **yes** — `0.md` revision 3 and `1.md` revision 3: policy self-consistency, problem tree, factors and unique solution all PASS |
| extended policies fully covered; the two scopes pairwise disjoint, each spanning its whole tree; task tools and GT closed; each uuid8 independently generated and frozen | **yes** — {accrual, restatement, capital retain, transfer} and {revolvement, estate retirement}; six policies, six tools, no overlap |
| every tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` problem, no cycle; the difficulty's edges a DAG | **yes** — task 0: 3 problems, 4 `value_input` edges (floor 2), user write at the root; task 1: 1 problem, 1 edge (floor 1), user write at the root |
| every computation: self-sufficient baseline, 4–6 factors (2 `parameter`, 1 `method`; per task ≥1 multi-source, ≥1 cross-difficulty), ladders of three distinct, business-real tiers stated in full in the rule, every factor load-bearing against an honest baseline, the baseline alone giving a definite number ≠ gold | **yes** — 31 factors across six computations, every one load-bearing on its task's world; whole-computation baselines 10 200.00 / 4 433.95 / 528.45 / 15 272.26 / 1 986.81 / 25 459.29, all definite and all ≠ gold |
| instantiation-stage gates re-run once on the final form | **yes, green** — the orchestrator's block of 2026-09-18T10:26 (EXTENDED, TASK-TOOL-CONTRACT, REPLAY 19/14 acts with closure 71/71 and 54/54, SOLVABILITY, COMPUTE with `xfac` 9 and 2, GROUNDING, SCOPE), cited rather than re-run because `replay_tasks.py` write-backs the task JSONs. `check_traceability` remains deferred to the KB stage by design |

Open observations at close-out, none of them grounds for rework: F-5, O-3, O-4, the `patronage_retain.formula` residue, R3-1 and R3-2. Each is recorded with its reason and none can be shown to change a scored value, a tier taken or a terminal state on either task's world.

**Round-3 verdicts. Task 0 — policy self-consistency PASS, problem tree PASS, factors bear weight PASS, unique solution PASS. Task 1 — all four PASS.** Every scored value of both tasks is unchanged from round 2 and was reproduced independently this round from the new charter and the unchanged worlds: 6 504.40 / 48 304.40 / 4 884.65 / 121.73 / 12 132.35 on task 0, and 2015 / 235.46 / 17 429.25 on task 1, together with all 31 factor sensitivities, all six baselines and all five edge sensitivities.

## revision_4

Re-audit round 4, 2026-09-18, after the render-layer audit of the published KB returned KB-RUNTIME RED on task 0 and the instantiate agent reworked the source. Revisions 1–3 above are untouched.

### revision_4 / re-derivation grounds

| input | round 3 | round 4 | treatment |
| --- | --- | --- | --- |
| `patronage.extended.yaml` | `0cb618864cd602dd` | **`7f70899dd901d4f5`** (changed) | charter-global sections re-derived |
| `task_tools.py` | `3f5661ad2dbded2d` | `3f5661ad2dbded2d` (unchanged throughout) | tool-module half of `action_binding_and_uuids` carried forward by reference on the identical hash |
| task 0 / task 1 masked views | `a435f8e7cf7989fa` / `b96ad164de581f4f` | unchanged | neither world moved; five scored figures on task 0 moved, so its per-task sections are re-derived in full in `0.md` → `revision_4` |

Not a blind derivation. Gates: the orchestrator's block of 2026-09-18T13:04 is green, `check_traceability` now included; cited, not re-run (`replay_tasks.py` write-backs the task JSONs). Task-file hashes after this audit are `9fe35aab093ba31d` and `ffc135b4f9c93e52`, exactly the brief's — no audited artifact was touched.

### revision_4 / what changed in the charter

Only `patronage_ext_year_end_unit_accrual` moved (+4 lines; every later policy shifts by four and is otherwise byte-identical, and all of rounds 2–3's fixes were re-verified in place). Two ladders had their evidence sets bounded in prose:

- **`conditioning_allowance`** — the rule now reads *"The scale tickets counted are the tickets of the year being reckoned, a ticket falling in the fiscal year its own delivery date lies in: the net bushels on the tickets recorded in the seventeen months up to today, less the net bushels on the tickets recorded in the five months up to today, so that grain received after the year closed is left to the year it was received in. The reach that gathers a late settlement back into the year closed gathers no scale ticket with it, since it speaks of settlements alone."* `out_of_condition_bushels` is now `tickets_to_date − tickets_after_year` with a new `in_year_cutoff_months: 5`.
- **`direct_ship_participation`** — *"The settlement statements counted here are the very statements the year's settled volume is taken from — the same seventeen months up to today, less the same statements left to the new fiscal year by the reach"*; `direct_ship_bushels` is now `direct_ship_to_date − direct_ship_after_year`, the second on `reach_months`.

### revision_4 / the KB-driven RED, verified closed

The render-layer finding was that the ladder named a set (*"the year's scale tickets"*) the prose never bounded while only the private compute bounded it, and bounded it against an in-force base sentence. Checked at the standard the coordinator names — **would the prose entail the computation to a reader who cannot see the binding?**

- **Yes, now.** The window is stated twice over in the rule itself (seventeen months less five months), the boundary principle is stated (*"a ticket falling in the fiscal year its own delivery date lies in"*), and the one thing a reader might otherwise carry across from the settlement rule — the reach — is excluded by name. A reader with no compute reaches exactly `[17 months, 5 months)`.
- **Consistent with the base sentence that stayed in force.** `patronage_evt_unit_accrual`'s *"The fiscal year a parcel of business falls in is fixed by the settlement, invoice or delivery date on the record … and the fiscal year ends 31 August"* is not named by this policy's one `overwrite`, which retires the grain-settlement sentence alone. The reworker's reason for moving the compute rather than the prose therefore holds: pinning the prose to seventeen months would have set the ticket set against a base sentence still in force, and would have needed a second override of a rule governing every stream. I verified the `overwrite` block: one entry, naming *"Grain marketed accrues on settled bushels rather than delivered bushels…"* and nothing else.
- **The twin closed on the same trip.** `direct_ship_participation` now takes its numerator from the same statements the denominator is taken from, and says so; on this world the figure (9 400.00) and the tier (four fifths) are unchanged, as claimed.

### revision_4 / charter-global checks, re-run

- **policy_conflict_scan** — base copy verbatim; six `(subject, target_tool, computes)` triples unchanged, one policy each; scopes disjoint and jointly complete.
- **rule_compute_equivalence** — the two new binding pairs each carry a `compute_basis` quotation that is a verbatim sentence of the rule, and the rule states both subtractions in words. No new unstated conjunct. I also swept the other ladders for the same shape of defect (a named evidence set the prose leaves unbounded while the compute bounds it): `unpriced_bushel_holdback`, `certificate_rows`, `retain_lines`, `allocated_years`, `cash_declared`/`cash_delivered`, `feed_invoiced`/`feed_paid` are unbounded in **both** faces; `input_discounts`, `recent_cash`/`prior_cash` are bounded in both. `prior_retain_rate` reads *"an earlier fiscal year"* against an unfiltered `LATEST`, which coincide because the year's own retain row is the write being made. No second instance found.
- **prerequisite_graph / prerequisite_sentences** — 5/5 `policy_source` strings still verbatim in the blocked policy's own rule; gates, forms, kinds and `resolved_by` unchanged.
- **override_declarations** — all six entries still well-formed (superseded clause verbatim in the named base rule, replacement verbatim in the extended rule). F-1, F-2, O-1 remain closed.
- **factor_ladders** — 4/5/4/6/6/6 factors; `parameter` 2/3/3/5/4/5, `method` 2/2/1/1/2/1; every ladder three tiers with distinct outcomes, every tier stated in its own rule; cross-difficulty 3/4/1/1/1/1 (nine on task 0, two on task 1, matching the gate's `xfac`).

### revision_4 / the two items judged and not changed

- **Date of death.** Verified against the frozen schema: `patronage_memberships` carries `birth_year` and `estate_flag` and no death date; `customers` and `patronage_requests` carry none either. Every **scored** ladder that turns on the death turns on `estate_flag` (`estate_priority_weighting`, `pool_ceiling_release`, `undelivered_cash_settlement`) or on `requested_date` (`estate_settlement_charge`); none reads a date of death. Only base `patronage_retirement`'s notice-period eligibility rests on it, its authority is the lodged documentation, and the persona states the value (11 June 2025, 107 days before the application of 2025-09-26, inside the class's 365 days). The reasoning holds; no scored figure is touched.
- **The retired clause's parameter.** `retain_rate_for_year`'s fall-through is `P('per_unit_retain_rate_usd')` while the base clause that used the class rate is retired by the round-2 `overwrite`. The reasoning holds: the retired sentence is a handling sentence, the parameter remains declared in `parameter_schema` and on every variant, and the fall-through is grounded in the **extended** policy's own sentence *"The rate taken is the class's own per-unit retain rate."* A tier value drawn from a variant parameter is what `factor_ladders` requires.

### revision_4 / findings

| id | class | where | bears on |
| --- | --- | --- | --- |
| the KB-driven RED (conditioning window) and its twin | **closed** | verified above | — |
| the two judged items | **sound**, no change needed | verified above | — |
| R3-1 | observation (carried) | the pinning sentence still presupposes at least one overtaken stream | neither world |
| R3-2 | observation (carried, still present) | *"the standing weighting (fifteen notices)"* in `tasks/0.json` — fifteen is the count of allocation lines, thirteen is the count of notices | task 0 |
| **R4-1** | **SOURCE-TASK RED (new)** | a half-cent tie whose only stated tie-break points away from the scored value | task 0 (`0.md` → `revision_4`) |
| **R4-2** | **SOURCE-CHAIN + SOURCE-TASK RED (new)** | three live proof fields in `tasks/0.json` still carry the retired 48,304.40 | task 0 (`0.md` → `revision_4`) |
| **R4-3** | **SOURCE-TASK RED (new to this report, pre-existing in the artifact)** | `tasks/1.json` `argument_uniqueness_tracing.revolvement_amount` still carries 1,607.70 and an invented "19.59 the year's rounding" | task 1 (`1.md` → `revision_4`) |
| **R4-4** | observation (new) | the five-month proxy for the 31 August year-end | neither world |

**On the stale-proof-figure class.** This is now its fourth and fifth appearance in this difficulty (round 1 Finding 6, round 2 R2-2, and R4-2/R4-3 here). The reworker reports a sweep of both dossiers this round; the sweep repaired the `factor_trace`, the `VERIFICATION` block, the seed-row counterfactuals and the "where carelessness loses it" figures — all of which I re-verified figure by figure and found correct — but missed the `stage_provenance` fact, two `argument_uniqueness_tracing.allocation_basis` fields and one `argument_uniqueness_tracing.revolvement_amount` field. Two of the four contradict a sibling sentence inside the same call object.

**On the count in the reworker's account.** Its message says twelve of the nineteen factor sensitivities moved. By my recomputation **fifteen** moved and four did not (`late_settlement_reach` 0, `conditioning_allowance` 7 240.00, `restated_volume_basis` 4 016.29, `retain_volume_basis` 97.02). The count appears only in that account, not in any artifact — the dossier says only that every factor still bears weight, which is true — so it is recorded here for accuracy and is not a defect of the artifacts.

## revision_4 / closing_checklist

**The difficulty does not close out this round.** Round 3's close-out is superseded: the render-layer audit showed the source did not entail its computation to a reader without the binding, that root is now fixed, but this round's re-derivation turns up three fresh reds of the proof-accuracy and rounding classes.

| Step 4 item | state |
| --- | --- |
| per-task files, old revisions traceable | **yes** — revisions 1–4 appended, none rewritten |
| every comparison section carries a PASS | **no** — `0.md` revision 4: SOURCE-CHAIN + SOURCE-TASK; `1.md` revision 4: SOURCE-TASK |
| policies covered, scopes disjoint, tools and GT closed, uuid8s frozen | **yes**, unchanged |
| trees: depth, `value_input` floors, `owner=user` problem, acyclicity | **yes**, unchanged and re-verified |
| baselines self-sufficient; factor counts; ladders of three distinct, business-real tiers; every factor load-bearing | **yes** — 31 factors, all load-bearing; baselines 10 200.00 / 4 433.95 / 528.45 / **15 273.50** / 1 986.81 / 25 459.29, all definite and ≠ gold |
| instantiation gates re-run on the final form | **yes, green**, cited from the orchestrator's 13:04 block, `check_traceability` included |

**Round-4 verdicts. Task 0 — policy self-consistency PASS, factors bear weight PASS, problem tree SOURCE-CHAIN RED (R4-2), unique solution SOURCE-TASK RED (R4-1, R4-2). Task 1 — policy self-consistency PASS, problem tree PASS, factors bear weight PASS, unique solution SOURCE-TASK RED (R4-3).** Every scored figure of both tasks was reproduced independently from the reworked charter: 6 994.80 / 48 794.80 / 4 904.45 / 122.97 / 12 147.44 on task 0, and 2015 / 235.46 / 17 429.25 on task 1.

## revision_5

Re-audit round 5, 2026-09-18. Revisions 1–4 untouched.

### revision_5 / re-derivation grounds

| input | round 4 | round 5 | treatment |
| --- | --- | --- | --- |
| `patronage.extended.yaml` | `7f70899dd901d4f5` | **`c010bb730960ae36`** (changed) | charter-global sections re-derived |
| `task_tools.py` | `3f5661ad2dbded2d` | unchanged throughout | tool-module half carried forward by reference |
| task 0 masked view | `a435f8e7cf7989fa` | **`b1496290791cb15e`** (changed — three seeded levers) | task 0 re-derived in full in `0.md` → `revision_5` |
| task 1 masked view | `b96ad164de581f4f` | unchanged | recomputed anyway against the new charter |

Gates: the orchestrator's block of 2026-09-18T14:26 is green including `check_traceability`; cited, not re-run. Task-file hashes after this audit are `3ac224aff7ef8a35` and `da7cf2c24de62395`, exactly the brief's — no audited artifact was touched.

### revision_5 / what changed

- **Charter (+2 lines).** Every one of the six policies now carries the rounding convention in its **own `rule`** and again in its **`baseline.rule`** — twelve statements in all, verified by grep and read in place (*"Every figure this rule works out is carried to two decimal places, and a half cent rounds up"*, and the equivalent in each of the other five) — matching the tool contract's *"half a cent rounding up"*. The accrual rule adds *"The five-month mark is where the desk draws the close of the year, and a record dated between that mark and the last day of the fiscal year falls to the new year by it, the mark and not the calendar deciding the side a record lies on"*, in the rule and in the baseline paragraph, and the conditioning paragraph now reads *"a ticket falling on the side of the mark its own delivery date lies on"*. No `compute` binding changed.
- **Task 0's world: three levers**, diffed row by row against the round-4 view — settlement S-441204 of 2025-02-12 from 17 800.00 to 17 600.00 bushels (with `gross_amount`/`net_amount` from 76 540.00 to 75 680.00, the same $4.30 a bushel); the FY2025 refined-fuels volume from 12 800.00 to 12 750.00 on **both** the accrual row and the notice line it was posted on; and the rebate from 2 410.00 to 2 400.00. `frozen_time` and `user_scenario` are byte-identical.

### revision_5 / R4-1, verified closed in both halves

**(a) The convention is now stated where a reader meets it.** Twelve statements across the six rules and their baseline paragraphs, agreeing with the tool contract. A reader with no compute now has a tie-break.

**(b) The midpoint sweep, run independently.** I instrumented my own evaluator to flag any value handed to `RND` (and to the internal rounding in `SUM`/`XSUM`) lying within 1e-9 of a half cent, and ran it over every evaluation the gates make: each computation at handling time, all 31 factor-baseline substitutions, all six whole-computation baselines, all five prerequisite-skip replays, and the dossiers' counterfactual replays, on both tasks.

| artifacts | midpoint hits |
| --- | --- |
| round-4 task 0 | **13 flagged evaluations from four distinct products** — 3 433.115 (ten evaluations: gold, the whole baseline, six of the seven factor substitutions and two edge replays), 4 647.495, 469.84499999999997, 4 135.505 |
| round-4 task 1 | 0 |
| **round-5 task 0** | **0** |
| **round-5 task 1** | **0** |

The reworker's account of the round-4 exposure is therefore right and my round-4 demonstration was the smaller part of it: four products, not one. Its count of twelve against my thirteen is my harness evaluating the gold transfer twice; the distinct-product count agrees exactly. The reseed removes every midpoint from both worlds, which I confirm independently.

**Consistency of the reseed, checked where it touches.** The refined-fuels lever moves the accrual row and the notice line **together** (both 12 750.00), so `energy_units` and `notice_energy_rate` still describe the same parcel; the notice line's own arithmetic follows the newly stated convention — `allocated_amount` 318.75 = 12 750 × 0.025 exactly, `cash_portion_amount` 95.63 = 95.625 rounded up, `equity_portion_amount` 223.12 = 318.75 − 95.63, which is what base `patronage_allocation.formula` prescribes; and the two figures propagate correctly into the transfer (`cash_declared` 6 901.61, down 0.37, and `notice_equity` 16 103.69, down 0.88). The settlement lever keeps its price per bushel. None of the three is named anywhere in `user_scenario`, which is unchanged.

### revision_5 / R4-4, verified closed

The five-month mark is now stated outright as where the desk draws the close of the year, in the accrual rule and again in its baseline paragraph, so it governs the settlement window and the ticket window alike; the conditioning paragraph speaks of *"the side of the mark"* rather than of the fiscal year. One set no longer has two boundaries, and because no record falls between 2025-08-15 and 31 August no figure moves — verified against the seed: tickets 2024-10-15, 2025-02-10, 2025-06-20, 2025-10-05 and settlements 2024-10-18, 2025-02-12, 2025-06-24, 2025-10-09, 2025-12-18.

### revision_5 / charter-global checks, re-run

All still hold and none regressed: base copy verbatim; six `(subject, target_tool, computes)` triples, one policy each; 5/5 prerequisite sentences verbatim in their blocked policy's own rule with gates, forms and `resolved_by` unchanged; six `overwrite` entries still well-formed; 4/5/4/6/6/6 factors with `parameter` 2/3/3/5/4/5 and `method` 2/2/1/1/2/1, every ladder three tiers stated in its own rule, cross-difficulty 9 on task 0 and 2 on task 1. **No ladder tier moved on either task** despite five scored figures moving on task 0 — I checked every tier taken against the records: reach two months, direct share four fifths, conditioning nine hundred and ninety-five thousandths, prior accrual from the rows; restated volume from the rows, crop input volume from the notice less the rebate, crop input two cents, refined fuels three cents, holdback ninety-five hundredths; retain volume from the rows, no crop input spend, the ledger's 0.0028, nine tenths; valuation from the restatement, prompt recording charge, crop input offset, certificate at fifteen, stock at par, whole cash carried.

### revision_5 / findings

| id | class | state |
| --- | --- | --- |
| R4-1 (a) and (b) | **CLOSED** — convention stated in all twelve places; zero midpoints on both worlds, verified by my own detector |
| R4-2 | **CLOSED** — all three fields now carry what their binding produces (48 635.60), verified against my recomputation |
| R4-3 | **CLOSED** — task 1's tracing now reads the ledger's own 1 627.29 and 172.20 and says the binding is a plain sum with no rounding step |
| R4-4 | **CLOSED** — see above |
| R3-1 | observation, carried unchanged (the pinning sentence presupposes at least one overtaken stream; not live) |
| R3-2 | observation, carried unchanged (*"the standing weighting (fifteen notices)"* — fifteen is the count of allocation lines, thirteen of notices) |
| **R5-1** | **SOURCE-FACTOR RED (new)** — `tasks/0.json` `design_rationale` still names the rebate as 2 410.00 and the crop input volume as 135 240.00, both retired by this round's reseed; demonstration in `0.md` → `revision_5` |
| **R5-2** | observation (new) — the convention and the implementation still differ in principle; the fix is that these two worlds contain no computed midpoint, not that the engine rounds as the prose says |

**On the sweep.** The reworker reports 0 unmatched literals on both tasks over a field list it sets out in full. I ran my own sweep of every live proof field of both task files against the retired figures of rounds 3 and 4 — the dossier bodies excluding the revision log, `solvability_contract`, `evaluation_criteria` (objectives, necessities, arguments and every tracing entry), `computations` and `prerequisite_closure` — and found exactly **one** unmatched literal, R5-1. Everything else is current, including the twenty-seven figures of the `VERIFICATION` block, the four edge sensitivities, the seed-row counterfactuals and the "where carelessness loses it" figures, each of which I replayed rather than read.

**A correction to my own earlier reports.** The reworker is right that its sweep caught something I had not. From round 1 to round 4 this task's seed bullet said *"remove the 2025-12-02 accrual and the accrual shortfall, the restatement and the retain all move"*, and I replayed only the accrual and let the rest stand. Replayed in full now: removing that row raises the accrual from 6 835.60 to 10 135.60 and leaves the restatement at 4 896.78 and the retain at 122.56, because both downstream policies read the accrual rows **after** the accrual write, which restores the same total either way. The bullet now says exactly that, and it is correct. Recorded here rather than by amending revisions 1–4, which stand as written.

## revision_5 / closing_checklist

**The difficulty does not close out this round**, on a single finding.

| Step 4 item | state |
| --- | --- |
| per-task files, old revisions traceable | **yes** — revisions 1–5 appended, none rewritten |
| every comparison section carries a PASS | **no** — `0.md` revision 5: SOURCE-FACTOR (R5-1). `1.md` revision 5: all four PASS |
| policies covered, scopes disjoint, tools and GT closed, uuid8s frozen | **yes**, unchanged |
| trees: depth, `value_input` floors, `owner=user` problem, acyclicity | **yes**, re-verified on the moved world |
| baselines self-sufficient; factor counts; ladders of three distinct, business-real tiers; every factor load-bearing | **yes** — 31 factors, all load-bearing; baselines 10 000.00 / 4 432.70 / 528.45 / 15 272.21 / 1 986.81 / 25 459.29, all definite and ≠ gold |
| instantiation gates re-run on the final form | **yes, green**, cited from the orchestrator's 14:26 block |

**Round-5 verdicts. Task 0 — policy self-consistency PASS, problem tree PASS, unique solution PASS, factors bear weight SOURCE-FACTOR RED (R5-1). Task 1 — all four PASS.** Every scored figure of both tasks was reproduced independently from the reworked charter and the reseeded world: 6 835.60 / 48 635.60 / 4 896.78 / 122.56 / 12 141.30 on task 0, and 2015 / 235.46 / 17 429.25 on task 1.

## revision_6

Re-audit round 6, 2026-09-18. Revisions 1–5 untouched.

### revision_6 / re-derivation grounds

| input | round 5 | round 6 | treatment |
| --- | --- | --- | --- |
| `patronage.extended.yaml` | `c010bb730960ae36` | `c010bb730960ae36` (**unchanged**) | every charter-global section is **carried forward by reference** on this hash, per the re-audit rule; nothing in the charter can have moved a conclusion |
| `task_tools.py` | `3f5661ad2dbded2d` | unchanged throughout | carried forward |
| task 0 masked view | `b1496290791cb15e` | `b1496290791cb15e` — byte-identical (`cmp`) | world unmoved |
| task 1 masked view | `b96ad164de581f4f` | byte-identical | world unmoved |
| `tasks/0.json` | `3ac224aff7ef8a35` | `83337d5bc6a1cd7f` | re-read in full |
| `tasks/1.json` | `da7cf2c24de62395` | `d3c571fb10a2f4f3` | re-read in full |

Because neither the charter nor either world moved, the scored figures cannot have moved, and I confirmed that by recomputing all six of them from the unchanged computes: task 0 **6 835.60 / 48 635.60 / 4 896.78 / 122.56 / 12 141.30**, task 1 **2015 / 235.46 / 17 429.25**, with every factor sensitivity, whole baseline and edge figure as recorded in revision 5. Gates cited from the orchestrator's 15:00 block, not re-run. Task-file hashes after this audit are exactly the brief's — no audited artifact was touched.

### revision_6 / R5-1, verified closed

`tasks/0.json` `design_rationale`, the agronomy bullet, now reads *"the **2,400.00** program rebate on invoice IN-4412488 … is what puts the crop input volume the restatement rests on at **135,250.00** rather than the 137,650.00 the notice was posted on."* Both figures are what the artifacts themselves produce: the seed row carries `discount_amount 2400.0`, my recomputation gives `input_discounts = 2 400.00` and `input_volume = 135 250.00`, and the step-14 tracing two fields away says the same. The counterfactual at the end of the same sentence (4 942.38 / 12 173.22) was already correct and was replayed again this round.

**Task 1's file changed without a round-6 log entry.** Its `full_task` hash moved while the reworker's account says the agronomy bullet was the only content change. I have no round-5 copy to diff against, so I cannot say what moved; what I can say is that my own full sweep of its live proof fields (below) finds nothing unmatched and every figure of the task reproduced, so whatever changed is not a defect. Recorded for accuracy.

### revision_6 / is the strict sweep actually stronger? — tested, not taken on trust

I rebuilt the two tests on my own harvest and ran them against the values at issue.

- I harvested **280 real values** for task 0 from my own evaluator — every compute binding of every policy at its handling time, every binding under each of the nineteen factor-baseline substitutions and each whole-computation baseline, every binding under each skip replay and under each of the eight declared counterfactual worlds, every seeded field, and every class and policy parameter.
- Round-5's test, reconstructed: that set plus every pairwise sum and difference plus scalar multiples. Mine came to **109 412 numbers** (the reworker reports 87 584 from 247 reals; my scalar list is longer, the shape is the same).
- **The decisive check.** `2,410.00` and `135,240.00` — the R5-1 pair — are **in the closure** and in **neither** real set. So the round-5 test provably could not have caught them, and the strict test does. The reworker's diagnosis is right, and its claim that the strict version catches what round 5 passed is verified rather than accepted.
- **Density.** A random two-decimal value drawn in [1 000, 20 000] is accepted by the closure **2.0 %** of the time and by the strict real set **0.007 %** — a fall of roughly 290-fold in the false-accept rate. At closure density the test was close to vacuous over the band these figures live in.
- **Stronger, not merely differently shaped.** Structurally, every real value lies in its own closure, so the strict acceptance set is a subset of the closure on a shared harvest: the strict test can only flag more, never fewer. Where its harvest is wider than round 5's — the intermediates of baseline substitutions and skip replays — the widening can only prevent false alarms on values the artifacts' bindings genuinely produce; it cannot admit a figure no binding produces, because nothing is reached by arithmetic any more. The residual limitation, which is real and worth stating: a stale figure that happened to coincide with a legitimate harvested intermediate would still pass, but the space it must hit is 442 declared values rather than ~87.6k derived ones.
- The two declared tables are the right shape, and I know that independently: my own sweep needed exactly the same two classes to avoid false alarms — the inline comparison products the rules state in words (five times the out-of-condition bushels, three times the direct-ship bushels, the class-minimum multiples) and the counterfactual worlds, which must be replayed rather than asserted. The two masking bugs it reports fixing are the two my own literal extractor hit first: a calendar-year mask swallowing the integer part of a decimal, and uuid8 tails read as quantities.

### revision_6 / my own literal sweep

Built independently of theirs: every numeric literal in the live proof fields of both task files — `user_scenario`, the `design_rationale` body with the revision log excluded, `solvability_contract`, `evaluation_criteria` (objectives, necessities, arguments and every tracing entry), `computations` (every `factor_trace` line and `factor_sensitivity` tier) and every `prerequisite_closure` field — checked against my harvested authoritative set after masking dates, business reference numbers and row ids.

| task | literals checked | unmatched |
| --- | --- | --- |
| 0 | 436 | **0 quantity literals** (residue: the ledger row count 46, the four per-policy branch counts, a step number, and "31 August") |
| 1 | 205 | **0 quantity literals** (residue: the row count 43, a branch count, and dates written in words with the 107-day span) |

The residue is structural rather than quantitative, and two of its members cross-check the artifacts: the four per-policy branch counts in task 0's `VERIFICATION` block sum to **67** and task 1's two sum to **38**, exactly the `brch` figures the compute gate reports. So my instrument and theirs agree that nothing stale remains, by different routes.

### revision_6 / R5-2, judged

**The disposition is right: carry it as a standing caveat, do not close it, and do not treat it as a red.** My grounds, which are the audit's own: there is no demonstrable consequence on either world — no computed value on either task lands within a billionth of a half cent (my detector, run again this round over every evaluation the gates make, reports none), the rules and the tool contract now state one convention, and the single divergent value is a seed field that no binding computes. A red requires a consequence demonstrated on the world in front of us, and there is none to demonstrate. The instrument the record now names — the RND detector, re-run on any reseed or new task — is the right one, and the stated escalation (if a future world cannot avoid a computed midpoint, change the policy's arithmetic rather than the prose) is the right order of remedy.

**One premise of the reasoning is false, and should not be left on the record as fact.** The entry says *"the obvious substitute, int(x * 100 + 0.5) / 100, fails the same way because the double is already below the midpoint before the half is added."* On the value this difficulty actually turned on it does not: for `x = 4904.45 * 70 / 100`, `round(x, 2)` gives 3 433.11 while `int(x * 100 + 0.5) / 100` gives **3 433.12**, the half-up answer, because the multiplication by a hundred rounds the product back up to the midpoint before the half is added. It gives the half-up answer on the seeded 95.625 too. The expression is unreliable in general — it does fail on values such as 1.005, and it is wrong for negatives — so the conclusion that no sound exact-decimal remedy exists inside the restricted language stands; but it does not stand on that sentence, which is a checkable arithmetic claim contradicted by running it. Recorded as an observation (**R6-1**): it changes no scored value, no tier, no edge and no argument's uniqueness, and the disposition it supports survives on its other grounds.

### revision_6 / does anything still rest on a reader seeing a binding?

**No scored figure does.** I checked every quantity a solver must produce against the published surfaces alone — the rules, the baseline paragraphs and the factor ladders, plus the tool contracts — with the compute set aside:

- every window is stated in words (seventeen months; the five-month mark, now named once as where the desk draws the close and governing both the settlement and the ticket sets; the two-, four- and five-month reach; the seventeen months on the discount read);
- every counting basis is stated as what it counts (allocation **lines**, capital retain **lines**, retain rows from an earlier fiscal year and the latest of them);
- the row the restatement is recorded against is fixed by the overtaking sentence, with its tie-break;
- the tie-break for a half cent is stated in all twelve places and agrees with the tool contract;
- every ladder's three tiers, its fall-through and its evidence set are in the policy's own rule, and every prerequisite is stated by a prerequisite sentence in the blocked policy's own rule.

Two residuals, neither with a consequence on these worlds and neither a scored figure: the recording-charge sentence says *"the transfer instruction registered on the membership"* in the singular where the binding takes the latest of them, which would matter only to a membership carrying two registered instructions and neither world does; and R5-2's convention-versus-implementation gap, which is world-dependent by construction and carries its detector with it.

## revision_6 / closing_checklist

**The difficulty closes out.** All four relationships PASS on both tasks.

| Step 4 item | state |
| --- | --- |
| per-task files one-to-one with the tasks, `_difficulty.md` alongside, old revisions traceable | **yes** — revisions 1–6 appended in place, none rewritten |
| every comparison section carries a PASS | **yes** — `0.md` and `1.md` revision 6 |
| extended policies fully covered; scopes pairwise disjoint, each spanning its whole tree; tools and GT closed; uuid8s independently generated and frozen | **yes**, carried forward on the unchanged charter and tool hashes |
| every tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` problem, no cycle; the difficulty's edges a DAG | **yes** — task 0: 3 problems, 4 `value_input` edges, user write at the root; task 1: 1 and 1, user write at the root |
| every computation: self-sufficient baseline, 4–6 factors (2 `parameter`, 1 `method`; per task ≥1 multi-source and ≥1 cross-difficulty), ladders of three distinct, business-real tiers stated in full in the rule, every factor load-bearing against an honest baseline, the baseline alone giving a definite number ≠ gold | **yes** — 31 factors, all load-bearing; baselines 10 000.00 / 4 432.70 / 528.45 / 15 272.21 / 1 986.81 / 25 459.29 |
| instantiation-stage gates re-run once on the final form | **yes, green**, the orchestrator's 15:00 block including `check_traceability`; cited rather than re-run because `replay_tasks.py` write-backs the task JSONs |

Open observations at close-out, none grounds for rework and each recorded with its reason: F-5, O-3, O-4, the `patronage_retain.formula` residue, R3-1, R3-2, **R5-2** (carried as a standing caveat with its detector) and **R6-1** (the false premise in R5-2's reasoning). The cross-difficulty and scenario-level disposition of R5-2 — it is reported to run alongside a similar caveat from another difficulty — is outside this skill's remit and is not ruled on here.

**Round-6 verdicts. Task 0 — policy self-consistency PASS, problem tree PASS, factors bear weight PASS, unique solution PASS. Task 1 — all four PASS.** Six rounds, and the last defect of the stale-proof-figure class is closed; nothing a solver must compute now depends on reading a binding.

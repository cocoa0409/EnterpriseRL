# Policy-task audit — home_claim_settlement / charter-global

## charter_global_frozen

- Auditor: independent erl-task-policy-audit agent (round 1). I did not write any of the audited artifacts.
- Written: 2026-09-24T23:47Z. This section was written before any task's GT was revealed. It rests only on the charter, the schema, the shared tools and the task-tool module.
- Freeze hashes (re-checked on disk; they match the orchestrator's view-construction hashes):
  - `tasks/home_claim_settlement/home.extended.yaml` sha256 `9a5d153fe660905f4f890e50056d9321e1bec4640bde1ee7a96a969f34244c8c`
  - `tasks/home_claim_settlement/task_tools.py` sha256 `c40f08d827450bd284311c0179488a0644a13668317fb7eaf9434d6b1e3ceb16`
- Fields permitted: `blueprint/{blueprint.yaml,db_schema.json,share_tools.py,products/*.yaml}`, the extended charter, `task_tools.py`, and the masked views `0.view.json` (sha256 a89bada0…abfa1) and `1.view.json` (sha256 966fa474…bbb). The views hold `frozen_time`, `user_scenario` and `initial_state` only. The DSL semantics come from `skills/erl-task-instantiate/scripts/check_compute.py::build_env`, which is the evaluator the gates use.
- Fields masked (unread until every task's derivation was frozen): `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`, the difficulty `worklog.md`, and all other scratchpad files.
- Entry conditions (Step 0): the gate snapshot arrived with the brief, and all 7 instantiation gates were green (extended, task-tool contract, replay, solvability, compute, grounding, scope). `check_traceability` was deferred until the KB is published. The masked views and their hashes were supplied. Input complete.
- Base copy: `head -2086` of the extended charter is byte-identical to `blueprint/products/home.yaml`. Only the four-line banner comment and `extended_policies` are added after it.

### policy_conflict_scan

Five extended policies, all `computes: amount`, `subject: [home_claim_payment]`:

| policy | trigger | target_tool (owner) | object written |
| --- | --- | --- | --- |
| home_ext_roof_denial_reversal | state_due | settle_denied_roof_surfacing_b6cb399f (agent) | dwelling / roof_surfacing payment that replaces a below_deductible denial |
| home_ext_structure_supplemental | on_request | accept_structure_supplemental_c73fec14 (user) | other_structures / general `supplemental` |
| home_ext_water_denial_reversal | state_due | settle_denied_water_damage_028e176f (agent) | dwelling / general payment that replaces a repeated_seepage denial |
| home_ext_mold_denial_reversal | state_due | settle_denied_mold_remediation_0cacd0ff (agent) | mold / general payment that replaces a repeated_seepage denial |
| home_ext_contents_supplemental | on_request | accept_contents_supplemental_dc7651d7 (user) | personal_property / general `supplemental` |

- **Subjects and objects.** No two policies write the same (coverage_part, property_class, payment kind). Roof and water both write `coverage_part=dwelling` payment rows, but they replace different denial entries (`below_deductible` roof_surfacing vs `repeated_seepage` general), so their objects stay disjoint.
- **Claim identity.** All five take "the latest first-notice entry on the policy" (`LATEST(... event_type='home_claim_reported', date_field='entry_date')`). They agree.
- **Occurrence deductible.** All five define it identically: wind_hail → max(pct × Coverage A, tier minimum), else the AOP deductible. They split it differently: roof takes `MN(occ, covered)`; structure takes `occ − Σ dwelling deductible_applied`; water takes `MN(occ − single-event credit, covered)`; mold takes none; contents takes `0 if Σ dwelling deductible_applied > 0 else MN(occ, rc_pp)`. These are compatible in the two task worlds (see each task file). Two cross-policy tensions are recorded under findings G-3 and G-4.
- **Waiver threshold.** Roof, structure and water add "RC on the claim's payment entries + RC on its denial entries". After a reversal, the denial row stays and the new payment row copies its RC, so the reversed part is counted twice (see G-5). Contents has no waiver sentence at all (G-4).
- **Cross-category read boundaries.** Structure reads `flood` history (`XCOUNT flood_claims flood_claim_payment loss_date=`). Water reads `dwelling` history (`XCOUNT/XSUM dwelling_claims dwelling_claim_payment`). Contents reads the `dwelling` holding (`CFIELD status/original_effective_date`). Roof and mold declare `cross_category: []` and their compute uses no X*/C* call. The declarations match the compute.
- **Scope exclusivity (structural, pre-reveal).** The prerequisite graph has two weakly connected components: {structure ← roof} and {contents ← water, contents ← mold}. The solvability snapshot reports trees of 2 and 3 problems, which is consistent with task 0 = {structure, roof} and task 1 = {contents, water, mold}. That split is disjoint and covers all five policies. It is confirmed against `charter_scope` only after the reveal, in the task files.

### rule_compute_equivalence

Every binding's `compute_basis` quotation is a verbatim substring of the policy's own `rule` (swept for all five policies). Every factor-ladder tier appears both as a rule sentence and as a branch of its `decides` binding. Details per policy:

- **Roof.** `covered` has three branches: the schedule (age > tier RC age AND material not exempt), full RC (within age OR exempt, AND RC ≤ no-holdback), and ACV. These match rule sentences 8–10. `schedule_pct` has 8 bands, matching rule sentence 11. `code_pct` 10/5/0 and `tearoff_pct` 8/5/0 match. `prior_deduction` has two tiers plus 0, matching. `result` is floored and rounded once, with the allowances added and the deduction taken before the floor, matching the last two sentences. Small asymmetry: `prior_standing` subtracts the current claim's withheld rows but not its released or forfeited rows. This is harmless when the current claim has no roof holdback rows (true in task 0). `prior_forfeited > 0` is tested over the aggregate of all earlier claims rather than per claim; the rule says "on it", i.e. per earlier claim. The two readings coincide when only one earlier roof claim is in the window (true in task 0). Observation only.
- **Structure.** Every binding is quoted. `job_trades` counts acv_initial + replacement_cost_full + actual_cash_value_final + roof_schedule payment entries on the claim, plus the customer's same-loss-date `flood_claim_payment` rows, exactly as the rule lists. `tenure_credit` middle tier is 60–179 months, matching the rule.
- **Water.** `dep_recognized` HO-5 = dep × (100−55)/100 and HO-3 = MN(dep, 40% RC), matching the rule. The `drying_pct` day boundaries (≤2, 3–7) and `access_pct` (freeze ≥10,000 → 6; freeze <10,000 or sudden → 3) match.
- **Mold.** `prior_water_paid` counts payment rows with the four water perils in the 36-month loss-date window, minus all payment rows on the current claim. That equals "on another claim" whenever every current-claim payment carries a water peril, which holds inside the policy's own scope (freeze / sudden discharge). The hazmat year tests (<1978, <1990) match. The cap `MN(…, mold_limit − mold paid on policy with loss_date in 12 months)` matches.
- **Contents.** Two empty compute conditions have no rule basis. `disposal_pct` also requires `disposal_rc > 0`, and `packout_pct` returns 0 when dwelling payment entries exist but carry RC 0.00. The rule states neither. Both are inert: the allowance is a percentage of `rc_pp`, and `rc_pp > 0` whenever a contents ACV entry stands. Observation. `first_release_date` is named "first" but computed with `LATEST`, which matches the rule's "latest documented contents replacement". The name is misleading; the semantics are equivalent.

Conclusion: no rule sentence is left unimplemented and no compute branch lacks a basis in its rule. No SOURCE-POLICY finding arises from check 2.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (the five tools are distinct).
- uuid8s: `b6cb399f`, `c73fec14`, `028e176f`, `0cacd0ff`, `dc7651d7`. They share no prefix or suffix, are not sequential, and are not adjacent hex values. Nothing suggests batch derivation.
- Docstrings: none names another tool, a sequence position or an ordering word. The only "first" hits are the noun "first-notice entry". The docstrings add no confirmation, review or wait.
- Tool bodies (read in full) write rows unconditionally. They never read a prerequisite state, never refuse and never hint. The two denial-replacing tools copy the denial's `replacement_cost_amount` (roof also copies `depreciation_amount`) onto the new payment row. The water tool withholds `depreciation_withheld` when `acv_initial`. The roof tool withholds the denial's depreciation when `acv_initial`. The mold tool never withholds and records `depreciation_amount=0.0`. The two accept tools write `supplemental` rows with RC/dep/deductible 0.00.
- Observation: the mold rule says the payment is "acv_initial otherwise, with nothing withheld when no depreciation is recorded", which implies a holdback when depreciation *is* recorded. The mold tool can never withhold. This is inert whenever the mold denial carries depreciation 0.00, which holds in task 1.

### prerequisite_graph

| blocked policy | problem | kind | gate (binding exists?) | form | resolved_by = problem's target_tool? |
| --- | --- | --- | --- | --- | --- |
| structure_supplemental | roof_denial_reversal | value_input | `dw_abs` (yes) | state | yes |
| contents_supplemental | water_denial_reversal | value_input | `dw_abs` (yes) | state | yes |
| contents_supplemental | mold_denial_reversal | value_input | `mold_entries` (yes) | state | yes |

- Roof, water and mold have `prerequisite: []`. Every `problem` names another extended policy in this file, never a base policy or itself. The graph is two in-trees of depth 1 and is acyclic.
- Each `policy_source` is locatable verbatim in the blocked policy's own `rule` (structure rule sentence 7; contents rule sentences 4 and 5).
- `form: state` on all three edges and no `fallback_reason` anywhere, which is consistent.
- `condition` vs sentence. Structure: the condition parenthetically adds "(the reversal payment on the roof surfacing included)". That is a narrowing illustration, not a strengthening, because the sentence's "dwelling payment entries" already includes that row. Contents/water: the condition restates the sentence (freeze / sudden discharge; dwelling payment rather than only a seepage denial). Contents/mold: likewise.
- `effect` statements were verified against the compute and the tool effects. The roof write adds a dwelling row with `deductible_applied` > 0 and a `roof_schedule` / `replacement_cost_full` / `acv_initial` first-settlement row, which moves `dw_abs` and `job_trades`. The water write adds a dwelling row with deductible and RC, which moves `pp_ded` (via `dw_abs`) and `packout_pct`. The mold write adds a mold payment row, which moves `mold_entries`.
- No authoring-viewpoint phrasing ("in this task", "at the opening") appears in any `prerequisite` field.

### prerequisite_sentences

Four-point test:

1. Structure: "The other-structures supplemental figure is fixed only after the dwelling payment entries of the same claim carry the deductible the dwelling absorbs."
   - Connective "only after" ✓.
   - State: dwelling payment entries carrying `deductible_applied`, which is record-visible and uses the finder's own words ✓.
   - No tool, id or snake_case ✓.
   - Strength matches the condition ✓.
   - Derivation: the reader sees that the claim's dwelling damage stands only as a roof_surfacing `below_deductible` denial. No dwelling payment entry exists, so the waited-on state is false. Among the other rules, the roof rule re-settles exactly that denial and writes a dwelling payment carrying "the deductible the roof surfacing absorbs". Hence the hop goes to the roof reversal.
2. Contents/water: "The personal property supplemental is not fixed until the dwelling water damage of the same claim carries a payment entry wherever the claim's first notice records a freeze or a sudden discharge of water."
   - "not … until" ✓, state form ✓, no tool name ✓.
   - Derivation: on a freeze claim whose dwelling damage stands only as a repeated_seepage denial, the water rule is the one that replaces that denial with a dwelling payment. The hop is single.
3. Contents/mold: the parallel sentence for "the mold remediation … carries a payment entry". The mold rule is the only rule writing a mold payment. The hop is single.

Further checks:
- The depended-on rules (roof, water, mold) restate none of these sentences and do not mention the dependents.
- No rule names another problem's tool or policy id.
- Base-rule order sentence: home_claim_settlement's "Roof surfacing of a wind or hail claim is settled under home_roof_settlement and water losses under home_water_limitations before this arithmetic is applied." No task tree rests on it, because both trees are grounded by extended prerequisite sentences. Observation only.
- Two-writer observation, **G-6** (full entry under findings).

### override_declarations

Swept sentence by sentence against `base_policy_refs` = [home_claim_settlement, home_roof_settlement, home_water_limitations, home_depreciation_recovery], which is the same for all five policies.

- **home_claim_settlement.** The "one deductible … absorbed first by dwelling, then other_structures, then personal_property, until used up" sentence is superseded only by structure. Roof follows it (dwelling first; `MN(occ, covered)` equals the base amount when no earlier dwelling payment absorbed any). Water replaces the dwelling's share by "occurrence deductible less the single-event credit"; this is declared, via the superseded water_limitations AOP sentence. Mold absorbs none; declared, and mold is not in the base order list anyway. **Contents** replaces "until used up" with "the contents absorb no deductible once any dwelling payment entry of the claim carries a deductible". Its overwrite list names only the RC/ACV clause, so **the contents deviation is undeclared (G-3)**.
- **Waiver sentence** ("total covered RC of the occurrence … at or above deductible_waiver_threshold … no deductible applies"). Roof, structure and water re-express it as "RC on payment + denial entries", which diverges from base after a reversal (double count, G-5). Contents has no waiver sentence and applies `MN(occ, rc_pp)` even on a waiver tier when no dwelling payment carries a deductible. That is an undeclared departure (part of G-4).
- **below_deductible sentence.** The reversal policies floor at 0.00 rather than denying. Inert in both worlds.
- **RC/ACV clause.** Superseded and declared by all five.
- **Payee sentence.** Roof, water and structure follow it ("payee follows the claim settlement payee rule"). Mold and contents say "insured alone" because the co-payee rule reaches only dwelling/OS, which is consistent with base.
- **Special-limit cap sentence.** Not engaged.
- **home_roof_settlement.** Both roof_settlement-based clauses are superseded and declared. The replaced_by text for the schedule clause is an allowance sentence that does not address the schedule's subject. The merged semantics are still unique, because the extended rule alone decides schedule vs RC vs ACV by roof age / tier / material and never reads `roof_settlement`. Observation. The base roof-age formula (calendar year of loss − install year) equals the extended "whole years from 1 January of the install year to the date of loss" for every date, so it is not an override. "Roof surfacing damage from wind or hail" is not restated in the extended roof rule's scope. That is inert in task 0 (wind_hail).
- **Parameter schema.** `roof_rc_max_age_years` is defined "at the policy term effective date". The extended rule compares the age "at the date of loss" and does not declare this. Inert in task 0: age 17 at both 2026-04-15 and 2026-06-22. Observation.
- **home_water_limitations.** The AOP clause is superseded by water (declared). The mold sublimit clause is superseded by mold (declared; 12-month window replaces the per-term measure). "Holdback applies to … mold payments exactly as to dwelling": mold's amount formula never subtracts depreciation, and its RC/ACV-clause override covers it. Inert when mold dep = 0.
- **home_depreciation_recovery.** Structure and contents use "smaller of RC and largest documented incurred cost on the releases" as the settled basis once a release stands. This is coherent with the base release formula: min(incurred, RC) − ACV is exactly what the release pays on top of ACV. No conflict.

### factor_ladders

| policy | factor | effect | decides | tiers | multi-source tier(s) | cross_difficulty | label honest? | ladder real? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| roof | roof_basis_method | method | covered | 3 | yes (roof age × tier age × material; RC × threshold) | — | yes (×schedule% / full RC / RC−dep are different algorithms) | yes |
| roof | roof_schedule_band | parameter | schedule_pct | 8 | no (age only) | — | yes | yes |
| roof | roof_code_upgrade | parameter | code_pct | 3 | yes (dwelling age × tier OL%) | — | yes | yes |
| roof | roof_tearoff_disposal | parameter | tearoff_pct | 3 | tier 2 yes (material × RC) | — | yes | yes (see O-4) |
| roof | prior_unrepaired_roof | parameter | prior_deduction | 3 | yes (payment rows × forfeiture/withheld rows) | — | borderline (tiers pick different summed quantities; O-3) | yes (O-3) |
| structure | structure_settlement_method | method | settled_basis | 3 | tier 2 yes (RC × threshold × release rows) | — | yes | yes |
| structure | storm_job_overhead_profit | parameter | op_pct | 3 | yes (home payment rows + flood payment rows) | flood | yes | yes (O-5) |
| structure | structure_permit_allowance | parameter | permit_pct | 3 | no (RC only) | — | yes | yes |
| structure | structure_haul_away | parameter | haul_pct | 3 | yes (peril × dep/RC) | — | yes | fall-through doubtful (O-6) |
| structure | member_tenure_credit | parameter | tenure_credit | 3 | yes (policy date × claim count) | — | yes | doubtful (O-7) |
| water | single_event_deductible_credit | parameter | event_credit | 3 | yes (LandlordGuard payment count × deductible) | dwelling | borderline (O-3) | yes |
| water | water_depreciation_convention | method | dep_recognized | 3 | yes (form × RC threshold) | — | yes (share vs cap vs as-is) | yes |
| water | water_drying_allowance | parameter | drying_pct | 3 | yes (peril × report days) | — | yes | **no: the peril conjunct restates the policy scope (G-2)** |
| water | water_access_tearout | parameter | access_pct | 3 | yes (peril × RC) | — | yes | **no: fall-through unreachable within scope (G-2)** |
| mold | mold_containment_scope | method | containment_factor | 3 | yes (earlier paid water rows × RC) | — | **no: multiplier only (G-1)** | tier 2 doubtful (O-8) |
| mold | mold_clearance_testing | parameter | clearance_fee | 3 | no | — | yes | yes |
| mold | mold_duct_cleaning | parameter | duct_fee | 3 | yes (peril × RC) | — | yes | **no: fall-through unreachable within scope (G-2)** |
| mold | mold_hazmat_survey | parameter | hazmat_fee | 3 | no (year built) | — | yes | yes |
| contents | contents_settlement_method | method | pp_basis | 3 | tier 2 yes | — | yes | yes |
| contents | contents_cleaning | parameter | cleaning_pct | 3 | yes (mold payment rows × contents RC) | — | yes | yes |
| contents | contents_packout | parameter | packout_pct | 3 | yes (dwelling payment count × RC) | — | yes | yes |
| contents | contents_prompt_replacement | parameter | prompt_pct | 3 | yes (ACV entry date × release date) | — | yes | doubtful (O-9) |
| contents | contents_companion_line | parameter | companion_pct | 3 | yes (LandlordGuard status × first-effective date) | dwelling | yes | **no: the condition is not one a carrier weighs when settling contents (G-7)** |
| contents | contents_disposal | parameter | disposal_pct | 3 | no (peril only) | — | yes | fall-through doubtful (O-6) |

Checks that hold across all 24 factors:
- Bindings are disjoint within each policy.
- No factor `decides: result`.
- Every tier is stated in the rule, with its condition and value or method, and is implemented in compute.
- No two tiers of one ladder share a value.
- Every fall-through equals the factor's `baseline`, and every `baseline` is the fall-through.
- Every value is drawn from the policy's `params`.

**Declared counts per computation:**
- roof: 5 = 1 method + 4 parameter
- structure: 5 = 1 + 4
- water: 4 = 1 + 3
- mold: 4 = 1 + 3
- contents: 6 = 1 + 5

**Cross-difficulty factors:** storm_job_overhead_profit (flood), single_event_deductible_credit (dwelling history), contents_companion_line (dwelling holding).

**Counts after the tests strike factors out (G-1, G-2, G-7):**
- mold: containment is not an honest `method`, and duct is an unreal ladder. That leaves 2 parameter factors plus containment as a de-facto parameter, i.e. 3, with **0 method**. Mold fails "≥4 factors, ≥1 method".
- water: drying and access are struck, leaving **2** (credit, depreciation convention). Water fails "≥4 factors".
- contents: companion is struck, leaving 5 = 1 method + 4 parameter. Contents still passes the count, but loses one of task 1's two cross-difficulty factors. The water credit remains.
- roof and structure: counts unaffected.

**baseline.rule self-sufficiency:**
- roof: a definite number from its seven sentences ✓.
- structure ✓.
- mold: "the fees are added" names no fee, so a baseline reader adds none; definite ✓.
- contents ✓.
- water: uses "the deductible left for it", whose defining sentence ("…occurrence deductible less the single-event credit") is not in `baseline.rule`. A reader falls back on the base notion, dwelling first, so the full occurrence deductible. That is definite through the base charter, and the reliance is recorded as O-10. Water `baseline.params` omits `wind_hail_deductible_minimum` although its occurrence-deductible sentence uses it; inert on non-wind perils (O-10).

### findings

Charter-global, pre-reveal. Each names the tasks whose files carry the demonstration.

- **G-1 — SOURCE-FACTOR RED (structural; bears on task 1).**
  - Symptom: `mold_containment_scope` is labelled `method`, but its tiers only change a multiplier.
  - Evidence: `remediation: "mold_rc * containment_factor"`; `containment_factor: "K('containment_factor_repeat') if … else (K('containment_factor_single') if … else K('containment_factor_standard'))"` with params 1.15 / 1.05 / 1.0.
  - Root cause: all three tiers compute the same formula `mold_rc × k`, selecting only k. That is a `parameter` by the skill's definition ("a factor labelled method whose tiers only substitute a different number into the same formula"). The rule's words "re-scoped to full containment" and "for post-remediation verification" do not change the algorithm.
  - Consequence: the mold computation has no honest `method` factor. Task 1's file demonstrates this on its world.
  - Location: extended.yaml, `home_ext_mold_denial_reversal.factors[0]`, `compute.remediation/containment_factor`.
- **G-2 — SOURCE-FACTOR RED (structural; bears on task 1).**
  - Symptom: three ladders use a peril conjunct that holds for every customer who can reach the write.
  - Evidence (scope): the water rule sentence 1 reads "…when the claim's first notice records a freeze or a sudden and accidental discharge of water while the dwelling damage stands … only as a repeated-seepage denial entry…". The mold rule sentence 1 has the same scope.
  - Evidence (ladders):
    - `water_access_tearout`: "6 percent for a freeze loss … at least 10,000.00, 3 percent for a freeze or sudden discharge loss below that value or for a sudden discharge loss of any size, and none for any other cause of loss". Every in-scope customer lands on tier 1 or 2, so the fall-through (the baseline 0) is unreachable and the ladder has two real tiers.
    - `mold_duct_cleaning`: "450.00 when … at least 4,000.00, 200.00 when … below 4,000.00, and nothing for any other cause of loss". Same shape: the fall-through is unreachable.
    - `water_drying_allowance`: the "freeze or sudden discharge" conjunct of tiers 1 and 2 restates scope. The ladder still divides customers by report days, so three tiers stay reachable (the milder form of the same shape).
  - Consequence: under the skill's test ("each part of a compound condition taken on its own … not one that holds of every customer who reaches this write"), these three are struck. Water then has 2 surviving factors (< 4); mold falls below 4 together with G-1. Demonstrated in task 1.
  - Location: extended.yaml, `home_ext_water_denial_reversal.factors[2,3]` and `home_ext_mold_denial_reversal.factors[2]`, with their rule sentences.
- **G-3 — SOURCE-POLICY (undeclared override; bears on task 1).**
  - Symptom: the contents rule says "A dwelling part that is paid has already absorbed the whole deductible left to it, so the contents absorb no deductible once any dwelling payment entry of the claim carries a deductible". Base home_claim_settlement says "One deductible applies per occurrence … it is absorbed first by dwelling, then other_structures, then personal_property, until used up."
  - Root cause: `home_ext_contents_supplemental.overwrite` names only the RC/ACV clause, so the "until used up" sentence stays in force for contents. The extended sentence gives 0 whenever the dwelling carries any deductible, even when it carries less than the occurrence deductible.
  - Consequence: task 1's file demonstrates the second value.
  - Location: extended.yaml, contents `rule` sentence 6, `compute.pp_ded`, `overwrite`.
- **G-4 — Observation (no demonstrable consequence in either world).**
  - The contents deductible sentence conflicts with the water rule's "One freeze or storm event is borne under one deductible across the customer's Larkspur property policies" in the case where the LandlordGuard deductible is at or above the occurrence deductible. There the water payment carries `deductible_applied` 0.00, so contents fall back to `MN(occ, rc_pp)` and the event bears the deductible twice.
  - Contents also has no waiver sentence. On a waiver tier, contents absorb a deductible whenever no dwelling payment carries one.
  - Neither case arises in task 1 (credit 1,000 < occ 2,500; tier waiver 0).
- **G-5 — Observation.**
  - After a denial reversal, the waiver sums (roof `occ_rc`, structure `occ_rc_total`, water `occ_rc_sum`) count the reversed part twice: the denial row stays and the new payment row copies its RC.
  - Base measures "total covered RC of the occurrence".
  - No flip in task 0 (55,100 vs 100,000). Task 1's tier waiver is 0.
- **G-6 — Observation (two-writer state).**
  - The structure sentence's state ("dwelling payment entries … carry the deductible the dwelling absorbs") can be brought about by two writes of this difficulty: `settle_denied_roof_surfacing_b6cb399f` and `settle_denied_water_damage_028e176f`. Both write dwelling payment rows with `deductible_applied`.
  - Likewise, the contents computational sentence "once any dwelling payment entry of the claim carries a deductible" is satisfied by either.
  - In each task world only one of the two rules' scope sentences holds: the water rule needs a freeze / sudden-discharge first notice plus a repeated_seepage dwelling denial; the roof rule needs a below_deductible roof_surfacing denial. So the reader resolves the hop from the depended-on rules' scope and the records. The consequence ("reader cannot resolve the hop") is not demonstrable in task 0 or task 1, so this is recorded as an observation naming both candidate writes.
- **G-7 — SOURCE-FACTOR RED (ladder realism; bears on task 1).**
  - Symptom: `contents_companion_line` adds 2% / 1% of contents RC to a contents claim payment because the customer "also insures a rental building under LandlordGuard". The tiers depend on that policy being in force and on its tenure.
  - Root cause: whether the insured holds an unrelated landlord policy is not a condition a homeowners carrier weighs when settling the indemnity owed on the insured's own contents. Multi-policy relationships are priced in premium (bundle discounts). Same-event deductible coordination is a different thing, which this charter already models in the water credit. A contents payment that varies with ownership of another policy is not a treatment a carrier would publish.
  - Consequence: the factor is struck. Contents keeps 5 factors, but task 1 is left with a single cross-difficulty factor (the water credit).
  - Location: extended.yaml, contents `factors[4]` and rule sentence 12.
- **O-3.** `prior_unrepaired_roof` and `single_event_deductible_credit` are labelled `parameter`, but their tiers select differently aggregated quantities (paid vs paid + standing holdback; whole occurrence deductible vs the LandlordGuard deductible carried), not constants. This is a borderline label. Also, deducting a *standing* (unpaid, still releasable) holdback in roof tier 2 treats money never paid as paid. Task 0 sits on tier 1. Observation.
- **O-4.** Roof tear-off: "none for … an asphalt roof below [10,000.00]" invents a size threshold for a cost every asphalt tear-off incurs. Task 0 is on the 5% tier. Observation.
- **O-5.** O&P: industry practice is typically 10% + 10% once three or more trades are involved; the "exactly two → 5%" tier and counting payment entries as "trades" are stylised. Observation.
- **O-6.** `structure_haul_away` and `contents_disposal` pay nothing "for any other cause of loss". Fire or smoke debris removal is ordinarily covered for every covered peril, so these fall-throughs are doubtful treatments. Task 0 is on haul-away tier 1 and task 1 on disposal tier 2. Observation.
- **O-7.** The member-tenure dollar credit on a claim supplemental resembles marketed deductible-reward programmes, so it is plausible but stylised. Observation.
- **O-8.** Mold containment tier 2 multiplies by 1.05 "for post-remediation verification", while `mold_clearance_testing` separately adds a clearance testing fee. In remediation practice these are largely the same service, which would pay for it twice. Task 1 sits on tier 1. Observation.
- **O-9.** A "prompt replacement allowance" (a percentage bonus for replacing contents quickly) is not a common carrier treatment; the RC holdback release itself is the incentive. Observation.
- **O-10.** Water `baseline.rule` relies on "the deductible left for it", which is undefined within the baseline (see factor_ladders). Water `baseline.params` omits `wind_hail_deductible_minimum`. Observation.
- **O-11.** The mold rule implies a holdback on acv_initial when depreciation is recorded; the mold tool can never withhold (see action_binding_and_uuids). Observation.
- **O-12.** Contents `disposal_rc > 0` and the packout RC-0 edge are compute conditions with no rule basis. Both are inert. Observation.

## closing_checklist

Written after both reveals (2026-09-24T23:50Z sandbox clock). The pre-reveal section above is left untouched. **The difficulty does not close**, because not all four relationships PASS for both tasks.

| task | policy self-consistency | problem tree | factors | unique solution | overall |
| --- | --- | --- | --- | --- | --- |
| 0 | SOURCE-POLICY RED (T0-R1) | PASS | PASS (observations) | PASS | **SOURCE-POLICY RED** |
| 1 | SOURCE-POLICY RED (T1-R1) | PASS | SOURCE-FACTOR RED (T1-R2, T1-R3) | SOURCE-TASK RED (from T1-R1) | **SOURCE-POLICY + SOURCE-FACTOR + SOURCE-TASK RED** |

Post-reveal changes to charter-global findings. These are appended here; the pre-reveal text stands as written.
- **G-6 is upgraded from observation to SOURCE-POLICY RED**, demonstrated in `0.md` as T0-R1. Task 0's `design_rationale` asserts "the roof reversal is the only extended policy whose target tool writes a dwelling payment entry". But `settle_denied_water_damage_028e176f` writes `coverage_part="dwelling"` payment rows carrying `deductible_applied` (task_tools.py lines 156–162). The single-writer proof for the structure edge is false. Task 0's scored values are unaffected.
- **G-3 is confirmed** by task 1's own `design_rationale`, which asserts the contents deductible change is declared. The contents `overwrite` does not name the base absorption-order sentence.

Checklist status:
- [x] Per-task files `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`, with `_difficulty.md` alongside. This is the first revision, so no older revision exists.
- [ ] Every comparison section carries a PASS. It does not; see the verdict table.
- [x] The extended policies are fully covered and the scopes are pairwise disjoint (confirmed against `charter_scope`: task 0 = {roof, structure}; task 1 = {water, mold, contents}). Task tools and GT are closed, and the five uuid8s were generated independently.
- [x] Each tree has 1 or 2 prerequisite problems and ≥ max(n − 1, 1) `value_input` edges (task 0: 1 of 1; task 1: 2 of 2). Each has an `owner=user` root. The whole-difficulty graph is acyclic.
- [ ] Every computation has 4–6 surviving factors with ≥ 2 parameter and ≥ 1 method, every ladder real, and honest labels. This fails for water (2 survive) and mold (3 survive, 0 method) per G-1 and G-2, and contents' companion-line ladder is unreal (G-7). Roof and structure pass. Every declared factor bears weight against an honest baseline on its task world, and every all-baseline number is definite and differs from gold.
- [ ] Re-run of the instantiation-stage gates on the final form: not performed. The difficulty does not close, and a re-run belongs to the round that closes it.

## revision_2

### charter_global_frozen (revision 2)

- Auditor: the same independent erl-task-policy-audit agent that did round 1. Re-audit round 2, written 2026-09-25T00:10Z. This section was written **before** either round-2 task GT was revealed.
- Round-1 text above is preserved unchanged. Round-1 file hashes at the start of round 2: `_difficulty.md` 20f3a041…c6bf6, `0.md` 66095e8d…6bf6, `1.md` 6b23d192…24af.
- Shared inputs changed, so every charter-global section is **re-derived in full**, not carried forward:
  - `home.extended.yaml`: round 1 `9a5d153f…4c8c` → round 2 `ba33187af7922105c99509623f65f4927bba5f8e5115b6a5c5c11c61064061c2`;
  - `task_tools.py`: round 1 `c40f08d8…b16` → round 2 `6feaa40e763971df9b51848c46f7d016c6efba3625bc7484bb88161962d1c8f6`.
  - Both were verified on disk and match the orchestrator's brief.
- The base section (first 2,086 lines) is still byte-identical to `blueprint/products/home.yaml`.
- Masked views: `0.view.json` 00d2ea6a…6c0e and `1.view.json` d70b9d4e…550e, both verified. Whitelist: `frozen_time`, `user_scenario`, `initial_state`.
- Entry conditions: the round-2 gate snapshot (all 7 green; traceability deferred) and the view hashes were supplied. Input complete.
- contamination_disclosure (charter level): the auditor read the full round-1 `tasks/0.json` and `tasks/1.json` in round 1, after the round-1 freeze. This revision's charter-global section rests only on the round-2 charter, the tools and the schema. The per-task consequences of that earlier exposure are disclosed in each task file.

### policy_conflict_scan (revision 2)

The five policies, targets, owners and triggers are as in round 1. What changed:

- **Roof**
  - Scope now reads "the wind or hail roof surfacing damage", matching base home_roof_settlement.
  - The waiver sum now counts "denial entries and … payment entries that replace no denial" (compute `source_entry_id=''`).
  - Tear-off gives its reasons.
  - `prior_standing` now nets the current claim's withheld, released and forfeited rows alike.
  - The overwrite `replaced_by` texts now restate the subject they replace.
- **Structure**
  - Prerequisite sentence is now "…fixed only after the roof surfacing of the same claim carries a payment entry wherever that roof surfacing was denied below the deductible."
  - Waiver uses the no-denial-replaced sum.
  - Haul-away ladder is now by depreciation share only (≥25 → 4; 10–25 → 2; <10 → 0).
- **Water**
  - Drying ladder has no peril conjunct.
  - Access ladder is freeze ≥10,000 → 6; freeze <10,000 → 3; sudden discharge → 0.
  - New `water_plumbing_code_upgrade` (built before 1980 × tier OL%) and `water_hazmat_survey`, the latter moved from mold.
  - The baseline now states "Before any single-event credit, the deductible left … is the whole occurrence deductible."
  - The single-event sentence opens "A freeze or sudden discharge that strikes the customer's home and a rental building the customer insures under LandlordGuard on the same date of loss is borne under one deductible".
- **Mold**
  - Containment is now additive: + 10% of the claim's wet area with an earlier paid water loss; + 400.00 barrier otherwise, when RC ≥ 3,000; as estimated below that.
  - New antimicrobial-category ladder (sudden → 8%; freeze reported >2 days → 4%; freeze ≤2 days → 0).
  - Duct ladder is now by wet area.
  - Hazmat moved to water.
  - Holdback override declared ("nothing is ever withheld on a mold payment").
- **Contents**
  - Declares an override of the whole base one-deductible sentence.
  - New deductible: `MX(0, MN(rc_pp, occ − same_event_share − dwelling deductible − OS deductible))`, with a waiver. The same-event share comes from same-date LandlordGuard payment deductibles on freeze or sudden-discharge losses.
  - Prompt-replacement and companion-line factors removed.
  - Disposal replaced by "saturated-contents handling".

Conflict checks after the rework:
- **Occurrence deductible across the five.** Roof takes `MN(occ, covered)`. Structure takes `occ − Σ dwelling deductible`. Water takes `MN(occ − credit, covered)`. Mold takes none. Contents takes `occ − share − Σ dwelling − Σ OS`. The water and contents rules use the same LandlordGuard-deductible figure (credit = `MN`-equivalent: whole occ when LG ≥ occ, else the LG deductible). Because water's `deductible_applied` is net of the credit, contents never re-charges the credited part and never charges the event twice. The round-1 tension G-4 case (LG ≥ occ) now gives water 0 and contents 0.
- **Waiver sums.** Roof, structure, water and contents now all use "denial entries + payment entries that replace no denial". The denial-replacing tools set `source_entry_id` (task_tools.py lines 61 and 164) and the mold tool does too (line 221), so a reversed part is counted once.
- **Cross-category reads.** Structure reads flood history. Water reads dwelling history (a factor). Contents reads dwelling history, a plain read declared as "not a factor". Roof and mold read none. Declarations match compute.
- **Scope exclusivity (structural):** unchanged; two components, {structure ← roof} and {contents ← water, mold}.

### rule_compute_equivalence (revision 2)

- All five policies were swept again. Every `compute_basis` value is a verbatim substring of its rule, and every ladder tier appears both in the rule and as a branch.
- New bindings checked:
  - roof `occ_rc` (no-denial-replaced filter) and roof `prior_standing` (current-claim netting);
  - structure `haul_pct`;
  - water `drying_pct`, `access_pct`, `plumbing_code_pct` (`MONTHS(year_built-01-01, 1980-01-01) > 0` = built before 1980), `hazmat_fee`;
  - mold `wet_area_rc`, `remediation`, `antimicrobial_pct`, `duct_fee`;
  - contents `same_event_share`, `pp_ded`, `packout_pct` (tier 2 now "a dwelling payment entry stands with a replacement-cost value below 10,000.00", matching compute), `wet_pct`.
- Round-1 O-12 is **closed**. The `disposal_rc > 0` condition is gone, and the pack-out RC-0 edge now falls in tier 2, as the rule says.
- **New observation R2-O1 (judgement call flagged by the reworker).** Water rule sentence 9 opens "A freeze or sudden discharge that strikes the customer's home **and a rental building** the customer insures under LandlordGuard on the same date of loss is borne under one deductible". Read with its lead-in, the credit covers a LandlordGuard loss from the same freeze or discharge. But the tier conditions ("where a LandlordGuard claim of the customer with the same date of loss carries a payment entry …") and the compute (`XCOUNT/XSUM … dwelling_claim_payment, loss_date=loss_date`) do not test the LandlordGuard claim's peril, although `dwelling_claims.peril` exists. Contents is the same: "For a freeze or sudden discharge loss …" is tested only on the home peril.
  - Consequence: a world with a same-date LandlordGuard wind/hail or fire payment and a home freeze claim would give credit X under compute and 0 under the lead-in reading.
  - Task 1's LandlordGuard claim `LGC-26-107715` is itself `peril=freeze`, so the readings coincide there and no consequence is demonstrable. Recorded as an observation.
  - My judgement on the call: the lead-in scopes the credit to the same event striking both buildings, so the narrower reading is the one the prose states. The compute is broader than the prose.

### action_binding_and_uuids (revision 2)

- The five `(target_tool, computes)` pairs are unique. uuid8s are unchanged and independent: `b6cb399f`, `c73fec14`, `028e176f`, `0cacd0ff`, `dc7651d7`.
- No docstring carries an ordering word (grep of before, after, then, prior, until, once: none). No tool names another tool.
- Tool bodies are unchanged in behaviour: unconditional writes, no refusal, no hint. The denial-replacing tools set `source_entry_id` to the denial; the accept tools set `""`.
- The mold docstring now says "remediation carries no depreciation, so nothing is ever withheld". That matches the mold rule and the new declared overwrite. **Round-1 O-11 closed.**

### prerequisite_graph (revision 2)

| blocked | problem | kind | gate | form | policy_source in own rule | resolved_by = target |
| --- | --- | --- | --- | --- | --- | --- |
| structure | roof | value_input | `dw_abs` (exists) | state | yes (rule sentence 7) | yes |
| contents | water | value_input | `dw_abs` (exists) | state | yes (sentence 4) | yes |
| contents | mold | value_input | `mold_entries` (exists) | state | yes (sentence 5) | yes |

- Roof, water and mold have `[]`. The graph is acyclic, and no edge points at a base policy or at itself.
- The structure `condition` now reads "Where the claim carries a below-deductible denial entry of dwelling roof surfacing, the claim also carries a dwelling roof surfacing home_claim_payment entry …". That is the same strength and scope as the sentence.
- `effect` statements match compute and tool effects. No authoring-viewpoint phrasing.

### prerequisite_sentences (revision 2)

- Structure: "The other-structures supplemental figure is fixed only after the roof surfacing of the same claim carries a payment entry wherever that roof surfacing was denied below the deductible."
  - Four-point test: connective "only after" ✓; state form, record-visible (a roof_surfacing payment entry on the claim; a below_deductible denial) ✓; no tool, id or snake_case ✓; scope and strength equal to the condition ✓.
  - **Single writer:** only `settle_denied_roof_surfacing_b6cb399f` writes `property_class="roof_surfacing"` payment rows (line 57). The water tool writes `property_class="general"` (line 160).
  - **Round-1 G-6 / T0-R1 closed at the sentence level.**
  - Residual observation R2-O2: the structure *compute* sentence "the other structures absorb what the occurrence deductible leaves after the deductible carried on the claim's dwelling payment entries" would also move under a water reversal on a freeze claim that has an OS part. No edge covers that case. No task world has it (task 0 is wind_hail).
- Contents/water and contents/mold sentences are unchanged and pass as in round 1. Single writers: the water tool is the only writer of a dwelling general payment replacing a repeated_seepage denial; the mold tool is the only writer of mold payments.
- The depended-on rules do not restate the sentences. No rule names another problem's tool or id.

### override_declarations (revision 2)

- **home_claim_settlement "One deductible … until used up".** Declared by structure (its absorption clause) and now by **contents** (the whole sentence). Roof follows it (dwelling first). Water's share is declared via the water_limitations AOP sentence. Mold absorbs none, declared. **Round-1 G-3 closed at the charter level.**
- **Waiver sentence** ("total covered RC of the occurrence"). All four re-expressions now count each part once: denials plus payments that replace no denial. A reversed part keeps its denial row and its payment row is excluded. **Round-1 G-5 closed.** Contents now has the waiver sentence (part of round-1 G-4, closed).
- **RC/ACV clause.** Superseded and declared by all five.
- **Payee sentence.** Followed. Mold and contents are insured-only, consistent with base.
- **home_roof_settlement.** Both roof_settlement-keyed clauses are superseded, and the `replaced_by` texts now restate the replacing subject (the schedule-percentage sentence and the age/material sentence). Round-1 observation on the replaced_by text closed. The roof age formula is equivalent to base. The wind/hail scope is now aligned.
- **Parameter-schema age anchor.** `roof_rc_max_age_years` is still "at the policy term effective date" in the schema and "at the date of loss" in the rule, undeclared. The reworker says this was kept. Observation.
- **home_water_limitations.** AOP sentence superseded by water (declared). Mold sublimit sentence superseded (declared). "Holdback applies to … mold payments" now superseded by mold (declared).
- **home_depreciation_recovery.** Consistent, as in round 1.

### factor_ladders (revision 2)

| policy | factor | effect | tiers | multi-source | cross_difficulty | label honest? | ladder real? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| roof | roof_basis_method | method | 3 | yes | — | yes | yes (task-world stamp issue: see task 0) |
| roof | roof_schedule_band | parameter | 8 | no | — | yes | yes |
| roof | roof_code_upgrade | parameter | 3 | yes | — | yes | yes |
| roof | roof_tearoff_disposal | parameter | 3 | tier 2 yes | — | yes | yes; reasons now given (O-4 closed) |
| roof | prior_unrepaired_roof | parameter | 3 | yes | — | borderline (O-3 kept) | yes |
| structure | structure_settlement_method | method | 3 | tier 2 yes | — | yes | yes |
| structure | storm_job_overhead_profit | parameter | 3 | yes | flood | yes | yes (O-5 kept) |
| structure | structure_permit_allowance | parameter | 3 | no | — | yes | yes |
| structure | structure_haul_away | parameter | 3 | no (dep and RC come from the same row) | — | yes | yes; the "any other cause → 0" fall-through is gone (O-6 closed for haul-away) |
| structure | member_tenure_credit | parameter | 3 | yes | — | yes | stylised (O-7 kept) |
| water | single_event_deductible_credit | parameter | 3 | yes | dwelling | borderline (O-3 kept) | yes (R2-O1) |
| water | water_depreciation_convention | method | 3 | yes | — | yes | yes |
| water | water_drying_allowance | parameter | 3 | no | — | yes | **yes: all three tiers reachable in scope, no peril conjunct** |
| water | water_access_tearout | parameter | 3 | tier 1/2 yes (peril × RC) | — | yes | **yes: fall-through (sudden discharge) reachable in scope**; realism note R2-O3 |
| water | water_plumbing_code_upgrade | parameter | 3 | yes (year built × tier OL) | — | yes | yes |
| water | water_hazmat_survey | parameter | 3 | no | — | yes | yes; tension R2-O4 |
| mold | mold_containment_scope | method | 3 | yes | — | **yes: tier 1 adds a second base (the wet area), tier 2 a flat barrier charge, tier 3 none. The algorithm, not a multiplier, differs** | yes |
| mold | mold_clearance_testing | parameter | 3 | no | — | yes | yes |
| mold | mold_antimicrobial_category | parameter | 3 | tier 2 yes (peril × report days) | — | yes | yes; peril is not constant within scope (freeze vs sudden). Stylised category mapping, R2-O3 |
| mold | mold_duct_cleaning | parameter | 3 | no | — | yes | **yes: by wet area, all tiers reachable** |
| contents | contents_settlement_method | method | 3 | tier 2 yes | — | yes | yes |
| contents | contents_cleaning | parameter | 3 | yes | — | yes | yes |
| contents | contents_packout | parameter | 3 | yes | — | yes | yes |
| contents | contents_saturated_handling | parameter | 3 | no | — | yes | yes; contents scope spans all perils, so every tier is reachable (O-6 closed for contents) |

- Counts:
  - roof: 5 = 1 method + 4 parameter;
  - structure: 5 = 1 + 4;
  - water: 6 = 1 + 5;
  - mold: 4 = 1 + 3;
  - contents: 4 = 1 + 3.
  - No factor is struck on structure grounds. **Round-1 G-1, G-2 and G-7 closed at the charter level.** Contents' companion-line factor is removed, and so is the prompt-replacement factor (O-9 closed). O-8 (PRV/clearance duplication) is closed: the 1.05 tier is gone.
- Every fall-through equals its `baseline`, and no two tiers share a value.
- Baselines:
  - water: `baseline.rule` is now self-sufficient ("Before any single-event credit …"), and `params` includes `wind_hail_deductible_minimum`. **O-10 closed.**
  - mold: remediation as estimated with no fees; definite.
  - contents: its baseline keeps the same-event share (a plain read); definite.
- Cross-difficulty factors: structure O&P (flood) and water single-event credit (dwelling).

### findings (revision 2, charter-global)

- Round-1 REDs: G-1 closed, G-2 closed, G-3 closed, G-6 closed (at the sentence level; single writer), G-7 closed. See the per-task files for the task-world confirmations.
- Round-1 observations: closed are G-4, G-5, O-4, O-6, O-8, O-9, O-10, O-11, O-12, the roof `replaced_by` text and the roof `prior_standing` sum. Kept are O-3, O-5, O-7, and the schema age anchor (the reworker says these were kept deliberately; they remain observations).
- **R2-O1 — Observation.** Same-date credit peril scope: the prose lead-in is narrower than the tiers and compute (see rule_compute_equivalence). No task world demonstrates it.
- **R2-O2 — Observation.** The structure deductible computation reads every dwelling payment deductible, not only the roof's. Only the roof edge is declared.
- **R2-O3 — Observation (stylised realism).** Water access pays 0 for every "sudden discharge", which the rule calls "from a fixture or appliance, which is reached without opening the building". But the `water_sudden_accidental` peril also covers bursts of concealed supply lines. Mold antimicrobial treats every sudden discharge as contaminated water, whereas IICRC classifies a clean supply-line discharge as Category 1. Neither is engaged in task 1 (freeze).
- **R2-O4 — Observation.** The water hazmat survey is "added before walls are opened" for every water reversal. Yet the access ladder says a sudden discharge is "reached without opening the building", so a sudden-discharge customer pays a pre-opening survey for walls that are not opened. Not engaged in task 1 (freeze).
- Stamp check, **per task world** (demonstrated in `0.md`, revision 2): `home_policies.roof_settlement` names the outcome of `roof_basis_method`'s schedule tier.

### closing_checklist (revision 2)

Written after the round-2 reveals. **The difficulty does not close**: task 0 carries a new SOURCE-FACTOR RED.

| task | policy self-consistency | problem tree | factors | unique solution | overall |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS (T0-R1 closed) | PASS | **SOURCE-FACTOR RED** (T0-R2-1, new; regression from the T0-O1 fix) | PASS | **SOURCE-FACTOR RED** |
| 1 | PASS (T1-R1 closed) | PASS | PASS (T1-R2 and T1-R3 closed) | PASS (closed) | **PASS** |

Closure of round-1 REDs:
- T0-R1 / G-6: closed.
- T1-R1 / G-3 and its SOURCE-TASK consequence: closed.
- G-4: closed.
- T1-R2 / G-1: closed.
- T1-R2 / G-2: closed.
- T1-R3 / G-7: closed.
- New RED: T0-R2-1 (stamp agreement, task 0).
- New observations: R2-O1 to R2-O4 and R2-T1-O1.

Checklist:
- [x] Per-task files map one-to-one to the tasks, with revision_2 appended and round 1 preserved.
- [ ] Every comparison carries a PASS. It does not: task 0 is RED.
- [x] Full coverage and disjoint scopes (`charter_scope`: {roof, structure} / {water, mold, contents}). Tools and GT are closed, and uuid8s are independent.
- [x] Trees have 1 or 2 prerequisites, value_input edges meet the floor, and each has a user-owned root. The graph is acyclic.
- [ ] Factor bounds on every computation. Every structure passes, but task 0's roof computation loses its only method factor on its world (T0-R2-1).
- [ ] Gate re-run on the final form: not performed. The difficulty does not close.

## revision_3

### charter_global_frozen (revision 3)

- Written 2026-09-25, **before** either round-3 task GT was revealed. Same auditor. Revisions 1 and 2 above are preserved unchanged. File hashes at the start of round 3: `_difficulty.md` d2690716…c76d, `0.md` dcfb3de0…cad4, `1.md` da574175…382f.
- Shared inputs:
  - `home.extended.yaml` changed: `ba33187a…61c2` → `fbd0a7c321c5f90c4f1ac488a894f04f80729cc103926cb0c67a499efd1909e8`. The charter-global sections are therefore re-derived below.
  - `task_tools.py` unchanged at `6feaa40e…f8c6`. The action_binding_and_uuids conclusions of revision 2 are carried forward on that hash.
  - The base section is still byte-identical to `blueprint/products/home.yaml`.
- Views unchanged since round 2: `0.view.json` 00d2ea6a…6c0e and `1.view.json` d70b9d4e…550e, both verified.
- contamination_disclosure (charter level): the auditor has read the round-1 and round-2 task JSONs, in each case after that round's freeze. This section rests only on the round-3 charter and the unchanged tools and schema.

### policy_conflict_scan (revision 3)

What changed since revision 2:

- **Roof (redesigned).**
  - The covered amount now "follows the roof surfacing settlement basis the declarations carry for the term": on the schedule, RC × band %; on replacement cost, full RC at or below the no-holdback threshold, else RC − depreciation. The band age is "the calendar year of the date of loss minus the roof install year", which is the base wording.
  - `roof_basis_method` and `roof_schedule_band` are removed as factors. Both the declarations basis and the band now sit in the baseline.
  - `prior_unrepaired_roof` is relabelled `method`.
  - New `roof_matching` (asphalt, by roof age: ≥20 → 10%; 10–19 → 5%; else 0) and `roof_emergency_tarp` (by report days: ≤3 → 450.00; 4–14 → 200.00; later 0).
  - The overwrite list now supersedes only the base schedule clause (replaced_by: the allowance sentence) and the RC/ACV clause. The base "When the policy's roof_settlement is replacement_cost, roof surfacing settles like the rest of the dwelling" clause is no longer superseded, and the extended rule now agrees with it (full RC ≤ threshold, else RC − dep with depreciation withheld).
- **Structure.** Scope narrowed to "the most recently reported wind or hail claim". Everything else as in revision 2.
- **Water.** The credit now requires "a LandlordGuard freeze or sudden-discharge claim" in the rule, the ladder and the compute (`peril='freeze'` / `'water_sudden_accidental'` on the XCOUNT/XSUM). The access rationale was rewritten. The hazmat rationale is now "because the wet walls, floors or ceilings of every reversed water loss are cut out".
- **Mold.** The antimicrobial ladder is now by report days only (>7 → 8%; 3–7 → 4%; ≤2 → 0; clean / grey / black water).
- **Contents.** The same-event share is now read only from "a LandlordGuard freeze or sudden-discharge claim" (compute peril-filtered).

Conflict checks:
- **Occurrence deductible.** Roof takes `MN(occ, covered)`, structure `occ − Σ dwelling`, water `MN(occ − credit, covered)`, mold none, contents `occ − share − Σ dwelling − Σ OS`. The water credit and the contents share now read the same peril-filtered LandlordGuard figure. No conflict.
- **Scope overlap.** Roof and structure are now both wind/hail-scoped; water and mold are freeze/sudden-scoped. So the dwelling deductible that the structure computation reads can only come from the roof reversal. **R2-O2 closed.**
- Contents stays unscoped by peril. Its deductible sentence ("after the deductible carried on the claim's dwelling … payment entries") would read a roof-reversal payment on a wind or hail claim, and no contents edge covers that case. See R3-O1.
- **Cross-category reads.** Unchanged in kind. The dwelling reads are now peril-filtered and still customer-scoped.
- **Scope exclusivity.** Two components, as before.

### rule_compute_equivalence (revision 3)

- All five policies re-swept: `compute_basis` quotes are verbatim in the rules, and every ladder tier appears in both faces.
- **Roof, new and changed bindings:**
  - `covered` (stamp-keyed basis) matches rule sentence 7.
  - `band_age` / `matching_age` (`MONTHS(install-01-01, loss)//12`) equal "calendar year of loss − install year" for every date. The rule states the matching age as "years old at the date of loss", which is the same.
  - `tarp_days` = `DAYS(loss_date, report_date)`, with ≤3 / 4–14 / later.
  - `matching_pct` asphalt test (3-tab or architectural).
  - The `result` terms add `matching_pct` and `tarp_fee`, matching the allowance sentence.
- **Water:** the credit peril filter matches "LandlordGuard freeze or sudden-discharge claim". **R2-O1 closed:** the prose, the tiers and the compute now agree on the narrower reading.
- **Mold:** `antimicrobial_pct` thresholds are 2 and 7 days, matching the rule.
- **Contents:** the `same_event_share` peril filter matches the rule.
- **R3-O3 — Observation.** The structure rule keeps "and the declarations' all-other-perils deductible for any other cause" although its scope is now wind or hail only. It is a dead branch and inert.

### action_binding_and_uuids (revision 3)

Carried forward on the unchanged `task_tools.py` hash `6feaa40e…f8c6` (revision-2 conclusions: unique pairs, independent uuid8s, no ordering words, no prerequisite judging). The roof tool docstring's `payment_type` wording ("roof_schedule when the roof surfacing is paid on the roof payment schedule percentage …") is consistent with the redesigned roof rule.

### prerequisite_graph and prerequisite_sentences (revision 3)

- Unchanged: structure ← roof (`value_input`, `dw_abs`, state); contents ← water (`value_input`, `dw_abs`, state); contents ← mold (`value_input`, `mold_entries`, state).
- Each `policy_source` is still verbatim in its own rule. The graph is acyclic. The four-point test passes as in revision 2.
- Single writers: roof-surfacing payments come only from the roof tool; the water dwelling general payment replacing a repeated_seepage denial only from the water tool; mold payments only from the mold tool.
- **R3-O1 — Observation.** On a wind or hail claim with a below-deductible roof denial and a contents ACV entry, the roof reversal would move the contents deductible (`dw_abs`). No contents prerequisite sentence names that state, and the contents deductible sentence carries no ordering connective. No task world has this: task 1 is a freeze claim with no roof denial.

### override_declarations (revision 3)

- **home_roof_settlement.**
  - The schedule clause is superseded and declared. The extended rule keeps its core (RC × band % less the deductible absorbed, nothing withheld: `roof_schedule`) and adds the allowances and the prior deduction.
  - The replacement_cost clause is **followed**, not superseded: RC ≤ threshold → full RC; otherwise acv_initial with depreciation withheld, as base home_claim_settlement does for dwelling.
  - The base roof-age formula is now used verbatim.
  - "roof_settlement changes only at binding, at renewal … never because of a claim" is respected: the rule reads the term's declared basis.
  - The schema age-anchor observation is **moot and closed**: the roof rule no longer uses `roof_rc_max_age_years`.
- **home_claim_settlement.** Unchanged from revision 2. The deductible-order overrides are declared by structure and contents, and the waiver re-expressions count each part once.
- **home_water_limitations** and **home_depreciation_recovery.** Unchanged from revision 2.
- No undeclared override found.

### factor_ladders (revision 3)

| policy | factor | effect | tiers | multi-source | cross_difficulty | label | ladder real? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| roof | prior_unrepaired_roof | **method** | 3 | yes (payment rows × forfeiture / withheld / released rows) | — | honest: tier 1 deducts one record quantity, tier 2 adds a second quantity (the standing holdback), tier 3 deducts nothing, so the composition of the deduction differs, not a constant. Same standard as mold containment in revision 2. **O-3 (roof) closed** | yes; the tier-2 rationale is now stated ("which the earlier claim may still pay") |
| roof | roof_code_upgrade | parameter | 3 | yes | — | yes | yes |
| roof | roof_tearoff_disposal | parameter | 3 | tier 2 yes | — | yes | yes |
| roof | roof_matching | parameter | 3 | tiers 1 and 2 yes (material × roof age) | — | yes | yes: matching of discontinued asphalt lines is a recognised settlement issue |
| roof | roof_emergency_tarp | parameter | 3 | no (report days) | — | yes | stylised; see R3-O2 |
| structure | (5 factors) | as revision 2 | | | flood (O&P) | | |
| water | (6 factors) | as revision 2; the credit ladder is now peril-scoped | | | dwelling (credit) | O-3 (credit label) kept | |
| mold | mold_antimicrobial_category | parameter | 3 | no (report days) | — | yes | yes: water category escalates with standing time. **R2-O3 (the sudden = contaminated mapping) closed** |
| mold | other three | as revision 2 | | | | | |
| contents | (4 factors) | as revision 2 | | | | | |

- Counts:
  - roof: 5 = 1 method + 4 parameter ✓;
  - structure: 5 = 1 + 4 ✓;
  - water: 6 = 1 + 5 ✓;
  - mold: 4 = 1 + 3 ✓;
  - contents: 4 = 1 + 3 ✓.
- Every fall-through equals its baseline, and no two tiers share a value.
- Roof `baseline.rule` is self-sufficient: declarations basis, band table, deductible, floor and rounding. Its `params` list the no-holdback threshold used by the replacement-cost branch ✓.
- **Stamps.** `home_policies.roof_settlement` is now a *baseline input* stated by the rule ("the roof surfacing settlement basis the declarations carry for the term"). It is no longer the outcome of any factor tier. No remaining factor's tier is named by a record field. Task-world confirmation is in `0.md` revision_3.
- **R2-O4 closed.** Hazmat is now justified for every reversed water loss (wet materials are cut out), and access excludes sudden discharge only because its tear-out "is already inside the replacement-cost value". The two are no longer in tension.
- **R3-O2 — Observation (stylised realism).**
  - `roof_emergency_tarp` pays by report delay alone ("450.00 when the loss was reported within 3 days, when the desk's emergency vendor tarps the roof at first notice"). No record shows that a tarp was placed or paid.
  - In practice, emergency-mitigation reimbursement follows the documented service, not the report interval.
  - The factor still bears weight and its tiers are distinct. Recorded as an observation.

### findings (revision 3, charter-global)

- **Round-2 RED T0-R2-1:** closed at the charter level. The stamp is now a declared baseline input, and no factor tier is stamp-named. Task-world confirmation is in `0.md` revision_3.
- **Round-2 observations:**

  | item | status |
  | --- | --- |
  | R2-O1 | closed (peril-scoped credit and share) |
  | R2-O2 | closed (structure scoped to wind or hail) |
  | R2-O3 | closed for mold; water access rationale rewritten, accepted |
  | R2-O4 | closed |
  | R2-T1-O1 | per task 1 file |
  | O-3 | closed for the roof; kept for the water credit label |
  | O-5, O-7 | kept |
  | schema age anchor | moot and closed |

- **New:** R3-O1 (a contents dw_abs dependency on a roof reversal in wind or hail worlds; undeclared, but no task world has it), R3-O2 (tarp keyed on report delay), R3-O3 (dead structure deductible branch). All are observations.

### closing_checklist (revision 3)

Written after the round-3 reveals. **All four relationships PASS for both tasks.**

| task | policy self-consistency | problem tree | factors | unique solution | overall |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS (T0-R2-1 closed) | PASS | **PASS** |
| 1 | PASS | PASS | PASS | PASS | **PASS** |

- Round-2 RED **T0-R2-1: closed.**
- Outstanding observations (not grounds for rework):

  | observation | where / note |
  | --- | --- |
  | R3-O1 | contents dw_abs vs a roof reversal in wind or hail worlds |
  | R3-O2 | tarp keyed on report delay |
  | R3-O3 | dead structure deductible branch |
  | R3-T0-O1 | stale overwrite description in task 0's `design_rationale` |
  | O-3 | water credit label |
  | O-5 | O&P stylisation |
  | O-7 | tenure credit |

Checklist:
- [x] Per-task files map one-to-one to the tasks. Revisions 1, 2 and 3 are appended; earlier text is preserved.
- [x] Every comparison section of revision 3 carries a PASS.
- [x] The extended policies are fully covered and the scopes are pairwise disjoint (`charter_scope`: {roof, structure} / {water, mold, contents}). Task tools and GT are closed, and the uuid8s are independent and frozen (`task_tools.py` unchanged since round 2).
- [x] Each tree has 1 or 2 prerequisite problems, all edges are `value_input` (≥ the floor), each root is owned by the user, and the difficulty graph is acyclic.
- [x] Every computation meets the factor bounds: 4–6 factors with ≥ 2 parameter and ≥ 1 method (roof 5, structure 5, water 6, mold 4, contents 4). Each task has ≥ 1 multi-source and ≥ 1 cross-difficulty factor (task 0: O&P/flood; task 1: water credit/dwelling). Every factor bears weight against an honest baseline, and every whole baseline is definite and differs from gold.
- [ ] Re-run of the instantiation-stage gates on the final form: **not run by the auditor.**
  - Per Step 0, the auditor cites the orchestrator's snapshot rather than running gates. The round-3 brief's snapshot, taken on this same charter hash `fbd0a7c3…09e8` and tools hash `6feaa40e…f8c6`, shows all 7 gates green, with traceability deferred until KB publication.
  - The formal re-run, and traceability after the KB is published, remain with the orchestrator.

The difficulty passes the source-layer audit on all four relationships as of revision 3. The only item left open is the traceability gate, which was deferred until the KB is published.

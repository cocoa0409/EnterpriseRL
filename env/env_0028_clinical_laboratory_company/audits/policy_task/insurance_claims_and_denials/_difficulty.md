# Policy-task audit — insurance_claims_and_denials / charter-global

## charter_global_frozen

- Freeze time: 2026-10-04T16:48:54Z (written before any task's GT was revealed; nothing in this section derives from a revealed GT).
- Auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiate agent.
- Frozen inputs (sha256, matching `audits/_views/policy_task/insurance_claims_and_denials/HASHES.txt`):
  - `tasks/insurance_claims_and_denials/coverage.extended.yaml` c5b79b294866412fae1b94ab01af9af6e71cc613da98f58360cec2cd90f4d408
  - `tasks/insurance_claims_and_denials/task_tools.py` 17dec1956707e9cd70c923655382e7afd7566161e9010f2361121bd4177e3022
  - task0.view.json 7df3d9ab63431fea19ddfbf582938126de5a31f9d382445922f58b30f920de55; task1.view.json 4623aafc45f5b8bcf7d010d5a2d9a43866b50a5b18fee32671d498e28899de44
- Fields permitted: blueprint (blueprint.yaml, db_schema.json, share_tools.py, products/*.yaml), the extended charter, task_tools.py, erlbench/ and the DSL evaluator in skills/erl-task-instantiate/scripts/check_compute.py (semantics of SUM/LATEST/within_months/CFIELD/CPARAM/X*), and per task only the masked view (frozen_time, user_scenario, initial_state).
- Fields masked (not read before every task's freeze): tasks/*.json in full (evaluation_criteria, computations, solvability_contract, prerequisite_closure, charter_scope, required_documents, design_rationale), the instantiate worklog, any prior audit.
- Entry conditions (Step 0): the brief carries the gate snapshot — check_extended EXTENDED OK, check_task_tools TASK TOOL CONTRACT OK, replay_tasks REPLAY OK, check_solvability SOLVABILITY OK, check_compute COMPUTE OK, check_grounding GROUNDING OK, check_cross_fire SCOPE OK; check_traceability deferred (KB not rendered). Masked views and hashes present; hashes re-verified with sha256sum and they match. Entry conditions met.
- Base copy: `diff <(head -n 1080 coverage.extended.yaml) blueprint/products/coverage.yaml` differs only by one trailing blank line — the base section is a verbatim copy.

### policy_conflict_scan

The charter holds the verbatim base (9 policies) and 8 extended policies, each bound to one target tool:

| extended policy | target_tool (owner) | computes | payer class reached | prerequisite edges |
| --- | --- | --- | --- | --- |
| coverage_ext_primary_internal_appeal | file_internal_appeal_c10f15cc (agent) | amount_in_dispute | "a contracted commercial plan" = Commercial In-Network Plan only (its first_level_appeal_name is "Internal Appeal") | value_input <- primary_information_correction |
| coverage_ext_primary_information_correction | file_information_correction_a0c86b6b (agent) | rebill_amount | any class (CO-16) | [] |
| coverage_ext_secondary_member_appeal | sign_member_appeal_c7144598 (user) | amount_in_dispute | "an out-of-network plan that pays second" = Commercial Out-of-Network Plan only | value_input <- secondary_identification_correction; state_gate <- primary_internal_appeal |
| coverage_ext_secondary_identification_correction | file_identification_correction_4ff16e31 (agent) | rebill_amount | any class (CO-31) | [] |
| coverage_ext_medicaid_plan_appeal | file_plan_appeal_d031f80e (agent) | amount_in_dispute | Medicaid Managed Care Plan only | value_input <- retro_authorization_correction; state_gate <- primary_member_appeal |
| coverage_ext_retro_authorization_correction | file_authorization_correction_79145f91 (agent) | rebill_amount | any class (CO-197) | [] |
| coverage_ext_primary_member_appeal | sign_primary_member_appeal_ad6f2953 (user) | amount_in_dispute | "an out-of-network plan that pays first" = Commercial Out-of-Network Plan only | value_input <- coordination_correction |
| coverage_ext_coordination_correction | file_coordination_correction_d59a8135 (agent) | rebill_amount | any class (CO-22) | [] |

Overlap scan:
- Subjects: four policies write `coverage_appeal_filed` (internal appeal, two member appeals, plan appeal) and four write `coverage_claim_resubmitted`; each is separated by denial code (CO-16 / CO-31 / CO-197 / CO-22) or by payer class (contracted commercial / out-of-network second / out-of-network first / Medicaid). No two extended policies reach the same (claim, denial) object in the same payer class, so no two policies give the same write two different values.
- Triggers/time anchors: every appeal inherits the base first-level window, the "Each level is filed once per claim" dedup and lab_appeal_levels_pursued; every correction inherits the base correction window, max_corrected_claims_per_claim and "A denial may be answered by at most one resubmission". No extended policy restates or contradicts these anchors.
- Terminal states: each write appends one claim line; no status transition; no conflict.
- Cross-category reads: orders (order_events credits/add-ons, orders.collection_date), invoices (invoice_transactions), assistance (approved award window and tier) — all read-only and within the customer; no conflict with those products' write ownership.
- Scope partition (derived from the masked views only, to be compared after reveal): task 0's world reaches {secondary_member_appeal, secondary_identification_correction, primary_internal_appeal, primary_information_correction}; task 1's world reaches {medicaid_plan_appeal, retro_authorization_correction, primary_member_appeal, coordination_correction}. The two sets are disjoint and together cover all 8 extended policies.
- Conflicts found: see `override_declarations` (event-field amount clause; CO-22 coordination gate) and `factor_ladders`.

### rule_compute_equivalence

Swept every compute binding against its `compute_basis` quotation and every basis quotation against the rule (mechanical check: every `compute_basis` value is a verbatim substring of its policy's whitespace-normalised `rule`; every compute binding has a basis entry and vice versa; every `K()` key used equals the `params` key set; every `baseline.rule` sentence is a verbatim sentence of the rule). Result: all pass for all 8 policies. Manual sweep:

- Windows: "within the last twelve/six months" is implemented as `within_months=12/6`, which the evaluator counts as calendar-month difference 0 <= MONTHS(event_date, today) < N (a row dated the same day-of-month or later 12 months back is excluded). The rule's words carry no counting convention; the implementation is one reasonable reading. Observation O-1 (no task in this difficulty has a row whose inclusion differs between "month difference" and "365 days" readings — checked in each task file).
- Claim/holding scoping: SUM/COUNT/LATEST are scoped to the target coverage; "on the coverage" in every rule matches.
- Rounding: every `result` uses RND (Python `round`, banker's on binary floats) while the rules say "rounded half up". Observation O-2: harmless only when no gold lands on an exact half cent (checked per task).
- coverage_ext_medicaid_plan_appeal `interest` = `MX(0, plan_portion) * ...`: the floor at zero on the plan portion inside interest is not stated in the rule ("The plan appeal's interest is its plan portion times its annual interest rate ..."). Observation O-3: compute adds a basis the rule does not state; it changes nothing unless the plan portion is negative (not the case in task 1).
- coverage_ext_secondary_identification_correction: the rule names the base "the leftover the plan paying first posted to the order's invoice", while `posted_leftover` sums every `invoices_responsibility_posted` line on that invoice (including any posted by the second plan itself). Observation O-4: in task 0 the order's invoice carries only the primary's posting, so no consequence there.
- Ladders: every `factors[].ladder` tier is a sentence of the rule and a branch of its `decides` binding, and every branch is a tier the rule states (all 39 declared factors checked). No tier lives only in compute.
- No compute binding invents a window, filter or branch absent from the rule apart from O-3.

### action_binding_and_uuids

- (target_tool, computes) pairs: 8 distinct tools, each claimed by exactly one policy.
- Docstrings: each describes one atomic write; none names another tool, states a position in a sequence, or carries before/after/first/once as an ordering of problems (the `appeal_level` enum text "first_level when no appeal has yet been filed on this claim" defines a level value, not an order of problems).
- Function bodies: every tool performs one `ctx.create` with no check of status, window, prerequisite or ownership (module docstring says so and the bodies confirm it). No tool judges a prerequisite.
- uuid8 suffixes: c10f15cc, a0c86b6b, c7144598, 4ff16e31, d031f80e, 79145f91, ad6f2953, d59a8135 — pairwise distinct, no shared prefix, no sequential or adjacent pattern. PASS.

### prerequisite_graph

Edges (all `form: state`, none carries `fallback_reason`):
1. primary_internal_appeal -> primary_information_correction, value_input, gate `disputed_charges` (exists in compute).
2. secondary_member_appeal -> secondary_identification_correction, value_input, gate `contested_charges` (exists).
3. secondary_member_appeal -> primary_internal_appeal, state_gate, gate `claim_events.appeal_level` (real field).
4. medicaid_plan_appeal -> retro_authorization_correction, value_input, gate `disputed_charges` (exists).
5. medicaid_plan_appeal -> primary_member_appeal, state_gate, gate `claim_events.appeal_level`.
6. primary_member_appeal -> coordination_correction, value_input, gate `contested_charges` (exists).

Every policy fills `prerequisite` ([] on the four corrections); every `problem` is an extended id of this file, none is a base policy or itself; the graph is acyclic (two disjoint trees of depth 3). Every `policy_source` is verbatim in the blocked policy's own rule (mechanically checked). Every `resolved_by` equals the depended-on policy's `target_tool`, and that tool's effect (a resubmission with reason corrected_claim / coordination_of_benefits_update, or an appeal line with appeal_level first_level) is exactly the row the `condition` names. `condition` texts match the sentence's strength (edge 1 "answering its CO-16 denial" = "answering each of its missing-information denials"; edge 5 "lodged by the member" = "carries a member appeal"). No authoring-viewpoint wording ("this task", "opening", "current world") in any condition or effect. PASS.

### prerequisite_sentences

Four-point test, per edge:

| edge | sentence (blocked policy's own rule) | connective | waited-on state (record-visible) | tool/id/snake_case named | strength |
| --- | --- | --- | --- | --- | --- |
| 1 | "The internal appeal's disputed charges are fixed only after the claim carries a corrected claim answering each of its missing-information denials." | only after | a corrected claim on the claim answering its CO-16 line (claim_events resubmission linked to the denial) | none | each CO-16 of that claim — matches condition |
| 2 | "The second-plan member appeal's contested charges are fixed only after the coverage carries a corrected claim, filed within those six months, answering its patient-identification denial." | only after | a corrected claim within six months answering the coverage's CO-31 | none | matches |
| 3 | "The second-plan member appeal's amount is not recorded until the claim held by the plan paying first for the same order carries a first-level appeal." | not ... until | a first-level appeal line on the primary coverage's claim for the same order | none | matches |
| 4 | "The plan appeal's disputed charges are not fixed until each authorization denial on the claim carries a corrected claim." | not ... until | a corrected claim answering each CO-197 of the claim | none | matches |
| 5 | "The plan appeal's amount is recorded only after the claim held by the plan paying first for the same order carries a member appeal." | only after | a member appeal (first-level appeal line) on the primary coverage's claim for the same order | none | matches |
| 6 | "The first-plan member appeal's contested charges are not fixed until the coverage carries a coordination claim, filed within those six months, answering its other-coverage denial." | not ... until | a coordination resubmission within six months answering the coverage's CO-22 | none | matches |

One write per state-form edge (reader's derivation sentence + records + depended-on rule -> resolving action):
- Edge 1: a corrected claim answering a missing-information (CO-16) denial is described only by coverage_ext_primary_information_correction ("This rule fixes the amount a corrected claim carries when the laboratory answers a missing-information denial (CO-16)"); the identification and authorization corrections answer CO-31 / CO-197. Unique.
- Edge 2: only coverage_ext_secondary_identification_correction answers a patient-identification denial (CO-31). Unique.
- Edge 4: only coverage_ext_retro_authorization_correction answers an authorization denial (CO-197). Unique.
- Edge 6: only coverage_ext_coordination_correction files a "coordination claim" answering an other-coverage denial (CO-22). Unique.
- Edges 3 and 5: three writes of this difficulty create a first-level appeal line (file_internal_appeal for a contracted commercial plan, sign_primary_member_appeal for an out-of-network plan paying first, file_plan_appeal for Medicaid; sign_member_appeal is for a plan paying second, never "the plan paying first"). The payer class of the coverage that pays first, read from `coverages.variant_name` + `coordination_order`, selects exactly one of them (Medicaid can never pay first when another coverage is live — base COB "Medicaid Managed Care Plan pays last"). Edge 5's "member appeal" additionally excludes the laboratory-filed internal appeal. The hop is resolvable in one reading once the records are read; recorded as observation O-5 (the waited-on state is not singled out by the sentence alone, but by sentence + records, which is the intended reading).
- No blocked rule carries a second wording, a tool name or another problem's id; no depended-on rule restates the sentence; docstrings are silent about sequence. No extended rule states a cross-problem order that grounds no edge, except the clause discussed in finding P-2 (the coordination correction's "once the coordination on file is current", which is a state the correction itself waits on and which no edge declares — see `override_declarations`).
- Base rule sentences stating cross-problem orders: coverage_evt_corrected_claim "coordination_of_benefits_update (CO-22, only after the coverage's coordination order has been updated following the denial; when cob_questionnaire_required_on_co22 is true the patient must first have updated their other-coverage information with the payer)", coverage_evt_denial_liability "CO-22 (other coverage primary) is cured by a corrected claim after the coordination order is updated", coverage_agg_coordination_of_benefits "A secondary claim is filed only after the primary payer's remittance". None grounds a declared edge. The first two bear on the coordination correction node of task 1 — see finding P-2 and `task1.md`.

### override_declarations

Sentence-by-sentence over each `base_policy_refs` entry (findings only; consequences are demonstrated in the task files).

coverage_evt_appeals (refs of the four appeal policies):
- "Denials CO-50, CO-151 and CO-197 (when no retroactive authorization is available) are appealed rather than corrected; a denial curable by a corrected claim is never appealed." — every extended appeal's disputed/contested charges add curable denial amounts (CO-16, CO-31; plus CO-22 and CO-27 for the first-plan member appeal; CO-197 for the plan appeal) "while no corrected claim stands". That disputes curable denials in an appeal, which this sentence forbids; not named in any `overwrite`. Observation O-6: in each task the edge forces the correction first, so the branch that includes curable amounts is never reached on the gold path and no second scored value can be demonstrated.
- "The laboratory files appeals on its own initiative through lab_appeal_levels_pursued levels; beyond them ... only the patient can appeal" — followed (all appeals are first_level; member appeals are the patient's own act).
- "When appeal_requires_patient_authorization is true, the laboratory may file only after the patient has personally signed an authorized-representative form for that claim." — superseded and named in both member-appeal policies' `overwrite` (replaced by the patient's own signature on the member appeal request). Merged reading unique.
- First-level window, counting rule, "Each level is filed once per claim", decision/reprocessing sentences — inherited, not contradicted.
coverage_evt_adjudication — "Each remittance resolves ..." and the cost-share / balance-billing sentences govern remittance posting, not the appeal amount or the re-bill amount; followed. The appeals' member-share/residual percents are projections of what the member would owe if overturned and do not contradict "the remittance governs". Observation only.
coverage_evt_denial_liability — "CO-16 ... and CO-31 ... are cured by a corrected claim" followed; "CO-22 (other coverage primary) is cured by a corrected claim after the coordination order is updated" — see finding P-2; "for CO-197 a retroactive authorization requested by the provider within prior_auth_retro_request_days of the date of service is filed as a corrected claim instead" — inherited, not restated by coverage_ext_retro_authorization_correction; its evidence is a per-task question (see task1.md). "Denials in group CO are never billed to the patient" — the member appeals call their amount the "member's net exposure" on CO-50 lines; a naming tension, not two values (observation O-7).
coverage_evt_corrected_claim:
- "A corrected or replacement claim answers one denial and carries that denial's amount" — superseded and named by all four correction policies. Declared.
- "its reason is ... coordination_of_benefits_update (CO-22, only after the coverage's coordination order has been updated following the denial; ...)" — coverage_ext_coordination_correction's `replaced_by` text adds "once the coordination on file is current", a different gate (a state of the record) from the base's "has been updated following the denial" (an update event after the denial); the base clause is not named as superseded. Finding P-2.
- Window, max corrections, one resubmission per denial — inherited, not contradicted.
coverage_agg_coordination_of_benefits — followed; the "plan paying first / second" wording in the extended rules reads `coordination_order`.
Base text outside the policies but in the same charter: event `coverage_claim_resubmitted`, field `amount`: "Amount put back in front of the payer; equals the denied amount being resubmitted." — a second clause on the very quantity the four corrections compute; the four `overwrite` entries name only the policy sentence. Finding P-1.

### factor_ladders

Per policy (effect: m = method, p = parameter; xd = cross_difficulty):

| policy | factors (effect) | count / p / m | xd factors |
| --- | --- | --- | --- |
| primary_internal_appeal | valuation (m), member_share (p), out_of_pocket_hold (m), interest_days (m), interest_rate (p), underpayment (m) | 6 / 2 / 4 | none |
| primary_information_correction | scope (m), credits (m), reprice_minimum (p), late_charge_minimum (p) | 4 / 2 / 2 | credits: orders |
| secondary_member_appeal | cap_ratio (m), filing_benefit (p), residual_share (p), assistance (p), interest_days (m) | 5 / 3 / 2 | filing_benefit: orders; assistance: assistance |
| secondary_identification_correction | leftover_base (m), invoice_minimum (p), credits (m), credit_minimum (p) | 4 / 2 / 2 | leftover_base: invoices; credits: orders |
| medicaid_plan_appeal | valuation (m), crossover_percent (p), member_copay (p), interest_days (m), interest_rate (p), underpayment (m) | 6 / 3 / 3 | crossover: orders |
| retro_authorization_correction | scope (m), credits (m), credit_minimum (p), invoice_minimum (p) | 4 / 2 / 2 | credits: orders |
| primary_member_appeal | balance_share (m), late_claim (p), leftover (p), relief (p), interest_days (m), interest_rate (p) | 6 / 4 / 2 | late_claim: orders; relief: assistance |
| coordination_correction | scope (m), credits (m), credit_minimum (p), late_charge_minimum (p), invoice_minimum (p) | 5 / 3 / 2 | credits: orders |

Structure checks (all 39 factors): each ladder has exactly 3 tiers, pairwise disjoint as stated, every tier's condition and value/method stated in the rule and implemented in its `decides` binding; `decides` is an input, never `result`; binding sets are disjoint within each policy; no two tiers of one ladder select the same value or method; each fall-through equals the factor's `baseline`; `baseline.rule` of every policy is self-sufficient (claim/object + disputed charges at billed value, or re-file as billed, rounded once; the plan appeal subtracts its named standard copay). Labels: every `parameter` ladder selects a number; every `method` ladder selects a different computation (a different aggregate as multiplier, a different day count, a cap rule, a whole/partial/nil addition, a different base) — honest under the open method list.

Multi-source factors exist in both trees (e.g. every correction's credits factor: credit date on the order ledger against the filing date on the claim ledger, AND the credit reason; the member appeals' assistance/relief factor: award window against the order's collection date AND the tier's discount percent).

Realism of conditions — finding F-1: in four policies whose scope is a single payer class, a tier condition (or one part of a compound condition) is a payer-class parameter that is constant over that class, so it holds of every customer who reaches the write and restates the policy's scope:

| factor | scope-restating part | value over the only class reached | effect on the ladder |
| --- | --- | --- | --- |
| internal_appeal_member_share | "the payer class carries a member cost share on clinical laboratory tests" | Commercial In-Network: clinical_lab_patient_cost_share true | tiers 1 and 2 exhaust every reachable customer; the fall-through "otherwise it is zero" (= baseline 0) is unreachable — a member share of zero for an in-network plan that carries cost share is a treatment no such plan gives |
| internal_appeal_valuation | "the payer class writes billed charges down to a contracted allowance" | Commercial In-Network: contractual_adjustment_applies true | part of tiers 1 and 2 restates scope |
| second_plan_residual_share | "the payer class carries a member cost share on clinical laboratory tests" | Commercial Out-of-Network: true | fall-through 0 (= baseline) unreachable |
| second_plan_cap_ratio | "the payer class lets the laboratory bill the member a balance" | Commercial Out-of-Network: balance_billing_allowed true | part of tiers 1 and 2 restates scope |
| first_plan_leftover | "the payer class carries a member cost share on clinical laboratory tests" | Commercial Out-of-Network: true | fall-through 0 (= baseline) unreachable |
| first_plan_balance_share | "the payer class lets the laboratory bill the member a balance" | Commercial Out-of-Network: true | part of tiers 1 and 2 restates scope |
| plan_appeal_valuation | "the payer class writes billed charges down to a contracted allowance" | Medicaid Managed Care: contractual_adjustment_applies true | part of tiers 1 and 2 restates scope |

Counting only factors that pass: primary_internal_appeal keeps out_of_pocket_hold (m), interest_days (m), interest_rate (p), underpayment (m) = 4 factors with 1 parameter (< 2) — fails the bound; secondary_member_appeal keeps filing_benefit (p), assistance (p), interest_days (m) = 3 factors (< 4) — fails the bound; primary_member_appeal keeps late_claim, relief, interest_rate (p) and interest_days (m) = 4 / 3 p / 1 m — within bounds; medicaid_plan_appeal keeps crossover, member_copay, interest_rate (p), interest_days, underpayment (m) = 5 / 3 / 2 — within bounds. The four corrections are not scoped to one payer class; their payer-class parts genuinely divide customers (e.g. Commercial Out-of-Network has contractual_adjustment_applies false), so no strike.

Observation O-8: the interest-rate factors (internal_appeal_interest_rate, plan_appeal_interest_rate, first_plan_interest_rate) declare as baseline the base rate, but each policy's `baseline.rule` carries no interest at all; the base rate is a fall-through value rather than something the baseline method states. It bears weight only while the interest-days factor sits off its baseline.

Observation O-9 (business realism, no demonstrable consequence): the member appeals reduce the amount disputed with the payer by the patient's financial-assistance discount (and by a fixed 50% "hardship contest percent" for a zero-percent hardship award), and the appeals aggregate denials of every claim on the coverage within six months into one claim's appeal amount; both are unusual payer-appeal practice, but neither is shown to give a second value on these worlds.

### findings

- **P-1 — SOURCE-POLICY RED (undeclared override, event-field amount clause).** Symptom: the base event `coverage_claim_resubmitted` defines its `amount` as "Amount put back in front of the payer; equals the denied amount being resubmitted." while the four correction policies fix that same amount as a re-bill amount (scope less credits/invoice corrections plus riding add-ons, or a secondary's leftover base). Root cause: each correction's `overwrite` names only coverage_evt_corrected_claim's "A corrected or replacement claim answers one denial and carries that denial's amount"; the event-field sentence on the same quantity stays in force, unnamed. Evidence: coverage.extended.yaml events block, `coverage_claim_resubmitted.fields.amount` (line ~557) vs the four `overwrite` blocks (lines 1337-1340, 1752-1755, 2187-2190, 2617-2620). Bears on: task 0 (information and identification corrections), task 1 (coordination and authorization corrections); consequences demonstrated in those files.
- **P-2 — SOURCE-POLICY RED (undeclared weakening of the base CO-22 gate).** Symptom: base coverage_evt_corrected_claim allows a coordination_of_benefits_update only "after the coverage's coordination order has been updated following the denial" (and base coverage_evt_denial_liability: "CO-22 ... is cured by a corrected claim after the coordination order is updated"); coverage_ext_coordination_correction's own rule instead answers the CO-22 "once the coordination on file is current". Root cause: the `overwrite` names only the amount sentence; the gate sentence is neither superseded nor followed. No task tool records a coverage details update. Bears on: task 1 (coordination correction and everything downstream); demonstrated there.
- **F-1 — SOURCE-FACTOR RED (unreal ladders: scope-restating conditions, unreachable fall-throughs).** See the table above. Bears on: task 0 (internal appeal and second-plan member appeal — also below the factor-count bounds once struck), task 1 (first-plan member appeal and plan appeal).
- Observations O-1 ... O-9 as recorded above; none is grounds for rework on its own.

## closing_checklist

Written after both tasks' frozen derivations (0.md 16:51:45Z, 1.md 16:52:54Z) and the GT reveal (16:52:58Z); the charter-global section above was not edited after the reveal except a pre-reveal wording fix in policy_conflict_scan.

- Audit files: `0.md`, `1.md` correspond one-to-one with tasks/0.json and tasks/1.json; this file sits alongside; first revision, no older revision to preserve.
- Comparison verdicts: neither task PASSES all four relationships — task 0: SOURCE-POLICY RED (P-1), SOURCE-FACTOR RED (F-1); task 1: SOURCE-POLICY RED (P-1, P-2), SOURCE-FACTOR RED (F-1, T-2), SOURCE-TASK RED (T-1). Problem tree PASS in both.
- Coverage and scope: GT charter_scope task 0 = {primary_information_correction, primary_internal_appeal, secondary_identification_correction, secondary_member_appeal}, task 1 = {coordination_correction, primary_member_appeal, retro_authorization_correction, medicaid_plan_appeal} — equal to the pre-reveal partition, pairwise disjoint, jointly covering all 8 extended policies; each task uses exactly its four tools; uuid8s independent (see action_binding_and_uuids).
- Trees: each has 3 prerequisite problems, 2 value_input edges, one owner=user write, no cycle; the difficulty-wide graph is two disjoint acyclic trees.
- Computations: every computation declares a self-sufficient baseline and 4-6 factors, every factor bears weight numerically on its world and every whole baseline differs from gold; but F-1 strikes seven ladders as unreal and T-2 strikes task 1's relief tier, leaving the internal appeal (1 parameter) and both member appeals (3 factors) below the bounds.
- Gate re-run on the final form: not performed — the difficulty does not reach the closing state (closing applies only once all four relationships PASS); the instantiation-stage gate snapshot supplied with the brief is the latest machine evidence.

Difficulty verdict: does NOT pass the source-layer audit.

## revision_2

### charter_global_frozen (round 2)

- Freeze time: written 2026-10-04 after 17:52:23Z, before any round-2 task JSON was opened. Auditor: the same independent auditor as round 1.
- Inputs (sha256, matching the round-2 `HASHES.txt`): coverage.extended.yaml b0516fe1d000e0b32baa2344ab85231a8ae186194176359ddf23808593571a35 (CHANGED from round 1 c5b79b29...); task_tools.py 17dec1956707e9cd70c923655382e7afd7566161e9010f2361121bd4177e3022 (unchanged); task0.view 6d79cee9...; task1.view 5c2e0693....
- Re-derivation rule: the extended charter's hash changed, so every charter-global section is re-derived in full below; `action_binding_and_uuids` depends on task_tools.py (unchanged) and on the (target_tool, computes) pairs, re-checked.
- Base copy: still verbatim (diff against blueprint/products/coverage.yaml differs only by the trailing blank line); blueprint files unmodified since round 1 (mtimes 14:39-15:03Z).
- Entry conditions: coordinator gate snapshot after rework — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; traceability deferred. Views and hashes present and matching.
- Masked until both round-2 task derivations are frozen: tasks/0.json, tasks/1.json (round 2), the worklog. Disclosure: the auditor read the round-1 GT of both tasks during round 1 (recorded in the round-1 comparisons); that knowledge is of the previous revision and is not used as evidence below.

### policy_conflict_scan (round 2)

Same 8 policies, same 8 tools, same payer-class/denial-code partition as round 1; no two policies reach the same (claim, denial) object. New declared overrides: coverage_ext_retro_authorization_correction supersedes coverage_evt_denial_liability's retroactive-request sentence; coverage_ext_coordination_correction supersedes coverage_evt_corrected_claim's CO-22 clause and coverage_evt_denial_liability's CO-22 cure sentence. Every `superseded_clause` is verbatim in the named base rule and every `replaced_by` is verbatim in the extended rule (mechanical check). Merged readings below are unique. Scope partition derived from the round-2 views: task 0 {primary_information_correction, primary_internal_appeal, secondary_identification_correction, secondary_member_appeal}; task 1 {coordination_correction, primary_member_appeal, retro_authorization_correction, medicaid_plan_appeal} — disjoint, jointly complete.

### rule_compute_equivalence (round 2)

Mechanical sweep repeated: every `compute_basis` quotation verbatim in its rule; no compute binding without basis and no basis without binding; `K()` keys = `params` keys for all 8 policies; every `baseline.rule` sentence verbatim in the rule; binding sets of each policy's factors disjoint. Manual sweep of the changed policies:
- The four corrections now carry "the denied amount being resubmitted": the denial's amount less the order's later credits and invoice corrections multiplied by the correction's share (identification correction: the second plan's posted-leftover base, never above the denial, less credits). Every compute implements this; result is clamped at zero and can never exceed the denial (`MX(0, denied - ...)`, `MN(ident_base, denied) - ...`).
- O-3 (round 1) closed: the plan appeal's rule now says "its plan portion, taken as zero where it is negative", matching `MX(0, plan_portion)`.
- New observation O-14: coverage_ext_coordination_correction's removal minimum — rule "the plan adjudicated at least one line of the claim" (the same rule elsewhere counts payment, member and contractual-adjustment lines as adjudication) vs compute `COUNT(... coverage_contractual_adjustment ...) >= 1` only. The two faces differ for a claim adjudicated only by payment or member lines; in task 1 the claim carries a contractual adjustment, so no consequence is demonstrable.
- New observation O-13: coverage_ext_secondary_identification_correction's definitional sentence ("the patient-identification denial's amount less the part of the order's later credits and invoice corrections that falls on it") and its mechanism (base = the leftover the first plan posted to the order's invoice, less billing-error corrections, never above the denial; then credits) coincide only when the posted leftover equals the denial; in task 0 they do (41.40 = 41.40).
- O-4 unchanged (posted_leftover sums every responsibility posting on the invoice; task 0's invoice carries only the primary's posting).
- O-1 / O-2 unchanged (checked per task).

### action_binding_and_uuids (round 2)

task_tools.py unchanged (hash 17dec195...); (target_tool, computes) pairs unchanged and unique; round-1 conclusion carried forward on that hash: PASS.

### prerequisite_graph (round 2)

Six edges unchanged in problem, kind, gate, form, `policy_source` (verbatim, re-checked), `resolved_by` (= target tool, re-checked); no `fallback_reason`; acyclic. PASS.

### prerequisite_sentences (round 2)

The six sentences are unchanged; four-point test and one-write analysis as in round 1 (O-5 unchanged). The round-1 issue with the base CO-22 order sentence (finding P-2) is now addressed by a declared override: the base clause "only after the coverage's coordination order has been updated following the denial; ..." is superseded by "A coordination claim answers an other-coverage denial where the coverage's coordination order on file already gives it the payment position the coordination rules assign it and, where the payer class requires it, the patient has updated their other-coverage information with the payer." This is a record-visible state plus a caller fact, not a cross-problem order; no remaining extended or base sentence grounds an undeclared dependency for any node of either tree.

### override_declarations (round 2)

- coverage_evt_corrected_claim "A corrected or replacement claim answers one denial and carries that denial's amount" — superseded by all four corrections (declared).
- Event field `coverage_claim_resubmitted.amount` "Amount put back in front of the payer; equals the denied amount being resubmitted." (round-1 P-1) — still not named in any `overwrite`, but no longer contradicted: each correction now fixes its amount as the part of the denied amount that is resubmitted (the denial less the share of later credits/corrections that falls on it), never above the denial. Read together, the event field and the policies give one value. The round-1 contradiction came from add-on charges riding above the denial, and those are gone. P-1 CLOSED. Observation O-15: the closure rests on reading "the denied amount being resubmitted" as the part of the denial put back; the extended rules state that reading outright.
- coverage_evt_corrected_claim CO-22 clause and coverage_evt_denial_liability "CO-22 ... is cured by a corrected claim after the coordination order is updated" — both superseded and named (round-1 P-2). Merged reading: a CO-22 refile is allowed where the coordination order on file already matches the coordination rules (base coverage_agg_coordination_of_benefits) and, for a payer class with cob_questionnaire_required_on_co22 true, the patient states the other-coverage update. Unique. P-2 CLOSED.
- coverage_evt_denial_liability "for CO-197 a retroactive authorization requested by the provider within prior_auth_retro_request_days of the date of service is filed as a corrected claim instead" — superseded and named (round-1 T-1 root): "An authorization denial is cured by an authorization correction where the order carries an approved authorization with its authorization number, the plan having accepted the provider's retroactive request." The condition is now record-visible (orders.prior_auth_status, orders.prior_auth_number). Consistent with base coverage_evt_appeals "CO-197 (when no retroactive authorization is available)". Unique.
- All other base sentences: as in round 1 (O-6, O-7 unchanged).

### factor_ladders (round 2)

| policy | factors (effect) | count / p / m | xd factors |
| --- | --- | --- | --- |
| primary_internal_appeal | valuation (m), member_share (p), out_of_pocket_hold (m), interest_days (m), interest_rate (p), underpayment (m) | 6 / 2 / 4 | none |
| primary_information_correction | apportionment (m), credits (m), credit_minimum (p), invoice_minimum (p) | 4 / 2 / 2 | credits: orders |
| secondary_member_appeal | cap_ratio (m), filing_benefit (p), residual_share (p), assistance (p), interest_days (m) | 5 / 3 / 2 | filing: orders; assistance: assistance |
| secondary_identification_correction | leftover_base (m), invoice_minimum (p), credits (m), credit_minimum (p) | 4 / 2 / 2 | leftover: invoices; credits: orders |
| medicaid_plan_appeal | valuation (m), crossover (p), member_copay (p), interest_days (m), interest_rate (p), underpayment (m) | 6 / 3 / 3 | crossover: orders |
| retro_authorization_correction | apportionment (m), credits (m), credit_minimum (p), invoice_minimum (p) | 4 / 2 / 2 | credits: orders |
| primary_member_appeal | balance_share (m), late_claim (p), leftover (p), relief (p), interest_days (m), interest_rate (p) | 6 / 4 / 2 | late: orders; relief: assistance |
| coordination_correction | apportionment (m), credits (m), credit_minimum (p), invoice_minimum (p), removal_minimum (p) | 5 / 3 / 2 | credits: orders |

Round-1 F-1 re-check: the payer-class parts that restated a single-class scope are removed from internal_appeal_valuation, second_plan_cap_ratio, first_plan_balance_share and plan_appeal_valuation (tiers now turn on paid lines / twelve-month plan payment / six- vs twelve-month balance only). The three member-share ladders now turn on deductible history alone, with a reachable fall-through, "no deductible assigned within twelve months", that maps to a declared standard percent: internal 15, second plan 55, first plan 55. Each policy's baseline.rule now subtracts that standard percent ("less the internal appeal's standard member share percent of them", etc.), so fall-through = baseline = what baseline.rule states. Every ladder: 3 tiers, disjoint, stated in the rule, implemented in its `decides` binding; no two tiers share a value or method; labels honest (apportionment and removal/credit ladders change how the reduction is formed; minimum ladders select numbers). No condition is constant over the payer class a policy reaches: the remaining payer-class condition, coord_removal_minimum's "writes billed charges down", divides customers because coordination_correction is not class-scoped. All four policies are within 4-6 factors with >= 2 parameter and >= 1 method. F-1 CLOSED.

Observation O-11 (realism, no demonstrable consequence): in the three member-share ladders the fall-through (no deductible assigned in twelve months) gives a lower member share than the middle tier (some deductible assigned, below the satisfied amount): 15 vs 50, and 55 vs 70 in both member appeals. That fits a plan without a deductible, but a member who has simply not started the deductible would be treated more generously than one partway through it. Neither task's customer sits on the fall-through.
Observation O-12 (realism, task 1): the credits ladders take every not-performed/duplicate credit on the order, including a credit on a charge posted after the claim was filed and so never billed on it. See 1.md.
O-8 (interest-rate baselines not stated in baseline.rule) and O-9 unchanged.

### findings (round 2)

- P-1 CLOSED (see override_declarations; O-15).
- P-2 CLOSED (declared override; unique merged reading).
- F-1 CLOSED (scope-restating parts removed; fall-throughs reachable and equal to baseline; bounds met).
- O-3 CLOSED.
- New observations O-11, O-12, O-13, O-14, O-15; carried observations O-1, O-2, O-4, O-5, O-6, O-7, O-8, O-9.
- No new charter-global RED.

### closing_checklist (round 2)

Written after both round-2 frozen derivations (17:57:43Z) and the round-2 GT reveal (17:57:49Z).
- Audit files: `0.md`, `1.md` one-to-one with the tasks, `_difficulty.md` alongside; round-1 text preserved untouched above each `## revision_2`.
- Comparison verdicts: task 0 PASS on all four relationships; task 1 PASS on all four relationships.
- Round-1 REDs: P-1, P-2, T-1, T-2, F-1 closed; O-3 closed. Observations checked without change: O-1, O-2, O-4, O-6, O-8, O-9, O-T1 (still observations, none grounds rework). New observations: O-11, O-12, O-13, O-14, O-15.
- Coverage and scope: GT charter_scope task 0 {primary_information_correction, primary_internal_appeal, secondary_identification_correction, secondary_member_appeal}, task 1 {coordination_correction, primary_member_appeal, retro_authorization_correction, medicaid_plan_appeal} — disjoint, jointly covering all 8 extended policies; each task uses exactly its 4 tools; uuid8s independent and unchanged.
- Trees: each 3 prerequisites, 2 value_input, 1 owner=user write, acyclic; difficulty-wide graph acyclic (two disjoint trees).
- Computations: every computation has a self-sufficient baseline stated in its rule and 4-6 factors (>= 2 parameter, >= 1 method); each task has multi-source and cross-difficulty factors with seeded, charter-consistent rows; every factor bears weight on its world and every whole baseline differs from gold (task 0: 172.00/158.10/41.40/83.70 vs 162.87/124.34/32.00/15.95; task 1: 186.00/111.60/79.00/245.00 vs 80.42/19.24/76.46/127.20).
- Gates re-run on the final form (2026-10-04T17:58Z, `PYTHONDONTWRITEBYTECODE=1`): check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cross_fire SCOPE OK; traceability deferred to KB publication.
- Boundary incident (disclosed): `replay_tasks.py` run without `--check` writes `db_closure` / `db_closure_matches_initial_state` back into tasks/0.json and tasks/1.json (mtime 17:58:05Z; sha256 afterwards 877ab2e2... and 3a4ee481...). It rewrites only those two fields, recomputed deterministically from each file's own initial_state and gold, and the coordinator's post-rework snapshot ran the same command. So the bytes are expected to be unchanged, but the auditor had no pre-run hash of the task files to prove it. No scored or proof field was touched. A later `--check` run reports REPLAY OK.

Difficulty verdict (round 2): PASSES the source-layer audit.

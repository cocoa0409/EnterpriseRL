# Policy-task audit — retail_claims_and_reimbursements / charter-global

## charter_global_frozen

- Scenario: env/env_0047_pharmacy_benefit_manager; difficulty: retail_claims_and_reimbursements (category `retail`); M = 2.
- Freeze hashes (sha256, checked against the brief before reading):
  - `tasks/retail_claims_and_reimbursements/retail.extended.yaml` = 6a10f8d4c37a8529bff7aa523b2fd1b31fc1a4724b8957590655fa2f0078e36c
  - `tasks/retail_claims_and_reimbursements/task_tools.py` = 86d4193e65c3cb9e73c401f3e2f5a4bec0d45a1a0f64ce0ccd46c630671aaf29
- Freeze time: 2026-10-08 07:20 UTC (written before either task's GT was opened). Auditor: independent policy-task auditor (did not author the artifacts).
- Read for this section: `blueprint/blueprint.yaml` (difficulties block), `blueprint/db_schema.json`, `blueprint/share_tools.py` (finder list), `blueprint/products/{retail,plan,review,mail,formulary}.yaml` (retail base + the variant parameters the extended computes read), the extended charter, `task_tools.py`, and the runtime DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`: LATEST/COUNT scoped to the benefit, `within_months` = whole calendar months via MONTHS, DAYS = calendar days).
- Masked / not read: `tasks/*.json` (all fields), `worklog.md`, any earlier audit (none exists — the directory was empty).
- Entry conditions (Step 0): the brief supplied the gate snapshot (check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cross_fire SCOPE OK; check_traceability deferred) and the two masked views with hashes (task_0.view.json 44145a03…, task_1.view.json bb9d699a…; both re-hashed and matched). Input complete.
- Base copy: `diff <(sed -n 1,993p retail.extended.yaml) blueprint/products/retail.yaml` differs only by one trailing blank line — the base section is verbatim.

### policy_conflict_scan

Extended policies (5), their writes and claimed computations:

| policy | target_tool (owner) | computes | trigger | prerequisite edges |
| --- | --- | --- | --- | --- |
| retail_ext_paper_claim_reimbursement | approve_paper_claim_1f52e397 (agent) | reimbursement_amount | state_due | none |
| retail_ext_review_bridge_supply | grant_review_bridge_supply_635c815d (agent) | days_supply_allowed | state_due | ← paper_claim (value_input, on_hand) |
| retail_ext_vacation_supply_days | request_vacation_supply_35815dad (user) | days_supply_allowed | on_request | ← review_bridge (value_input, pending); ← paper_claim (value_input, on_hand) |
| retail_ext_dose_change_supply | grant_dose_change_override_e9e89c2d (agent) | days_supply_allowed | state_due | none |
| retail_ext_lost_stolen_replacement | report_lost_stolen_replacement_dcea41b5 (user) | days_supply_allowed | on_request | ← dose_change (value_input, lost_days) |

- Overlapping subjects: four policies share subject `retail_override_granted` but each writes a different `override_type` through a different tool (emergency_supply / vacation_supply / dose_change / lost_stolen), so no two reach a conclusion about the same row. The paper-claim policy alone writes `retail_dmr_approved`. No two extended policies compete for one quantity.
- Cross-reads between policies are one-directional and match the declared edges: bridge and vacation read approved paper claims; vacation reads emergency_supply overrides; lost-stolen reads dose_change overrides and counts every override type for the drug (so the dose-change grant also enters lost-stolen's share tier — declared in the edge's `effect`). Dose-change and paper-claim read no other extended policy's write.
- Time anchors: all five use frozen_time's date as "today"; override validity (seventh calendar day) is applied by the tools exactly as base `retail_evt_override` states.
- Cross-category read boundaries: plan (CPARAM/CFIELD on the active enrollment), review (review_cases, review_authorizations, review program params), mail (mail_accounts, mail_prescriptions, mail_orders, home delivery params). All reachable through share finders (find_plan_enrollments, find_review_cases, find_review_authorizations, find_review_programs, find_mail_accounts, find_mail_prescriptions, find_mail_orders) plus the rendered product parameters.
- Scope of the M tasks (derived blind from the views, to be confirmed at reveal): task 0's world (vacation request, pending Ubrelvy renewal, undecided foreign paper claim) engages {paper_claim, review_bridge, vacation}; task 1's world (stolen Nurtec, QL approval after the last fill) engages {dose_change, lost_stolen}. The two sets are disjoint and together cover all five extended policies.
- Conflicts found by this scan are listed under `override_declarations` and `findings` (CG-3, CG-4 are undeclared deviations from base on networks no task uses).

### rule_compute_equivalence

Mechanical sweep: every `compute_basis` quotation is a verbatim substring of its policy's `rule` (one case-only mismatch: paper-claim `clm_dos` quotes "the overlap of the paper claim…" where the rule has "The overlap…"); every `baseline.rule` sentence is a sentence of the `rule`; every compute binding has a basis entry; every `replaced_by` is in the rule. Manual sweep per policy:

- paper_claim: days cap ladder, overlap/refill-threshold ladder (threshold = days supply × early_refill_threshold_[non]controlled; "before the threshold" ↔ `elapsed < net_days * refill_threshold`), allowed-amount ladder (foreign: receipt × paid_days / receipt days × oon_reimbursement_rate; US OON: per_day × paid_days × rate; network: per_day × paid_days; RND 2), day-supply multiple, tier copay/coinsurance, OOP-max and insulin cost-share ladder, final `max(0, min(allowed, paid) − cost_share)` RND 2, and the explicit step order — all stated and implemented. Equivalent.
- review_bridge: case-opening ladder (`case_by != 'prescriber'` equals "member or an authorized representative" because the `requested_by` enum is exactly {prescriber, member, authorized_representative}), outstanding info-request ladder, home-delivery ladder, on-hand (approved paper claim later than every paid network claim wins), netting. Equivalent.
- vacation: on-hand anchor ladder, authorised-supply offset, review-status ceiling, 6/12-month vacation reduction (`within_months` = whole calendar months), carried early days, single-step subtraction floor 0. Equivalent, with one loose point recorded as observation O-4 (tier 2 of the offset — "such an emergency supply has already been used" — is coded without the seven-day window that "such" may carry).
- dose_change and lost_stolen: **not equivalent on the transit interval** — the rule says the days of a standard home delivery shipment "start the home delivery program's standard_shipping_business_days after the shipment date"; that parameter is defined in `products/mail.yaml` as "business days in transit for standard shipping after dispensing", yet `transit` / `arrival` add it to calendar-day arithmetic (`transit - DAYS(src_dos, NOW)`, `arrival + lost_len - DAYS(lost_dos, NOW)`). The conversion of business days into calendar days is a basis compute invents and the rule never states (the rule's "All quantities are whole days" does not say calendar days). Finding CG-1.
- Other dose_change/lost_stolen points checked and equivalent: fill source (shipment later than the last paid retail claim, or that claim reversed), QL approval in force and effective after the fill / pending QL case, share (controlled 0.85 / QL-managed non-controlled 1.0 / other 0.75), re-count rounding down, fill-length sizing, earlier-loss and override-share ladders, floor/int at the end.

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one policy (five distinct tools). Subjects/terminal states admit one reading each: approval row + `reimbursement_balance` increase; one `retail_overrides` row per grant of the stated override_type.
- Docstrings name no other tool and state no position in a sequence. They contain "after the call …" (post-call effect) and real-world "before the review is decided / before the member travels / before the earlier fill would otherwise allow a refill" — business timing, not inter-tool order (observation O-5).
- Function bodies: none checks a business precondition, refuses or hints (each does find → create/update → return). Tool layer does not judge prerequisites.
- uuid8s: 1f52e397, 635c815d, 35815dad, e9e89c2d, dcea41b5 — pairwise distinct, no shared prefix/suffix, no sequential pattern. PASS.

### prerequisite_graph

- Every policy fills `prerequisite` (two `[]`). Edges: bridge→paper_claim, vacation→bridge, vacation→paper_claim, lost_stolen→dose_change. All `problem` ids are extended ids in this file, none self, none base. Acyclic (two components: paper_claim → bridge → vacation with paper_claim → vacation; dose_change → lost_stolen).
- Every `policy_source` is verbatim in the blocked policy's own `rule` (mechanically checked). All `form: state`; no `fallback_reason` (none required).
- `resolved_by` equals the depended-on policy's `target_tool` in all four edges; each `gate` names a real binding of the blocked compute (`on_hand`, `pending`, `on_hand`, `lost_days`) whose value the resolving write changes (demonstrated per task).
- `condition`s: bridge/vacation paper-claim edges = "every retail_dmr_submitted row … has a retail_dmr_approved or retail_dmr_denied row" — same strength as the sentences. vacation→bridge condition matches its sentence. lost_stolen→dose_change condition ("when a quantity-limit approval raising the drug's quantity per 30 days took effect after the most recent fill … a dose_change override … granted on or after that fill") is narrower than the sentence's "every dose increase recorded on the drug" only in the case of a still-pending QL exception case (is a pending request a "recorded dose increase"?) — observation O-3; no task world contains a pending QL case.
- No authoring-viewpoint phrasing in any `prerequisite` field.

### prerequisite_sentences

| edge | sentence (blocked rule) | four-point test | the one write bringing the state about | derivation |
| --- | --- | --- | --- | --- |
| bridge ← paper_claim | "The review bridge is not worked out until every paper claim filed on the benefit for the drug under review carries its decision." | ordering "not … until" ✓; record state (decision rows on submissions) ✓; no tool/id/snake_case ✓; strength = condition ✓ | approve_paper_claim_1f52e397 (the difficulty has no denial tool) | reader sees an undecided submission → paper-claim policy's own rule ("A paper claim awaiting its decision is approved on the submission it decides…") → approval |
| vacation ← bridge | "The vacation supply is fixed only after the benefit carries an emergency supply for the drug for each of its coverage reviews still awaiting decision." | "only after" ✓; state (emergency_supply override row on the benefit) ✓; ✓; ✓ | grant_review_bridge_supply_635c815d (only tool writing override_type emergency_supply) | pending review case + no emergency override → bridge policy ("An emergency supply is granted only while a coverage review for that drug is pending…") → grant |
| vacation ← paper_claim | "A vacation supply is not sized until each paper claim on the benefit for the drug has been decided." | "not … until" ✓; state ✓; ✓; ✓ | approve_paper_claim_1f52e397 | as first row |
| lost_stolen ← dose_change | "A replacement for lost, stolen or damaged medication is sized only after the benefit carries a dose-change override for every dose increase recorded on the drug since its most recent fill." | "only after" ✓; state (dose_change override row) ✓; ✓; strength see O-3 | grant_dose_change_override_e9e89c2d | QL approval effective after the last fill + no dose_change override → dose-change policy ("A dose-change override is granted … for the drug of the member's most recent quantity-limit approval…") → grant |

- No rule carries a second wording, tool name or problem id for its dependency; no depended-on rule restates the dependent's sentence.
- No extended rule states a cross-problem order that grounds no declared edge. Base sentences with a cross-problem order ("A reimbursement may be paid only after its submission has been approved" in `retail_evt_dmr_payment`; "A refill that rejects as too soon is paid only under an override" in `retail_refill_too_soon`) ground no edge and no task tree rests on them (observation O-6).

### override_declarations

Sentence-by-sentence over each `base_policy_refs` entry:

- paper_claim vs `retail_evt_dmr`: receipt requirement, filing limit, run-out, denial reasons, receipt date, processing window, decide-once — inherited unchanged. OON clause — declared (overwrite #1); the extended rule re-states its eligibility half ("under emergency_only only for an urgent fill …; foreign purchases only when dmr_foreign_claims_covered is true"), so the merged meaning is unique. Pricing clause — declared (overwrite #2); cap at amount paid, less cost share, floor 0, minimum payment re-stated. **Undeclared:** the base phrase "less the member cost share the plan would have charged on that date" includes the deductible portion (base `retail_claim_cost_share`: "after any deductible portion, which the plan's deductible rule sets"); the extended member cost share has no deductible term (CG-3a).
- paper_claim vs `retail_claim_cost_share`: base "for 61 to 90 days, only where retail_90_allowed is true, it is multiplied by band_61_90_multiplier; a fill longer than max_days_supply_retail rejects". Extended "band_61_90_multiplier above 60 days" with no retail_90_allowed condition and no 90-day ceiling, and the "otherwise" days tier does not limit network/US fills to max_days_supply_retail. On Performance/Essential/National (retail_90_allowed false, band_61_90_multiplier 0.0) a 61+ reimbursed-day paper claim gets a tier copay × 0.0 = 0.00. Undeclared (CG-3b).
- paper_claim vs `retail_refill_too_soon`: base governs network adjudication (subject retail_claim_paid); extended applies the threshold/accumulation limit to paper-claim days (takes days off rather than rejecting). Different subject — no competing conclusion on one quantity.
- review_bridge vs `retail_evt_override`: emergency-supply days sentence declared and replaced verbatim in the rule; per-year quota, pending-review condition, validity, open-benefit gate inherited.
- vacation vs `retail_evt_override` (overwrite: []): lead time, per-year quota, controlled exclusion, validity, open-benefit gate inherited. **Undeclared:** base "for up to vacation_override_max_days_supply days"; the extended ceiling tier 1 is pending_review_vacation_days = 60, which exceeds vacation_override_max_days_supply = 30 on Performance, Essential and National networks (CG-4).
- dose_change vs `retail_evt_override`: base sets eligibility only ("granted when dose_change_override_allowed is true and the new prescription at the higher dose is on file"), no days figure — no conflict.
- lost_stolen vs `retail_evt_override`: per-year quota and controlled/police-report gates inherited; no base days figure — no conflict.
- All five vs `retail_refill_too_soon`: no competing conclusion.
- Structural note (observation O-1): every extended rule states its baseline sentences and then the ladder sentences that refine them (e.g. "The reimbursed days of the paper claim are the days supply on the receipt." followed by "The reimbursed days of the paper claim depend on where the fill was bought: …"). Read literally the two give different values for a foreign receipt; the framework mandates this shape and the rules' own ordering sentences ("The steps run in this order…", "then nets…", "also taken off") resolve it in favour of the ladder. Not counted as a conflict.

### factor_ladders

| policy | factor | label | decides | tiers | label honest | tiers distinct | multi-source tiers | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| paper_claim | purchase_place_days | parameter | days_capped | 3 | yes | yes | tier 2 only (OON ∧ network emergency_only) | — |
| paper_claim | previous_fill_overlap | method | paid_days | 3 | yes | yes | yes (receipt date vs network claim) | — |
| paper_claim | allowed_amount_basis | method | allowed | 3 | yes (tier 1 changes the base from network rate to receipt amount) | yes | single-condition | — |
| paper_claim | accumulator_cost_share | parameter | cost_share | 3 | yes | yes | tier 2 (OOP not met ∧ insulin) | plan (category read; declared null) |
| review_bridge | case_opening_bridge | parameter | status_days | 3 | yes | **no on 4 of 6 networks** (urgent_bridge_days 3 = emergency_supply_days 3 on Performance/Essential/National/Preferred Savings) — CG-5 | same-record conjunction | review |
| review_bridge | information_request_extension | parameter | info_days | 3 | yes | yes | requests vs receipts (two event kinds) | review |
| review_bridge | home_delivery_extension | parameter | ship_days | 3 | yes | yes | yes (mail_prescriptions ∧ mail_accounts) | mail |
| review_bridge | on_hand_netting | method | bridge | 3 | **no** — one formula `max(0, horizon − on_hand)` | **no** — tier 3 ("the whole bridge horizon" when none remains) is tier 2 ("the bridge horizon less that supply") at supply 0 — CG-2 | — | — |
| vacation | held_fill_anchor | method | on_hand | 3 | yes (source-record selection incl. a "count nothing" tier) | yes | yes | — |
| vacation | authorised_supply_offset | method | pending | 3 | yes | yes | yes (override ∧ claims using it) | — |
| vacation | review_status_ceiling | parameter | ceiling | 3 | yes | yes on 5 networks; **tier 1 = fall-through on Preferred Savings** (60 = 60) — part of CG-4 | tier 1 (approval expired ∧ case pending) | review |
| vacation | recent_vacation_reduction | parameter | repeat_ded | 3 | yes | yes | single-record | — |
| vacation | carried_early_days | method | early_ded | 3 | yes (all vs beyond-grace) | yes | — | — |
| dose_change | re_dosed_fill_source | method | src_days | 3 | yes | yes | yes (mail shipment ∧/∨ retail claim reversal) | mail |
| dose_change | delivery_timing | parameter | transit | 3 | yes | yes | — | mail |
| dose_change | new_quantity_source | parameter | q_new | 3 | yes | yes | yes (authorization vs fill date) | review |
| dose_change | re_dosing_date | method | start_off | 3 | **no** — tiers pick a date (approval effective date / case opening date / today) substituted into the one shortfall formula; same conditions as new_quantity_source ("chosen the same way") — CG-6 | yes as values | — | review |
| dose_change | dose_change_end_share | parameter | share | 3 | yes | yes (0.85/1.0/0.75 on National) | — | review |
| dose_change | fill_length_sizing | method | dc_days | 3 | yes | yes | — | — |
| lost_stolen | lost_supply_source | method | lost_len | 3 | yes | yes | yes | mail |
| lost_stolen | arrival_timing | parameter | arrival | 3 | yes | yes | — | mail |
| lost_stolen | dosing_on_record | method | lost_days | 3 | **no** — tier 2 is stated as "re-counted **the same way**" as tier 1 (only the date and the quantity differ) — CG-7 | tiers 1 and 2 select the same method | — | review |
| lost_stolen | earlier_loss_reduction | parameter | loss_ded | 3 | yes | yes | — | — |
| lost_stolen | early_fill_override_share | parameter | repl_share | 3 | yes | yes | — | — |

Counts (declared → after the tests above):

- paper_claim: 4 declared (2 parameter, 2 method) → 4 survive.
- review_bridge: 4 declared (3 parameter, 1 method) → **3 survive, 0 method** (on_hand_netting struck, CG-2). Baseline also fails self-sufficiency (CG-8).
- vacation: 5 declared (2 parameter, 3 method) → 5 survive.
- dose_change: 6 declared (3 parameter, 3 method) → 6 factors; re_dosing_date's `method` label is dishonest (CG-6), leaving 2 honest method factors.
- lost_stolen: 5 declared (3 parameter, 2 method) → dosing_on_record's `method` label dishonest (CG-7), leaving 1 honest method factor.
- All ladders are stated in full in their `rule` and implemented in `compute`; every fall-through equals its policy's baseline for that input; every `decides` is an input binding (none decides `result`); binding sets are disjoint within each policy.
- Baselines: paper_claim, vacation, dose_change, lost_stolen baselines are self-sufficient. review_bridge's is not (CG-8).

### findings

- **CG-1 — SOURCE-POLICY RED (rule/compute equivalence), bears on task 1.** Symptom: dose_change and lost_stolen treat standard_shipping_business_days as calendar days. Evidence: rule (both policies) "they start the home delivery program's standard_shipping_business_days after the shipment date"; `products/mail.yaml` parameter_schema "standard_shipping_business_days: business days in transit for standard shipping after dispensing"; compute `transit: "CPARAM('mail', 'standard_shipping_business_days') if from_mail and m_ship == 'standard' …"` then `end_off: "transit - DAYS(src_dos, NOW) + …"` and `arrival` → `left_today: "arrival + lost_len - DAYS(lost_dos, NOW)"` (calendar days). Root cause: compute converts business days to calendar days one-for-one, a basis the rule does not state. Consequence demonstrated in 1.md.
- **CG-2 — SOURCE-FACTOR RED (unreal ladder / dishonest label), bears on task 0.** review_bridge `on_hand_netting` (only method factor of the policy). Rule: "when that supply covers the whole bridge horizon the review bridge is zero days; when some supply remains but less than the bridge horizon the review bridge is the bridge horizon less that supply; when none remains it is the whole bridge horizon." With supply 0, "the bridge horizon less that supply" = the whole bridge horizon: tiers 2 and 3 select the same method; tier 1 is the zero floor of the same subtraction. The factor is one method, `max(0, horizon − on_hand)`. Striking it leaves the policy 3 factors and 0 method factors (below 4 and below 1 method).
- **CG-3 — SOURCE-POLICY (undeclared override of base), charter-level; no task world is affected.** (a) The member cost share of a paper claim omits the deductible portion that base pricing ("the member cost share the plan would have charged on that date", with base cost share "after any deductible portion") includes — not named in `overwrite`. Situation: a Rx Value member (deductible 200, tiers 2–5) with deductible unmet files a tier-2 paper claim: base charges deductible + copay, extended charges the copay only. (b) Day-supply multiple "band_61_90_multiplier above 60 days" with no retail_90_allowed condition: a Performance-network member with a 75-reimbursed-day network-pharmacy paper claim gets tier copay × 0.0 = 0.00 under extended, while base says such a supply is not payable at retail (rejects above max_days_supply_retail 30). Not named in `overwrite`. Task 0 (Open Choice, Rx Plus with deductible 0 and OOP met) sits outside both situations; no task demonstrates a second answer from it.
- **CG-4 — SOURCE-POLICY (undeclared override of base), charter-level; no task world is affected.** vacation `overwrite: []`, yet the ceiling tier "the vacation ceiling is pending_review_vacation_days" (60) contradicts base `retail_evt_override` "A vacation supply may be granted … for up to vacation_override_max_days_supply days" on Performance/Essential/National (30). Same situation (expired approval + pending review on a National member): base caps at 30, extended allows up to 60. On Preferred Savings the same tier equals the fall-through (60 = 60). Task 0 is on Open Choice (max 90): no consequence there.
- **CG-5 — SOURCE-FACTOR (unreal ladder on some networks), charter-level; not on any task's world.** case_opening_bridge tier 1 value urgent_bridge_days = 3 equals the fall-through emergency_supply_days = 3 on Performance, Essential, National and Preferred Savings. Task 0 is on Open Choice (5), where the tiers differ.
- **CG-6 — SOURCE-FACTOR RED (mislabelled effect), bears on task 1.** dose_change `re_dosing_date` is labelled `method` but its tiers ("re-dose from the approval's effective date" / "from the date the case was opened" / "from today") only substitute a date (`start_off`) into one shortfall formula; its tier conditions are the new_quantity_source conditions ("The re-dosing date is chosen the same way"). Factor counts still hold (6 factors, 2 honest methods).
- **CG-7 — SOURCE-FACTOR RED (two tiers selecting the same method), bears on task 1.** lost_stolen `dosing_on_record` (`method`): tier 1 "the days of the lost supply left on the effective date … are re-counted at that approval's quantity per 30 days … and the days from that effective date to today are taken off"; tier 2 "the days left on the date the case was opened are re-counted the same way at the quantity it requests and the days from that date to today are taken off". Tiers 1 and 2 are one method with different date/quantity inputs (and the fall-through is that formula at the member's own dosing). As a `parameter` the factor would be honest; as labelled it is not. Counts still hold (5 factors, 1 honest method).
- **CG-8 — SOURCE-FACTOR RED (incoherent baseline), bears on task 0.** review_bridge `baseline.rule`: "The base bridge days are emergency_supply_days. The bridge horizon is the base bridge days plus the information extension of the bridge plus the delivery extension of the bridge. The review bridge is the bridge horizon." The two extensions are never given a value in the baseline; their zero defaults exist only in the factor ladders' fall-throughs (`info_days: "0"`, `ship_days: "0"`). A reader of the baseline alone gets emergency_supply_days + ? + ?, not a definite number.
- Observations: O-1 (baseline-then-ladder sentence shape, above); O-2 (`clm_dos` basis case mismatch); O-3 (lost_stolen sentence "every dose increase recorded" vs condition limited to QL approvals — pending QL case unresolved); O-4 (vacation offset tier 2 omits the seven-day window "such" may imply); O-5 (docstrings contain "after the call" / business "before" wording, no inter-tool order); O-6 (base cross-problem orders ground no edge).

## closing_checklist

(Written after both tasks' reveals — see below this line once appended.)

### closing status (appended 2026-10-08 after both reveals; nothing above this line was changed by the reveals)

The difficulty does **not** close: Step 4's checklist requires all four relationships to PASS for every task, and neither task does.

- Per-task files: 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json; this is revision 1 (no older revision existed).
- Scope: the reveals confirm charter_scope task 0 = {paper_claim, review_bridge, vacation}, task 1 = {dose_change, lost_stolen}. They are pairwise disjoint and jointly cover all 5 extended policies and 5 task tools.
- Trees: task 0 has n = 2 prerequisite problems and 3 value_input edges; task 1 has n = 1 and 1 value_input edge. Each has a user-owned root, and both are acyclic. Across the difficulty the edges form a DAG (two components).
- Factors: task 0 fails (CG-2, CG-8, both in the bridge computation). Task 1 fails on labels (CG-6, CG-7) and on false tier grounds in factor_sensitivity.
- Unique solution: task 0 passes (the blind derivation equals GT on every write). Task 1 fails (CG-1: 39/9 vs 40/10).
- Charter-level findings no task's world exercises (they stay on record): CG-3, CG-4, CG-5.
- Gates were not re-run by this audit. The skill leaves gate execution to the orchestrator, and the brief's snapshot is cited in § charter_global_frozen.

| task | policy self-consistency | problem tree | factors | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | SOURCE-FACTOR RED | PASS | RED (SOURCE-FACTOR) |
| 1 | SOURCE-POLICY RED (CG-1) | PASS | SOURCE-FACTOR RED | SOURCE-TASK RED | RED (SOURCE-TASK, SOURCE-POLICY, SOURCE-FACTOR) |

## revision_2

### charter_global_frozen (revision 2)

- Trigger: re-audit round 2 after rework. Both shared inputs changed, so every charter-global section below is re-derived in full; the revision-1 text above is left untouched.
  - `retail.extended.yaml`: 6a10f8d4… → **ad4a29ae97c6e85fda20e78bf861e35935f74da6468c3938f9d2e13f39fa50f0**.
  - `task_tools.py`: 86d4193e… → **2303bb10b081ee051ef4d0f6aa9c0058f65f765c1a3e56e60c58dcc9e371f0ab**.
  - Views unchanged (44145a03…, bb9d699a…). Blueprint product files and db_schema were not part of the rework.
- Freeze: 2026-10-08 ~08:30 UTC, before either rebuilt `tasks/*.json` was opened. Same masking as revision 1; worklog.md not read.
- Entry conditions: the brief's post-rework gate snapshot is all green (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; traceability deferred), and the view hashes re-check.
- Base copy is still verbatim (diff against `products/retail.yaml` = trailing blank line only).
- Mechanical sweep (re-run on the new charter):
  - every `compute_basis` quotation is in its rule, with no case mismatch left;
  - every baseline sentence is in its rule;
  - every `replaced_by` is in its rule;
  - every prerequisite `policy_source` is verbatim in the blocked rule, and every `resolved_by` equals the depended-on `target_tool`;
  - every compute binding has a basis.

### policy_conflict_scan (revision 2)

- Unchanged structure: 5 extended policies, 5 tools, 4 state-form value_input edges (bridge←paper_claim, vacation←bridge, vacation←paper_claim, lost_stolen←dose_change), acyclic.
- Each `(target_tool, computes)` is still claimed by exactly one policy.
- Subjects, cross-reads and time anchors as in revision 1. No two extended policies compete for one quantity.

### rule_compute_equivalence (revision 2)

- paper_claim: new day-supply multiple (ceil(days/30) when retail_90_allowed is false), deductible portion, copay capped at allowed − deductible, coinsurance on allowed − deductible, insulin tier — all stated in the rule and implemented (`units`, `ded_left`, `ded_part`, `tier_cs`, `cost_share`). Equivalent.
- review_bridge: new on-hand anchor (approved paper claim later than every network claim / reversed latest network claim → 0 / network claim) and `bridge: MX(0, horizon − on_hand)` match the rule. Equivalent.
- vacation: ceiling tier 1 is now `int(max × pending_review_vacation_share)`, stated in the rule as "rounded down to whole days". The closing sentence still says "every quantity is in whole days with no rounding" (O-7). On every network the result is unchanged, since the share is applied once and floored.
- dose_change / lost_stolen: standard shipments now start "standard_arrival_days calendar days after the shipment date" (K = 9), and expedited ones "expedited_transit_days calendar days". The rule states the unit, so compute adds no unstated basis. **CG-1 closed.** Remaining point: the 9 days are fixed for every home delivery program, while the mail product's own standard transit is 3–7 business days (O-9).

### action_binding_and_uuids (revision 2)

- uuid8s are unchanged and distinct (1f52e397, 635c815d, 35815dad, e9e89c2d, dcea41b5).
- Bodies still only find/create/update; no refusal path.
- Docstrings no longer contain before/after/first/then/prior (word-boundary grep empty). **O-5 closed.**

### prerequisite_graph and prerequisite_sentences (revision 2)

- The three task-0 edges' sentences and conditions are unchanged, and the four-point test still passes.
- The lost_stolen edge sentence now reads "A replacement for lost, stolen or damaged medication is sized only after the benefit carries a dose-change override for every quantity-limit approval that raised the drug's quantity since its most recent fill." It has the same scope as the condition (a pending QL case is no longer arguably included) and names records in the tables' words. **O-3 closed.**
- Exactly one write brings each waited-on state about: the approval, the emergency-supply grant, the dose-change grant.
- No rule states an undeclared cross-problem order. O-6 (base orders ground no edge) is unchanged.

### override_declarations (revision 2)

- **CG-3b closed:** a new overwrite on `retail_claim_cost_share` names the superseded clause ("for 61 to 90 days, only where retail_90_allowed is true, … a fill longer than max_days_supply_retail rejects.") and its replacement (above 60 days: band_61_90_multiplier where retail_90_allowed, else one 30-day cost share per 30 days or part); the replacement is verbatim in the rule.
- **CG-3a closed as reported, with a new defect in its place (CG-9):** the member cost share now carries a deductible portion. But the rule's own deductible remaining — "the plan's individual deductible, or its family deductible for any coverage level other than employee only, less the deductible met on the member's active plan enrollment" — is not the plan's deductible rule that base `retail_claim_cost_share` defers to ("after any deductible portion, which the plan's deductible rule sets").
- **CG-4 closed:** ceiling tier 1 = vacation_override_max_days_supply × 0.67, rounded down (20 / 40 / 60 for max 30 / 60 / 90). It is never above the base "for up to vacation_override_max_days_supply days" and never equal to the fall-through.
- **New finding CG-10** (pre-existing in revision 1, missed by the round-1 audit): the tier cost share on a coinsurance tier is "the tier coinsurance rate multiplied by the allowed amount … less its deductible portion". `plan_cost_share` raises that to the per-fill minimum and lowers it to the per-fill maximum ("raised to the per-fill minimum and lowered to the per-fill maximum where those are non-zero"). Not named in `overwrite`.
- Everything else as in revision 1 (inherited eligibility, declared OON/pricing/emergency-days overrides, no conflict for dose_change/lost_stolen).

### factor_ladders (revision 2)

| policy | factors (label) | change since rev 1 | verdict |
| --- | --- | --- | --- |
| paper_claim | purchase_place_days (P), previous_fill_overlap (M), allowed_amount_basis (M), accumulator_cost_share (P: 0 / ded + min(insulin cap, tier) / ded + tier) | cost-share tiers now include the deductible | 4 factors, 2 P, 2 M; distinct tiers; baseline self-sufficient |
| review_bridge | case_opening_bridge (P: max(1, emergency_supply_days − 2) / 7 / emergency_supply_days), information_request_extension (P), home_delivery_extension (P), **bridge_supply_anchor** (M: paper-claim fill / reversed latest claim → 0 / latest network claim) | on_hand_netting replaced by bridge_supply_anchor; urgent tier now emergency − 2 | 4 factors, 3 P, 1 M. bridge_supply_anchor is the same source-record ladder accepted for vacation's held_fill_anchor in rev 1, with a distinct "count nothing" tier. Urgent tier differs from the fall-through on every network (1 vs 3, 3 vs 5). **CG-2, CG-5 closed.** Baseline now says "The information extension of the bridge and the delivery extension of the bridge are zero days." and nets the latest network claim's days, so it gives a definite number. **CG-8 closed.** |
| vacation | as rev 1; review_status_ceiling tier 1 = max × 0.67 | share replaces the fixed 60 | 5 factors, 2 P, 3 M; tier 1 ≠ fall-through on all networks |
| dose_change | re_dosed_fill_source (M), delivery_timing (P: 9 / 2 / 0), new_quantity_source (P), **re_dosing_date (P)**, dose_change_end_share (P), fill_length_sizing (M) | re_dosing_date relabelled parameter | 6 factors, 4 P, 2 honest M. **CG-6 closed.** re_dosing_date still shares its tier conditions with new_quantity_source (O-8); counted as one factor this would still leave 5 |
| lost_stolen | lost_supply_source (M), arrival_timing (P), **dosing_on_record (P)**, earlier_loss_reduction (P), early_fill_override_share (P) | dosing_on_record relabelled parameter; tier 2 text no longer says "the same way" | 5 factors, 4 P, 1 M. **CG-7 closed.** |

- Every ladder is stated in its rule and implemented. Fall-throughs equal baselines. `decides` are inputs, and bindings are disjoint.
- All five baselines are self-sufficient:
  - paper_claim: receipt days, network rate, deductible, tier cost share;
  - bridge: emergency_supply_days + 0 + 0 − network on hand;
  - vacation, dose_change, lost_stolen: as in revision 1.

### findings (revision 2)

Status of round-1 items:

| item | claimed | verified |
| --- | --- | --- |
| CG-1 | closed | **closed**: rule now states calendar days; one reading |
| CG-2 | closed | **closed**: netting is no longer a factor; replacement method factor passes |
| CG-3a | closed | **closed as stated**, but the new deductible clause is CG-9 |
| CG-3b | closed | **closed** (declared overwrite) |
| CG-4 | closed | **closed** |
| CG-5 | closed | **closed** |
| CG-6 | closed | **closed** (label honest; O-8 remains) |
| CG-7 | closed | **closed** |
| CG-8 | closed | **closed** |
| O-2 | closed | **closed** |
| O-3 | closed | **closed** |
| O-4 | closed | **closed**: vacation offset tier 2 now "the most recent emergency supply for the drug has already been used by a claim" |
| O-5 | closed | **closed** |
| O-1, O-6 | no change | unchanged (structural / base orders; observations) |

New defects:

- **CG-9 — SOURCE-POLICY (undeclared override of the plan deductible rule), charter-level, introduced by the rework; no task world is affected.**
  - Evidence:
    - The paper-claim rule: "the deductible remaining (the plan's individual deductible, or its family deductible for any coverage level other than employee only, less the deductible met on the member's active plan enrollment)".
    - `plan_deductible`: "for any other coverage level the family amount applies as set out in plan_agg_family_accumulation".
    - `plan_agg_family_accumulation`: "When deductible_embedded is true, a member's deductible is met at the lower of reaching deductible_individual on their own postings or the family reaching deductible_family".
    - The plan rule also exempts the Preventive Drug List when preventive_list_bypasses_deductible; the extended clause has no such exemption.
  - Same situation, two conclusions: a Rx Value member (individual 200, family 600, embedded) on employee_plus_family coverage, own deductible_met 150, family YTD 300, files a tier-2 paper claim allowed 400.
    - Plan rule: remaining = min(200 − 150, 600 − 300) = 50.
    - Extended: 600 − 150 = 450.
  - Task 0 (employee_only, Rx Plus with no deductible tiers) does not reach it.
- **CG-10 — SOURCE-POLICY (undeclared override of the plan's coinsurance min/max), charter-level, present since revision 1 and missed then; no task world is affected.**
  - Situation: Rx Value tier 4 (rate 0.25, min 125, max 350), paper claim allowed 300 after deductible.
  - Plan: max(75, 125) = 125. Extended: 75.
  - Task 0's receipt is tier 2 copay.
- Observations:
  - **O-7:** vacation "rounded down" vs "with no rounding".
  - **O-8:** re_dosing_date / new_quantity_source share one condition set.
  - **O-9:** standard_arrival_days 9 is fixed across home delivery programs whose own standard transit is 3–7 business days. Under the Standard program (7 business days) it matches the business-day count for a mid-week shipment.

### closing status (revision 2, appended after both revision-2 reveals)

The difficulty still does **not** close.

- Task 1 carries R2-1 (SOURCE-FACTOR, false factor_trace figures 29R / 17L in tasks/1.json).
- The charter carries two new charter-level SOURCE-POLICY defects that no task's world exercises:
  - **CG-9:** the paper-claim deductible remaining is not the plan's embedded/family rule, and has no preventive-list exemption. Introduced by the CG-3a rework.
  - **CG-10:** the coinsurance tier cost share ignores the plan's per-fill min/max. Pre-existing; missed in round 1.
- Every round-1 RED and the claimed observations (CG-1…CG-8, O-2…O-5) are verified closed. O-1 and O-6 are unchanged. No round-1 PASS regressed on either task's world.

Checklist items that do hold:
- One file per task plus this file. Revision 1 is preserved, with revision 2 appended.
- Scopes are disjoint and complete (5 policies, 5 tools).
- Trees:
  - task 0: n = 2, 3 value_input edges, root user-owned;
  - task 1: n = 1, 1 value_input edge, root user-owned;
  - the difficulty-wide graph is a DAG.
- Factor counts within bounds with honest labels:
  - paper_claim 4 (2P/2M); bridge 4 (3P/1M); vacation 5 (2P/3M); dose_change 6 (4P/2M); lost_stolen 5 (4P/1M);
  - each task has ≥1 multi-source and ≥1 cross-difficulty factor with seeded rows;
  - every factor bears weight against a self-sufficient baseline whose fall-back differs from gold (853.40 / 5 / 90 / 30 / 0).
- uuid8s are independent and frozen.
- Gates: not re-run by this audit. The brief's post-rework snapshot is all green, with traceability deferred.

| task | policy self-consistency | problem tree | factors | unique solution | verdict (rev 2) |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | SOURCE-FACTOR RED (R2-1) | PASS | **RED (SOURCE-FACTOR)** |
| charter | SOURCE-POLICY (CG-9, CG-10), no task consequence | — | — | — | open |

## revision_3

### charter_global_frozen (revision 3)

- Trigger: re-audit round 3.
  - `retail.extended.yaml` changed: ad4a29ae… → **40c6a61395ebb5e7b05cedba3540399a24e34ab9f742f7b69fe836fe486d97ae**.
  - `task_tools.py` unchanged (2303bb10…), so § action_binding_and_uuids (revision 2) is **carried forward by reference** on that hash.
  - Charter-dependent sections are re-derived below.
  - Views unchanged (44145a03…, bb9d699a…).
  - plan / retail / mail / review product hashes are unchanged from revision 2 (cd9d6e2c…, d45b9fb4…, 45c05b73…, 64105c14…).
- Freeze: 2026-10-08 ~10:05 UTC, before the rebuilt tasks/*.json were opened. worklog.md not read.
- Entry conditions: the post-rework gate snapshot in the brief is all green (traceability deferred).
- Base copy is still verbatim.
- Mechanical sweep, re-run:
  - every compute_basis quotation, baseline sentence and replaced_by is in its rule;
  - every **superseded_clause is verbatim in its base policy's rule** (all 5);
  - every prerequisite policy_source is verbatim in the blocked rule, with resolved_by = the depended-on target_tool;
  - every binding has a basis.

### What changed in the charter (located by reading all five policies)

- paper_claim:
  - (a) a fourth overwrite on `retail_claim_cost_share` supersedes "A retail claim starts from the 30-day cost share the member's Pharmacy Benefit Plan sets for the drug's formulary tier (after any deductible portion, which the plan's deductible rule sets)." It is replaced by an own-member deductible: individual deductible less the member's deductible_met, on deductible tiers, insulin exemption honoured, "neither the family accumulation nor the Preventive Drug List exemption of the plan's deductible rule is applied to it". Compute `ded_left` is now individual-only.
  - (b) The coinsurance tier now reads "raised to the tier's per-fill coinsurance minimum and lowered to its per-fill coinsurance maximum where those are not zero, and never more than the allowed amount … less its deductible portion". Compute has `tier_min`, `tier_max`, `coins_low`, `coins_cap`, equivalent to `plan_cost_share`'s formula on (allowed − deductible).
- vacation: the closing sentence now reads "every quantity is in whole days; apart from rounding the pending-review ceiling down, nothing is rounded." It no longer contradicts the ceiling tier.
- dose_change / lost_stolen: standard shipments now start "the home delivery program's standard_shipping_business_days plus weekend_allowance_days, counted as calendar days, after the shipment date". `weekend_allowance_days` = 2 in both policies; compute is `CPARAM('mail','standard_shipping_business_days') + K('weekend_allowance_days')`. The sentence fixes the unit ("counted as calendar days"), so it has one reading: 7 + 2 = 9 calendar days on Home Delivery Standard, and 5 / 5 / 3 + 2 on the other programs. The arrival now tracks the program's own transit.
- review_bridge: unchanged in substance.

### Re-derived checks

- policy_conflict_scan: structure unchanged (5 policies, 5 tools, 4 state-form value_input edges, acyclic, one claimant per (tool, computes)).
- rule_compute_equivalence: equivalent for all five policies; the new deductible, coinsurance and arrival clauses are each stated and implemented as quoted above.
- prerequisite_graph / prerequisite_sentences: sentences unchanged from revision 2; four-point test passes; one resolving write per waited-on state.
- override_declarations:
  - Every deviation found so far is now named in an `overwrite`, or does not deviate:
    - CG-3b and CG-9 → overwrites #3 and #4;
    - CG-10 → removed (min/max now applied).
  - The family-OOP point (O-11 below) falls under overwrite #2, which supersedes the whole base pricing clause, including "the member cost share the plan would have charged on that date".
- factor_ladders: factor sets, labels and tier counts are as in revision 2. In detail:

| policy | factors | P/M |
| --- | --- | --- |
| paper_claim | 4 | 2P/2M |
| bridge | 4 | 3P/1M |
| vacation | 5 | 2P/3M |
| dose_change | 6 | 4P/2M |
| lost_stolen | 5 | 4P/1M |

  - delivery_timing / arrival_timing tier 1 is now the mail program's business days + 2 calendar days. Across programs it differs from tier 2 (expedited 2) and from the fall-through (0). Baselines are self-sufficient.

### findings (revision 3)

Status of round-2 charter items and observations:

| item | claimed | verified |
| --- | --- | --- |
| CG-9 | closed as declared overwrite | **closed** as a retail-side deviation: the base sentence that delegated the deductible to the plan's deductible rule is named and replaced, and the merged meaning is unique. Residual cross-category effect recorded as CG-11 |
| CG-10 | closed | **closed** |
| O-7 | closed | **closed** |
| O-9 | closed | **closed**: arrival = program's standard business days + 2, counted as calendar days |
| O-8, O-1, O-6 | no change | unchanged (observations) |

New:

- **CG-11 — observation (charter-level, no task world reaches it): the declared own-member deductible still posts to the plan ledger under the plan's family rules.**
  - The approval event triggers `plan:plan_ded_post` with the paper claim's deductible_amount (base event `retail_dmr_approved`).
  - `plan_agg_family_accumulation` says "A family member's posting never exceeds the family amount remaining", and `plan_deductible` says preventive-list drugs "skip the deductible".
  - Example: an employee_plus_family Rx Value member (individual 200, family 600, embedded), own met 150, family YTD 580. The extended rule gives a 50.00 deductible portion, so the family total would reach 630 > 600.
  - A retail-side `overwrite` cannot supersede a plan-category rule. Neither task's world has family coverage or a deductible portion (task 0: Rx Plus, no deductible tiers; task 1: no paper claim). Recorded as a cross-category observation: it changes no scored value in this difficulty.
- **O-11 — observation:** the paper claim zeroes the member cost share only at the individual OOP maximum, not when the family reaches oop_max_family (`plan_agg_family_accumulation`: "Out-of-pocket is always embedded…"). This is covered by overwrite #2 (the base "member cost share the plan would have charged" clause is superseded in full). No task world has family coverage.

## closing_checklist (revision 3 — appended after both revision-3 reveals)

All M = 2 tasks PASS on all four relationships in revision 3. The difficulty passes the source-layer audit.

- **Files:**
  - 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json, with this file alongside.
  - Revisions 1, 2 and 3 are preserved, each appended below the previous one.
  - Every task file's latest comparison carries PASS.
- **Coverage and scope:**
  - All 5 extended policies are covered.
  - charter_scope: task 0 = {paper_claim, review_bridge, vacation}; task 1 = {dose_change, lost_stolen}. Pairwise disjoint, each spanning its whole tree.
  - The task tools and GT are closed (every GT write calls one of the 5 tools with the target_tool's owner).
  - Each tool has an independent, frozen uuid8 (1f52e397, 635c815d, 35815dad, e9e89c2d, dcea41b5).
- **Problem trees:**
  - task 0: 2 prerequisite problems, 3 value_input edges ≥ 1, root owner=user (request_vacation_supply);
  - task 1: 1 prerequisite problem, 1 value_input edge ≥ 1, root owner=user (report_lost_stolen_replacement);
  - no cycles; the difficulty-wide prerequisite graph is a DAG of two components.
- **Factors:**

| computation | factors | P/M | baseline.rule alone | gold |
| --- | --- | --- | --- | --- |
| paper_claim | 4 | 2P/2M | 853.40 | 520.27 |
| review_bridge | 4 | 3P/1M | 5 | 14 |
| vacation | 5 | 2P/3M | 90 | 16 |
| dose_change | 6 | 4P/2M | 30 | 40 |
| lost_stolen | 5 | 4P/1M | 0 | 10 |

  - Every ladder has 3 tiers stated in its rule, distinct in outcome, with conditions and outcomes that line of business holds.
  - Each task has ≥1 multi-source factor (home_delivery_extension / review_status_ceiling; re_dosed_fill_source / lost_supply_source) and ≥1 cross-difficulty factor with seeded rows (review, mail).
  - Every factor bears weight on its task's world against an honest baseline, and every baseline alone gives a definite number different from gold.
- **Gates on the final form:** the orchestrator's post-rework snapshot (on charter 40c6a613…, tools 2303bb10…) is EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK. check_traceability is deferred to the render stage. This audit cites the snapshot and does not run gates itself.
- **Open observations (no demonstrated consequence on any scored solution; not grounds for rework under this skill):**
  - O-1: baseline-then-ladder sentence shape;
  - O-6: base cross-problem orders ground no edge;
  - O-8: re_dosing_date / new_quantity_source share one condition set;
  - O-11: paper claim zeroes cost share only at the individual OOP maximum;
  - O-12: stale round-2 note in tasks/1.json design_rationale;
  - task 1 item 6: "prescription on file" rests on the persona;
  - **CG-11**: the declared own-member paper-claim deductible would post to the plan ledger past the plan's family-deductible and preventive-list rules for a family-coverage or preventive-drug member. Cross-category, and outside both task worlds. The KB-render and scenario-level stages should be aware of it.

| task | policy self-consistency | problem tree | factors | unique solution | verdict (rev 3) |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | PASS | PASS | **PASS** |

## revision_4

### charter_global_frozen (revision 4)

- Trigger: round 4, a tool-implementation-only rework. The whole-scenario validator rejected `from datetime` in task_tools.py; the rework replaced it with an in-module pure date helper.
- Hashes:
  - `retail.extended.yaml` 40c6a613… — **unchanged**.
  - `task_tools.py` 2303bb10… → **fe5faf0a4bdbed2b82250b1aa8477c42c023d54484c18e8de094af62a2ee064a**.
  - Views unchanged (44145a03…, bb9d699a…).
- Carried forward by reference on the unchanged charter hash 40c6a613…, from revision 3: policy_conflict_scan, rule_compute_equivalence, prerequisite_graph, prerequisite_sentences, override_declarations, factor_ladders and findings (CG-11, O-1, O-6, O-8, O-11, O-12). None of these reads the tool module's bodies.
- Re-derived below, because the tool module changed: action_binding_and_uuids, and the runnable tool effects.
- Freeze: 2026-10-08 ~12:20 UTC, before the rebuilt tasks/*.json were opened. worklog.md not read.

### action_binding_and_uuids (revision 4)

- Module surface (AST):
  - the only import is `from erlbench import ToolContext, tool`; no datetime, time, random or uuid;
  - one new private class `_Calendar.plus_days(stamp, days)`;
  - five tools with unchanged names, decorators (`owner`, `rw="write"`) and parameter lists;
  - uuid8s unchanged and distinct (1f52e397, 635c815d, 35815dad, e9e89c2d, dcea41b5);
  - docstrings still contain no before/after/first/then/prior (word-boundary grep empty), consistent with the orchestrator's AST comparison.
- Bodies (AST-unparsed, docstrings stripped) are line-for-line the revision-1/2/3 bodies, with one exception: the four override tools compute `valid = _Calendar.plus_days(today, 7)` instead of `(date.fromisoformat(today) + timedelta(days=7)).isoformat()`, and `today` still comes from `ctx.now()[:10]`.
  - No body reads another problem's rows to refuse, errors on an unmet prerequisite, or computes a policy amount.
  - The tool layer still judges no prerequisite.
- **Helper equivalence:** `_Calendar.plus_days` was checked against `datetime.date + timedelta` (in the audit's own scratch script, not in the artifact). The check covered every start date from 1999-01-01 to 2031-12-31 with offsets {0, 1, 7, 28, 31, 60, 365, 366}: 96,424 cases, **0 mismatches**, including leap years, 2100 (not a leap year), month and year rollovers. The helper only ever receives +7 from the tools.
- The policy requirement the helper serves is base `retail_evt_override` "Each override is valid through the seventh calendar day after it is granted, the grant date being day zero". plus_days(today, 7) is exactly that.

### closing_checklist (revision 4 — appended after both revision-4 reveals)

- The round-4 change is confined to the tool implementation. `_Calendar.plus_days` reproduces calendar addition exactly over the tested domain (96,424 cases, 0 mismatches). Every tool still writes exactly the rows, fields and dates the policy and GT require (replayed in 0.md and 1.md § revision_4). Names, signatures, owners, uuid8s and docstrings are unchanged, and the tools still judge no prerequisite.
- No round-3 RED existed. Nothing regressed: GT writes, baselines and factor figures of both tasks are identical to revision 3.
- The revision-3 closing checklist stands, carried forward on charter hash 40c6a613…. The tool-related lines are re-confirmed on tools fe5faf0a….
- Gates on the final form, per the orchestrator's snapshot: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / TRACEABILITY / SCOPE OK, and validate_scenario VALID. This audit cites the snapshot and does not run gates itself.
- Open observations are unchanged from revision 3 (CG-11, O-1, O-6, O-8, O-11, O-12, task 1 item 6). None has a demonstrated consequence on a scored solution.

| task | policy self-consistency | problem tree | factors | unique solution | verdict (rev 4) |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | PASS | PASS | **PASS** |

The difficulty passes the source-layer audit.

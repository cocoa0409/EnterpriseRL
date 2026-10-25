# Policy-task audit — insurance_claims_and_denials / charter-global

## revision_1

## charter_global_frozen
- Freeze: 2026-10-20 14:51 UTC (written before any task GT field was opened). Auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiator.
- Hashes (sha256, first 12): `claim.extended.yaml` 74495b18d633, `task_tools.py` 1aabaeab0e6f (both match the coordinator gate snapshot). Views: `0.view.json` 39a89ff9d428b838, `1.view.json` 8ef0045aea4a8726 (match brief).
- Read: blueprint/blueprint products `claim.yaml` (base), `encounter.yaml` (variant parameters, lifecycle, prompt-pay/liability policies for cross-category seed checks), `db_schema.json`, `share_tools.py` (function list), `claim.extended.yaml`, `task_tools.py`, the two masked views, `audits/render_source/XF_recipe.md`, `skills/erl-task-instantiate/scripts/check_compute.py` (DSL primitive semantics only; I evaluated the charter's own `compute` on the view worlds with it, gates were not run).
- Masked / not read before freeze: `tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure*), `worklog.md`, `/tmp/*_0073/`, any other scenario or difficulty directory. No recursive grep touched `tasks/`. contamination_disclosure: none.
- Entry conditions: gate snapshot (7 gates green, check_traceability deferred) and masked views with hashes were supplied in the brief; accepted as entry evidence, not re-run.
- Base section: every top-level key of the extended file except `extended_policies` is byte-equal (parsed) to `blueprint/products/claim.yaml`. Every `superseded_clause` is a verbatim sentence of the named base rule; every `replaced_by` and every `compute_basis` quote is a verbatim substring of its policy's `rule`; every `baseline.rule` sentence is in its `rule`; every prerequisite `policy_source` is verbatim in the blocked policy's own `rule` (scratch sweep /tmp/audit_claims_0073/cb.py).

Policy shorthand used below: P1 `claim_ext_unauthorized_implant_closeout`, P2 `claim_ext_small_lab_item_closeout`, P3 `claim_ext_noncovered_convenience_closeout`, P4 `claim_ext_member_decision_closeout` (root, owner=user), P5 `claim_ext_retrospective_denial_refund`, P6 `claim_ext_unauthorized_imaging_closeout`, P7 `claim_ext_self_administered_drug_closeout`, P8 `claim_ext_external_review_decision_closeout` (root, owner=user).

### policy_conflict_scan
- Subjects: P1, P2, P3, P4, P6, P7, P8 all write `claim_denial_written_off` (one row, carc copied from `insurance_claims.denial_carc`); P5 writes `claim_takeback`. The base dedup eligibility `claim_denial_write_off.one_write_off_per_reason` ("The same denial reason is written off once per write-off reason on a claim", distinct_fields [carc_code, writeoff_reason]) is overwritten by no policy and stays in force.
- Pairs writing the same (carc, writeoff_reason): P1/P6 (NO_AUTHORIZATION_OBTAINED), P3/P7 (NONCOVERED_NO_WAIVER), P4/P8 (APPEALS_EXHAUSTED). Their triggers overlap: P1 and P6 both fire on any denied, non-emergency claim whose account bills 0278 and 0350 lines (P6 additionally needs a recovery); P3 and P7 on a denied claim with a payer payment whose account bills both the convenience list and 0637; P4 and P8 on any denied commercial/Marketplace claim whose appeal count reaches `appeal_levels_available` inside the external-review window — the claim of task 0 and the claim of task 1 both satisfy both P4's and P8's gate (see findings C1, C2).
- Lab items on an Observation Stay Account: P2 says they "are part of the stay's per-diem and carry no separate value"; P5 says the laboratory tests are retained diagnostics "which its payer agreements keep payable as outpatient diagnostics" and values them; P8 says they "stay payable" (finding C7).
- Time anchors: P8's external-review window (whole calendar months from `denial_date`, day-number convention) matches `MONTHS` in the DSL and base `claim_appeal_windows`; P2's overwrite of the BELOW_APPEAL_THRESHOLD/open-window clause is scoped to lab items and member-level windows only.
- Cross-category read boundary: every policy reads only `encounter_accounts` (CFIELD/CPARAM by the claim's `encounter_id`) and `encounter_transactions` charge postings of that account (XSUM/XCOUNT filtered by `encounter_id`); no policy writes outside `claim_transactions`/`insurance_claims` (XF E23: `claim_denial_written_off` and `claim_takeback` have `triggers: []`).
- Terminal states: every tool leaves `insurance_claims.status` unchanged and only moves `payer_balance`; every write-off policy leaves "the contractual remainder, which Riverbend's month-end contractual close posts on the last calendar day of the month" on the claim (observation O3).
- Scope exclusivity (from the prerequisite graph, pre-reveal): tree A = {P4 ← P1, P2, P3}; tree B = {P8 ← P5, P6 ← P5, P7}. The two trees are disjoint and together cover all eight extended policies. Whether each task claims exactly one tree is compared after reveal in the task files.

### rule_compute_equivalence
Swept every binding of P1–P8 against its `compute_basis` quote and back. Verbatim quoting holds everywhere (P2 binding `pct` alone has no `compute_basis` entry — O1). Non-equivalences found (all listed; details in findings):
- P4 `implant_booked` = any NO_AUTHORIZATION_OBTAINED write-off on the claim; rule: "leaves out the implant charges (revenue code 0278) once an unauthorized-implant write-off entry stands on the claim" (C3).
- P2 `per_code_value` omits the value of laboratory codes not on the schedule; rule: "each laboratory code and the specimen collection code is tested on its own" (C4).
- Hidden revenue-code filter 0636 on HCPCS codes the rule names without a revenue code: P6 `contrast_charges`, `contrast_units`, `contrast_method`, `contrast_rate` (Q9967); P8 `imaging_charges` (Q9967), `heparin_charges`, `heparin_units`, `heparin_unit_fee` (J1644) (C5).
- P8 `closeout_value` sums only G0378, J1644, 96365, 0250, 0270/0272 and imaging; rule/baseline: the close-out "covers the services of the claim's hospital account that the denial reached and that no other route closes ... The close-out value is the charges it covers multiplied by the payer class's expected allowed percentage" (C6).
- Edge inputs (XF B6): zero units, absent recovery, empty denial_date, negative refund, 0.00 results are each stated and implemented. Rounding (B10): every rule says "rounded to the nearest cent once, on the final total" and every compute applies one `RND(...,2)` on `result`. Month counting (B8): P8 states the day-number convention `MONTHS` implements. Same-day ties (B7): no LATEST is used; the refund tool's choice of `pays[0]` among several payment remittances has no rule sentence (O4).

### action_binding_and_uuids
- Eight `(target_tool, amount_usd)` pairs, each claimed by exactly one policy. Tool bodies: each write tool calls `ctx.create` + `ctx.update` in its own body, checks no condition (module docstring and bodies), imports only `erlbench`; helper is a class static method (XF E18). Docstrings: no example values, no other tool named, the only ordering word is "after the posting" (balance description). Single-value args only (E22). No factor id is a substring of a tool name (E20).
- uuid8s 819e3af9, 1ab4cd54, 58e216c4, 7cc13d5d, 9b1903be, 395b7f3f, 664aab61, 5747d436: distinct, no shared prefix/suffix or sequence pattern.
- Business-reading note (O5): `write_off_unauthorized_implant_819e3af9` and `write_off_unauthorized_imaging_395b7f3f` write identical rows (same `make_id` arguments, same reason, same carc); so do the convenience/SAD pair and the two user close-out tools. The DB end state cannot tell which of a pair was called.
- E24: P7's domain ("a claim that has a payer payment posted and is not closed") includes never-denied claims whose `denial_carc` is `NONE`; the SAD tool copies it into `claim_transactions.carc_code`, whose frozen enum has no `NONE` (finding C12).

### prerequisite_graph
- `prerequisite` is filled on all eight policies (`[]` on P1, P2, P3, P5, P7). Edges: P4←P1 (value_input, gate `implant_booked`), P4←P2 (value_input, `small_booked`), P4←P3 (state_gate, gate `claim_transactions.writeoff_reason`), P6←P5 (value_input, `recovered`), P8←P5 (value_input, `recovered`), P8←P6 (value_input, `imaging_booked`), P8←P7 (state_gate, `claim_transactions.writeoff_reason`). Every `problem` is an extended policy of this file, none self-referential; graph acyclic (topological orders: P1,P2,P3 → P4; P5 → P6 → P8, P7 → P8).
- Every `policy_source` is verbatim in the blocked policy's own rule; all edges `form: state`, no `fallback_reason` (none required). Every `resolved_by` equals the depended-on policy's `target_tool`. Every value_input `gate` names a binding of the blocked compute and the depended-on write changes it (verified on both task worlds in the task files).
- The two `state_gate` edges name a column (`claim_transactions.writeoff_reason`) as gate; the extended policies carry no eligibility block and neither compute reads NONCOVERED_NO_WAIVER, so the gate exists only as the rule sentence (O2). No authoring-viewpoint wording in any `prerequisite` field.
- Conditions vs sentences: P4←P3's `condition` ("convenience items at or above the routine-supply floor") is narrower than its sentence ("every take-home convenience item on the account") — finding C15. The others match in scope.

### prerequisite_sentences
Four-point test, per edge:
- P4←P1 "The member-decision value is fixed only after any implant lacking its own authorization carries its unauthorized-implant write-off entry on the claim." Connective "only after"; state form; no tool/id/snake_case; scope = condition. Reader's hop: P1's rule is the only rule that writes an implant write-off ("takes the implant lines ... off the claim as one write-off entry with the write-off reason NO_AUTHORIZATION_OBTAINED"). But the record that shows the state is a `claim_denial_written_off` row with reason NO_AUTHORIZATION_OBTAINED, which P6's write produces identically; P4's compute accepts either (C3).
- P4←P2 "The member-decision value is fixed only after any laboratory item small enough to close below the appeal threshold carries its below-threshold write-off entry on the claim." Passes; single writer P2.
- P4←P3 "The member's decision is not recorded until every take-home convenience item on the account carries its non-covered write-off entry on the claim." Connective "not ... until"; state form; writer P3 — but broader than the condition (C15).
- P6←P5 and P8←P5 "... is fixed only after the payer's recovery of its payment stands as a recovery entry on the claim." Passes; only P5's tool writes `claim_takeback` in this difficulty.
- P8←P6 "The external-review close-out is fixed only after any advanced imaging lacking its own authorization carries its no-authorization write-off entry on the claim." Same two-writer record problem as P4←P1 (C3); P8's own coverage sentence is generic ("only while no no-authorization write-off entry stands on the claim"), so an implant entry alone removes the imaging from the close-out.
- P8←P7 "The patient's external-review decision is not recorded until every self-administered drug on the account carries its non-covered write-off entry on the claim." Passes within P8's domain (P8 needs a recovery, hence a payment, which is P7's gate).
- No depended-on rule restates the blocked sentence; no rule names a tool or policy id. Each rule names its seven siblings' subjects only inside the declared overwrite restatement (XF D16), not as an order. No undeclared cross-problem order found. No base sentence grounds an edge.

### override_declarations
Sentence-by-sentence against each `base_policy_refs` entry (finding half only):
- `claim_denial_write_off` sentence 1 ("A denied amount is written off ... BELOW_APPEAL_THRESHOLD ..."): retired by P1, P2, P3, P4, P6, P7, P8, each `replaced_by` restating the clause for every other denied amount and naming all seven sibling scopes (D15/D16 satisfied). Sentence 2 (no BELOW_APPEAL_THRESHOLD above the threshold while a window is open): retired by P2 for lab items under a member-level window only, restated for everything else. Sentence 3 (dedup) and 4 (patient liability) followed by all.
- `claim_timely_filing`, `claim_appeal_windows`, `claim_authorized_representative`: followed (no extended write files a claim, an appeal or an AOR). P4 departs from `claim_appeal_windows` "a member-level appeal ... is available only where that window is greater than zero" by stating, for every payer class, that "the remaining member-level appeal belongs to the patient" (C9).
- `claim_denial_routing`: CO-50 routes to MEDICAL_NECESSITY_APPEAL; P1 and P6 book NO_AUTHORIZATION_OBTAINED under whatever the current denial code is (both task claims are CO-50) (C8). "The claim closes once no route remains" is not overwritten while every root leaves the claim denied with a remainder (O3).
- `claim_recoupment_and_overpayment` (P5, P6, P8 refs; P5 `overwrite: []`): base "is recorded against the remittance that carried it" vs P5 "against the remittance that carried the claim's payment" — undeclared departure (C14). "An overpayment Riverbend identifies itself ... refunded within overpayment_refund_days" — P5 is payer-requested, no conflict.
- `claim_remittance_posting` (P5, P7): "a contractual amount is never moved to the patient" followed; the extended "contractual remainder ... month-end contractual close" is a non-remittance contractual posting the base event `claim_contractual_adjustment` (grain: per remittance per CO-45 line) does not describe (O3).

### factor_ladders
Declared factors (effect / cross_difficulty label); every ladder has >= 3 tiers, every tier is a rule sentence and a branch of its binding, every fall-through value equals the declared `baseline` binding, no two tiers of one ladder share a value or method (checked on params).
- P1 (6): implant_valuation_method m/encounter; implant_markup_band p; implant_cost_margin p; implant_units_counted m; device_handling_addon p; tissue_handling_allowance p. Multi-source: valuation method, cost margin, addon, allowance.
- P2 (5): laboratory_pricing_basis m; laboratory_schedule_level p; laboratory_units_allowed p; specimen_collection_fee p; small_item_test_basis m. No cross_difficulty label (all read the encounter account).
- P3 (4): convenience_units_counted m; routine_supply_floor p; convenience_self_pay_value p/encounter; later_unit_share p.
- P4 (6): surgical_pricing_method m/encounter; arthroscopy_case_rate p; secondary_procedure_share p; ancillary_bundling m; take_home_equipment_rate p; site_of_service_differential p/encounter.
- P5 (6): retained_test_pricing_method m/encounter; echocardiogram_contract_fee p; ecg_tracing_fee p; ecg_tracings_counted m; lab_fee_schedule_multiplier p; member_cost_share_netting p (history).
- P6 (5): ct_valuation_method m/encounter; ct_angiography_fee p; contrast_handling m; contrast_rate_per_ml p; imaging_site_differential p/encounter.
- P7 (4): self_administered_drug_valuation m/encounter; self_pay_dose_price p; pharmacy_dispensing_fee p; sad_doses_counted m.
- P8 (6): observation_pricing_method m/encounter; observation_case_rate_band p; heparin_unit_rate p; general_pharmacy_handling m; observation_supply_percentage p; infusion_contract_fee p.
Structural defects (each a SOURCE-FACTOR RED, full member lists in findings F1–F6): factors whose contribution exists only on another factor's tier (F1, 15 members), factor tiers that read other factors' outputs (F2, 5 members), tier conditions that hold of every customer reaching the write (F3), fall-through tiers no customer can reach (F4), a method pair with no distinguishing input (F5), a mislabelled parameter (F6).
Counting only factors that survive F1–F6: P1 keeps 1 (implant_valuation_method); P2 keeps 2 (laboratory_pricing_basis, specimen_collection_fee); P3 keeps 1 (convenience_units_counted); P4 keeps 3, all parameters (secondary_procedure_share, take_home_equipment_rate, site_of_service_differential); P5 keeps 2 (retained_test_pricing_method, member_cost_share_netting); P6 keeps 3 with 1 parameter (ct_valuation_method, contrast_handling, imaging_site_differential); P7 keeps 1 (self_administered_drug_valuation); P8 keeps 5 (all but observation_case_rate_band). Only P8 stays inside the 4–6 factor / 2 parameter / 1 method bounds. The per-task minima (>= 1 multi-source and >= 1 cross-difficulty factor) still hold on survivors: task 0 through P4 site_of_service_differential (claim class AND campus, encounter) and P1 implant_valuation_method; task 1 through the P5/P6/P7/P8 method factors.

### findings
Charter-global findings. "Bears on" names the task files that demonstrate the consequence.

**C1 SOURCE-POLICY RED — P4 and P8 claim the same claim and the same patient decision.** P4 rule: "On a claim in denied status whose provider-level appeal levels are all used (its highest appeal level filed is at least the payer class's available appeal levels), the remaining member-level appeal belongs to the patient; when the patient decides in person not to pursue it ... this rule takes the services still open off the claim as one write-off entry with the write-off reason APPEALS_EXHAUSTED". P8 rule: "On a claim in denied status whose internal appeal levels are all used (the appeals filed on it number at least the payer class's available appeal levels), where the payer class offers independent external review and the external-review window is still open, the remaining route is the patient's own request for external review; when the patient decides in person not to request it ... APPEALS_EXHAUSTED". On any commercial/Marketplace claim whose appeals reach the level count inside 4 months, both gates are true (`member_gate`, `review_gate`), the two rules name different "remaining" routes, and base dedup permits only one (carc, APPEALS_EXHAUSTED) entry. No sentence orders or excludes one against the other. Bears on task 1 (P4 evaluates 5584.80 on its world — a second root write) and task 0 (P8's gate is true, value 0.00, no scored consequence).

**C2 SOURCE-POLICY RED — same-reason write-off collisions.** P1 and P6 each require a (current carc, NO_AUTHORIZATION_OBTAINED) entry on a denied non-emergency claim whose account bills implants (0278) and CT (0350) once a recovery stands; P3 and P7 each require a (current carc, NONCOVERED_NO_WAIVER) entry on a denied claim with a payment whose account bills convenience-list items and 0637 drugs. Base `one_write_off_per_reason` (in force) allows the first of each pair only; which survives depends on order, and the second's amount is either lost or the dedup is broken. Neither task world carries both members of a pair (task 0 has no CT/0637; task 1 has no 0278/convenience items): no task consequence.

**C3 SOURCE-POLICY RED — the "implant entry"/"imaging entry" state is not record-distinguishable.** P4 rule "leaves out the implant charges (revenue code 0278) once an unauthorized-implant write-off entry stands" vs compute `implant_booked: COUNT('claim_transactions', event_type='claim_denial_written_off', writeoff_reason='NO_AUTHORIZATION_OBTAINED') > 0`; P8's sentence names the imaging entry while `imaging_booked`/`imaging_written_off` and P8's coverage sentence take any NO_AUTHORIZATION_OBTAINED entry. The tools `write_off_unauthorized_implant_819e3af9` and `write_off_unauthorized_imaging_395b7f3f` write identical rows. Same situation, two conclusions: a P4 claim with CT and implants where only the imaging entry stands — rule keeps the implant charges in the member-decision value, compute drops them; a P8 claim with an implant entry and no imaging entry — the imaging is neither written off by P6's rule-scope nor covered by P8. No task world carries both line families: no task consequence.

**C4 SOURCE-POLICY RED — P2 per-code test drops non-schedule laboratory codes.** Rule: "each laboratory code and the specimen collection code is tested on its own and every one whose value is at or below the payer class's small-denial write-off amount is written off"; compute `per_code_value` sums only the six schedule codes and the collection fee. Hypothetical in P2's domain: a Commercial PPO outpatient account billing 85025 and a non-schedule code (e.g. 82947 at 40.00): rule writes off the non-schedule code's 23.40 (40.00 × 58.5%), compute writes 0 for it. Task 0's account has only schedule codes: no task consequence.

**C5 SOURCE-POLICY RED (XF B9) — hidden revenue-code filters.** Rule P6 "the contrast agent billed with them (code Q9967)", "the contrast code Q9967 by its charges and billed units"; rule P8 "the heparin (code J1644)", "the contrast code Q9967"; computes filter `revenue_code='0636'` in P6 `contrast_charges`, `contrast_units`, `contrast_method`, `contrast_rate` and P8 `imaging_charges`, `heparin_charges`, `heparin_units`, `heparin_unit_fee`. A Q9967 or J1644 line under another revenue code (e.g. 0255, 0250) is counted by the rule and dropped by the compute. Task 1's lines are under 0636: no task consequence.

**C6 SOURCE-POLICY RED — P8 compute covers less than the rule.** Rule/baseline: "The close-out covers the services of the claim's hospital account that the denial reached and that no other route closes ... The close-out value is the charges it covers multiplied by the payer class's expected allowed percentage of charges"; compute values only G0378/0762, J1644/0636, 96365/0260, 0250, 0270, 0272 and 0350+Q9967. Any other revenue code on an observation account (0450, 0510, 0636 drugs other than J1644 and Q9967, 0761) is covered by the rule and absent from the compute. Task 1's account has no such line: no task consequence.

**C7 SOURCE-POLICY RED — contradictory statements on lab payability for commercial observation stays.** P2: "on an Inpatient Admission Account or an Observation Stay Account the laboratory items are part of the stay's per-diem and carry no separate value". P5: "Riverbend treats a retrospective denial of a stay as reaching every service of the account except the retained diagnostic tests, which its payer agreements keep payable as outpatient diagnostics: ... the laboratory tests (revenue code 0300)", valued "at the lesser of its schedule value and its charges" on a commercial observation account; P8: "the retained diagnostic tests (revenue codes 0483, 0730 and 0300), which stay payable". Same lines, opposite premises about Riverbend's payer agreements. Bears on task 1.

**C8 SOURCE-POLICY RED (realism, XF B12/E24/F27) — invented "own authorization" rule for implants and advanced imaging.** P1: "Riverbend's payer agreements require each implant to carry an authorization of its own, separate from the procedure's; a claim carries a single authorization reference, which is the procedure's, so every implant line on the account lacks its own authorization"; P6 the same for "advanced imaging ... separate from the stay's or the procedure's". (a) The frozen schema defines `insurance_claims.prior_auth_number` as "payer authorization reference for the services", not the procedure's or the stay's only. (b) The rule covers Original Medicare and BadgerCare claims, which have no Riverbend payer agreement and require no prior authorization for CT or for implants billed with an authorized procedure; radiology-benefit prior-authorization programs exclude imaging done during inpatient, observation and emergency encounters. (c) Both rules book NO_AUTHORIZATION_OBTAINED "carrying the claim's current denial reason code", so a CO-50 (medical necessity) denial — both task claims — produces a no-authorization write-off the payer never issued, while base routing sends CO-50 to MEDICAL_NECESSITY_APPEAL and, once upheld at the last level, to APPEALS_EXHAUSTED. Bears on task 0 (P1) and task 1 (P6).

**C9 SOURCE-POLICY RED (realism + base) — P4 asserts a member-level appeal that does not exist for every payer class.** P4: "the remaining member-level appeal belongs to the patient" for any claim whose appeal level reaches `appeal_levels_available`. Base parameter_schema: `member_appeal_window_days` "0 means the program has no member-level appeal and disputes go to the state workers' compensation process" (Workers' Comp = 0); base `claim_appeal_windows`: a member-level appeal "is available only where that window is greater than zero". For Original Medicare/Medicare Advantage the 5 levels run through judicial review and are shared by provider and beneficiary; nothing remains after them. `member_gate` tests no member window. No task world is WC/Medicare: no task consequence.

**C10 SOURCE-POLICY RED (realism, ACA/Medicare appeal rules) — every appeal row counts as an "internal appeal level".** P8 `review_gate` and P5 `final_gate` count all `claim_appeal_filed` rows (PROVIDER_RECONSIDERATION, UNDERPAYMENT_APPEAL and RECOUPMENT_DISPUTE included) as the plan's exhausted internal appeals; ACA external review (45 CFR 147.136 / 29 CFR 2590.715-2719) follows exhaustion of the claimant's internal appeals, which a provider's contractual reconsideration is not, and Medicare's five levels are not "internal". Task 0's claim (two PROVIDER_RECONSIDERATION rows only) satisfies P8's external-review gate; it feeds C1 on task 1.

**C11 SOURCE-POLICY RED (realism, OPPS packaging) — program tiers of P4 and P8.** P8: for Medicare Advantage, Original Medicare or BadgerCare observation stays the hours are "priced per hour, the billed hours but no more than obs_hour_cap times obs_hourly_prog", infusion at `infusion_fee_prog`, general pharmacy at `rx_line_allowance` per line, while heparin is "packaged into the stay"; Medicare pays observation through the comprehensive observation APC, which packages hours, infusions and pharmacy alike. P4: on program outpatient-surgery claims "only their anesthesia and recovery lines paid separately", while the same rule's `mpr_prog: 0.0` treats secondary procedures as packaged; OPPS packages 0370/0710 lines. Both tasks are commercial: no task consequence.

**C12 SOURCE-POLICY RED (realism + E24) — P7 domain.** "Riverbend's agreements treat self-administered drugs on a hospital claim as covered by no payer class" is applied through the "otherwise" tier to Inpatient Admission Accounts, where drugs are covered inpatient services. P7's domain ("a claim that has a payer payment posted and is not closed") includes never-denied adjudicated claims; there the rule's "carrying the claim's current denial reason code" and the tool's `carc_code=claim.get("denial_carc")` write `NONE`, a value absent from the frozen `claim_transactions.carc_code` enum. Task 1's claim is CO-50 and observation: no task consequence.

**C13 SOURCE-POLICY RED (XF B12) — framing clauses resting on no record.** P3 and P7: "with no advance financial-responsibility waiver among the claim's records" — no table or field of the schema records a waiver, so the clause can never be tested. P5: "Riverbend refunds to the payer, at the payer's request" — no record holds a payer refund request. Bears on task 0 (P3) and task 1 (P5, P7) as unverifiable conditions; no scored-value change.

**C14 SOURCE-POLICY RED (XF D17) — undeclared departure in P5.** Base `claim_recoupment_and_overpayment`: "A payer takeback ... is recorded against the remittance that carried it." P5 (`overwrite: []`): "records the refund as one payer recovery entry on the claim with the reason code WO-72, against the remittance that carried the claim's payment"; the tool copies the payment's trace and `remit_date`. The base `recoupment_dispute_window` (in force) anchors on that `remit_date`. Bears on task 1 (recovery row dated 2026-05-06 by remittance, so the base 60-day dispute window reads as already closed when it posts); no scored-value change.

**C15 SOURCE-POLICY RED (check 6, scope) — P4←P3 sentence broader than its condition.** Sentence: "The member's decision is not recorded until every take-home convenience item on the account carries its non-covered write-off entry on the claim." Condition: "whenever the account carries take-home convenience items at or above the routine-supply floor." P3 defines the convenience items as "the items on Riverbend's convenience list (codes E0218, A9273 and E0236) billed under revenue code 0274" and leaves a below-floor code's charges "on the claim for the month-end contractual close". Bears on task 0 (A9273 at 9.00 per unit).

**F1 SOURCE-FACTOR RED (XF A4) — factors gated through another factor's tier.** Each member enters the computed amount only when another factor's method tier is taken; under the policy baseline its binding is read by nothing, so its declared `baseline` is not a value `baseline.rule` states for any input (the baseline rule names no markup, margin, fee, level, multiplier or band). Members: P1 implant_markup_band and implant_cost_margin (only inside `cost_plus_value`, selected by implant_valuation_method's cost-plus tier), P1 implant_units_counted (its fee-schedule use exists only on the fee-schedule tier; its other use is F2); P2 laboratory_schedule_level (only in `val_*` under lab_method 2); P4 arthroscopy_case_rate (only under surgical_method 2); P5 echocardiogram_contract_fee, ecg_tracing_fee, ecg_tracings_counted, lab_fee_schedule_multiplier (only under retained_method 1/2); P6 ct_angiography_fee (only under ct_method 1/2), contrast_rate_per_ml (only under contrast_method 2); P7 self_pay_dose_price, pharmacy_dispensing_fee, sad_doses_counted (only under sad_method 1/2); P8 observation_case_rate_band (only under obs_method 2). Related: P3 routine_supply_floor zeroes whole per-code items built from the other three P3 factors (the others are gated through it). On a world where the gating factor sits on its fall-through each member is inert; on both task worlds the gating tiers are taken, so the members bear weight there (task files).

**F2 SOURCE-FACTOR RED (XF A1) — tiers that read other factors' outputs.** P1 device_handling_addon "for each counted device unit" and tissue_handling_allowance "for each counted tissue unit" multiply implant_units_counted's bindings; P3 later_unit_share applies to "each further counted unit at that self-pay value" (convenience_units_counted × convenience_self_pay_value); P2 small_item_test_basis tests "each laboratory code" at the value produced by laboratory_pricing_basis, laboratory_schedule_level, laboratory_units_allowed and specimen_collection_fee; P4 surgical_pricing_method's case-rate tier embeds `case_rate` and both its case-rate and fall-through ("percentage") tiers embed `secondary_share` — so its fall-through equals `baseline.rule` ("the charges it covers multiplied by the payer class's expected allowed percentage") only when another factor also sits at baseline. Demonstrated on task 0's world (task file): substituting implant_units_counted alone moves P1 only through the addon/allowance (1760.72 → 1695.72).

**F3 SOURCE-FACTOR RED — conditions that hold of every customer reaching the write.** P3 routine_supply_floor tiers 1–2 and later_unit_share tier 2: "billed on a Riverbend hospital account" (compute `CFIELD('encounter','variant_name', ...) != ''`) — every claim is billed on a Riverbend hospital account, so the tiers reduce to the payer class and the fall-through is reached only by Workers' Comp claims. P3 convenience_self_pay_value tier 2: "the account class does not give that discount AND the code is billed" — every code that contributes is billed (count 0 ⇒ item 0), so the clause restates scope.

**F4 SOURCE-FACTOR RED — fall-through tiers (= declared baselines) no customer can receive.** P6 ct_angiography_fee: `cta_fee` is used only under ct_method 1/2, both commercial-only, and every commercial claim billing 71275 is on tier 1 or 2, so `cta_fee_std` (690.00, the baseline) never prices anyone. P6 contrast_rate_per_ml: used only under contrast_method 2 (commercial with contrast units), where tiers 1–2 cover every commercial class, so `contrast_ml_std` (0.35) never applies. P3 convenience_self_pay_value: tier 3 ("the code's per-unit charge", the baseline) is reachable only by an unbilled code, whose item is 0. Each ladder has two live tiers.

**F5 SOURCE-FACTOR RED (XF C14) — method pair with no distinguishing input.** P4 ancillary_bundling tier 2 "the anesthesia and recovery charges (revenue codes 0370 and 0710) times the expected allowed percentage" vs tier 3 "the ancillary charges times the expected allowed percentage" (0370+0710+0250+0272): the same aggregate (charge amount under a revenue-code filter) times the same constant; per the recipe's structural test the pair fails, so the factor is a filter choice, not a method.

**F6 SOURCE-FACTOR RED — mislabelled effect.** P2 laboratory_units_allowed is labelled `parameter` but its tiers change the computation (tiers 1–2 `MN(units, mue × MX(lines,1))`, tier 3 the bare billed units: the line-count input and the cap operation appear and disappear); the identical shape is labelled `method` in P1 implant_units_counted, P5 ecg_tracings_counted and P7 sad_doses_counted.

### observations (not grounds for rework)
- O1 P2 binding `pct` has no `compute_basis` entry (unit conversion of the expected allowed percentage).
- O2 The two `state_gate` edges name a column as `gate`; no eligibility block or compute binding implements them. Their weight is the act-now/wait decision their rule sentence gives, not a value.
- O3 Every write-off policy leaves a "contractual remainder, which Riverbend's month-end contractual close posts on the last calendar day of the month" — a back-office posting with no remittance, unlike base `claim_contractual_adjustment` (one row per remittance per CO-45 line); every root leaves the claim `denied` with a non-zero `payer_balance` although base `claim_denial_routing` "The claim closes once no route remains" is in force. No tool closes a claim, so no second terminal state is reachable.
- O4 `refund_payer_recovery_9b1903be` takes `pays[0]` (file order) when several payment remittances exist; P5 states no rule for that case.
- O5 Paired tools write byte-identical rows (implant/imaging, convenience/SAD, the two user close-outs): DB end states cannot distinguish the tool within a pair.
- O6 `cross_difficulty: null` on many factors that read the encounter account (labels only).

## closing_status (written after both task files were frozen and compared; not a closing checklist — REDs are open)
- Per-task files `0.md`, `1.md` correspond to tasks 0 and 1; this is revision_1 (no older revision).
- Revealed `charter_scope`: task 0 = {P1, P2, P3, P4} with their four tools; task 1 = {P5, P6, P7, P8} with their four tools — pairwise disjoint, jointly cover all eight extended policies and tools; each matches the tree derived blind.
- Trees: task 0 P4 ← {P1, P2, P3} (2 value_input + 1 state_gate); task 1 P8 ← {P5, P6 ← P5, P7} (3 value_input + 1 state_gate); owner=user roots; whole-difficulty graph acyclic. Every prerequisite unmet at frozen_time and every value_input edge bears weight on its world (task files).
- GT (writes, owners, order, amounts, prerequisite_closure figures, factor_sensitivity and baseline_result figures) equals the blind derivations in both tasks, except one false `tier_taken` statement in task 1 (task 1 finding 3).
- The difficulty does not pass the source-layer audit: open charter REDs C1–C15 and F1–F6; task 1 has a second defensible root write (C1); task 0 has a second reading that blocks its root (C15). Gate re-run on a final form is the coordinator's step after rework.

VERDICT revision_1: task0=RED task1=RED charter=C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12,C13,C14,C15,F1,F2,F3,F4,F5,F6

## revision_2

### charter_global_frozen (revision_2)
- Re-audit 2026-10-20 (after the coordinator's round-2 brief). **Not blind**: the coordinator authorised reading `worklog.md`, whose REWORK section states the round-2 handling-time figures, and both GT files were read after the derivations below were computed. The derivations were nonetheless computed from the charter, the views and the DSL before the GT files were opened (scratch /tmp/audit_claims_0073/derive2.py); I treat the round as non-blind evidence.
- Hashes (first 12): `claim.extended.yaml` 32d1a66ae041, `task_tools.py` 5fa4abea6583, `tasks/0.json` 5df4bf2986a3, `tasks/1.json` d3416741832a, views r2 `0.view.json` 455192878627b4ff, `1.view.json` 08fc4bb88ff01fb1 — all match the brief. Both charter hashes changed, so every charter-global section is re-derived in full (nothing carried forward from revision_1).
- Mechanical sweeps (scratch cb.py): base section parsed-equal to `blueprint/products/claim.yaml`; every `superseded_clause` verbatim in its base rule; every `replaced_by`, `compute_basis` quote, `baseline.rule` sentence and prerequisite `policy_source` verbatim in its own rule; every binding has a `compute_basis` entry (O1 closed).
- Read isolation unchanged; no other scenario or difficulty directory read. contamination_disclosure: the round is non-blind as stated; nothing else.

Policies (round 2): P1 `claim_ext_surgery_post_payment_refund` (refund_surgery_claim_payment_239964f7), P2 `claim_ext_surgery_small_item_closeout` (write_off_surgery_small_items_d7ad9b50), P3 `claim_ext_noncovered_convenience_closeout` (write_off_noncovered_convenience_item_58e216c4), P4 `claim_ext_member_decision_closeout` (user, close_denial_on_member_decision_7cc13d5d), P5 `claim_ext_retrospective_denial_refund` (refund_payer_recovery_9b1903be), P6 `claim_ext_observation_small_item_closeout` (write_off_observation_small_items_ab2aa651), P7 `claim_ext_self_administered_drug_closeout` (write_off_self_administered_drugs_664aab61), P8 `claim_ext_external_review_decision_closeout` (user, close_denial_on_external_review_decision_5747d436).

### policy_conflict_scan (revision_2)
- Domains: P1–P4 act only on Commercial PPO/HMO/Marketplace claims of an Outpatient Surgery Account; P5–P8 only on such claims of an Observation Stay or Emergency Department Visit Account (every gate tests `CFIELD('encounter','variant_name')` and the claim class). Roots: P4 additionally needs zero MEMBER_APPEAL_WITH_AOR rows, appeals < levels and an open member window (DAYS ≤ member window + presumption, window > 0); P8 needs ≥ 1 MEMBER_APPEAL_WITH_AOR row, appeals ≥ levels, external review available and MONTHS < 4. Evaluated: every task-0 policy is 0.00 on task 1's worlds and vice versa (derive2 opening values).
- Same-reason writers per claim: BELOW_APPEAL_THRESHOLD P2 (surgery) / P6 (obs/ED); NONCOVERED_NO_WAIVER P3 / P7; APPEALS_EXHAUSTED P4 / P8 — each pair split by account class, so base `one_write_off_per_reason` admits every write. NO_AUTHORIZATION_OBTAINED is no longer written. Recovery (`claim_takeback`) writers P1 / P5, split the same way.
- Packaging statements across policies for the same lines: P6 "Ketorolac is packaged into the stay and keeps no value of its own when a Commercial HMO claim is for an Observation Stay Account" vs P8, which values a listed code that does not pass the small-item test among "the remaining charges and any open small items at the expected allowed percentage"; P2 "Cefazolin is packaged into the surgical case and keeps no value of its own when a Commercial PPO claim is for an account that bills an arthroscopy code" vs P4, which likewise values a non-passing J0690 at the expected allowed percentage (finding C16).
- Scope: revealed `charter_scope` task 0 = {P1, P2, P3, P4} + their four tools; task 1 = {P5, P6, P7, P8} + their four tools — disjoint and jointly complete.
- Event scope of the refunds: P1 and P5 write `claim_takeback` (claim category, `claim_transactions`, base `triggers: []`). The blueprint's difficulty claim lists event_types [claim_correction_filed, claim_resubmitted, claim_member_info_updated, claim_appeal_filed, claim_appealed, claim_denial_written_off, claim_closed]; `claim_takeback` is not in that list. Judgement: the write territory is the primary category (blueprint skill: "categories (the primary category set = the write territory, globally exclusive)", "Pairwise disjointness holds on the primary category axis alone"), the row lands in the claim category's own event table, no other difficulty can write it, and the difficulty summary names `claim_recoupment_and_overpayment` among its governing rules; none of the four audit relationships fails because of it. It is a declaration mismatch with the blueprint's event_types list (observation O8). Revision_1's P5 already wrote `claim_takeback` and I did not record it then — disclosed here, not a regression.

### rule_compute_equivalence (revision_2)
All eight computes swept against their rules: every HCPCS read states its revenue code and the compute filters exactly that (C5 class closed); every root and refund carries an explicit "every other charge"/"remaining charges" family (C6 class closed; P8 supplies exclude only the listed A4216, which the rule states); small-item tests are per listed code on charges and the computes cover exactly the listed codes (C4 class closed); `small_booked`/`recovered` read only rows the same domain's single writer produces (C3 closed). Rounding: one `RND(...,2)` on `result` everywhere, as stated. Zero-unit, no-recovery, empty denial date, negative refund edges stated and implemented. Month/day conventions: P8 whole-month day-number rule = `MONTHS`; P4 member window = `DAYS(denial_date, NOW) <= window + presumption`, equivalent to base's presumed-receipt counting. Tie (XF B7): the rules say "the claim's earliest-posted payer payment"; the tools sort by (posting_date, claim_txn_id), a tie rule no rule sentence states (finding C18).

### action_binding_and_uuids (revision_2)
- Eight `(target_tool, amount_usd)` pairs, one policy each. New uuid8s 239964f7, d7ad9b50, ab2aa651 are independent of each other and of the five kept ones. Each write tool calls `ctx.create` + `ctx.update`, checks no condition; only `erlbench` imported; helpers are class static methods; no factor id is a substring of a tool name; single-value args.
- Docstrings: both refund tools say Riverbend "refunds to the payer after the payer denied the paid services" — an ordering word in a docstring (finding C17). No example values.
- Factor ids `antiemetic_unit_rate` and `iv_solution_unit_rate` are declared in both P2 and P6 (observation O9).

### prerequisite_graph (revision_2)
Edges: P2←P1, P4←P1, P4←P2 (value_input: `recovered`, `recovered`, `small_booked`), P4←P3 (state_gate, gate `claim_transactions.writeoff_reason`); P6←P5, P8←P5, P8←P6 (value_input), P8←P7 (state_gate). All `form: state`, no fallback; every `resolved_by` is the depended-on `target_tool`; every value_input gate is a binding of the blocked compute; acyclic; no authoring-viewpoint text. The state-gate edges still name a column (O2 kept).

### prerequisite_sentences (revision_2)
- P2/P4/P6/P8 recovery sentences ("... is fixed only after the payer's recovery of its payment stands as a recovery entry on the claim"): only P1 (surgery claims) / P5 (observation/ED claims) write a recovery entry in each domain — one writer per hop.
- P4←P2 / P8←P6 ("... is fixed only after the small items that pass the small-item test carry their below-threshold write-off entry on the claim"): one writer per domain.
- P4←P3 "The member's decision is not recorded until, on an account that carries take-home convenience items and no non-covered patient liability, those items carry their non-covered write-off entry on the claim." P8←P7 the same for self-administered drugs. Scope equals the `condition` and the depended-on rule's own gate (no price floor remains): C15 class closed.
- Both directions occur ("is fixed only after", "is not recorded until"); no tool, id or snake_case token; no depended-on rule restates a sentence; no undeclared cross-problem order.

### override_declarations (revision_2)
- `claim_denial_write_off` sentence 1: retired by P2, P3, P4, P6, P7, P8, each `replaced_by` scoped "only for" its own items and naming the five sibling write-off scopes. Sentence 2 ("A denied amount above small_denial_write_off_usd is never written off as BELOW_APPEAL_THRESHOLD while an appeal window remains open") is no longer retired by anyone: P2's listed codes each pass at ≤ the threshold and the entry's amount is below it, so the per-code reading stands; the aggregate of passing charges can exceed the threshold while the member window is open (task 0: 180.00 > 50.00) — observation O10.
- `claim_recoupment_and_overpayment` "A payer takeback re-opens ... recorded against the remittance that carried it.": retired by P1 and P5 for their own refunds, each naming the other, restating the clause for every other takeback (C14 closed).
- `claim_appeal_windows` / `claim_authorized_representative`: P4's "Riverbend files the last internal level of a commercial claim only as the member's own appeal under the patient's signed authorized-representative form" narrows what base leaves open; no tool of this difficulty files appeals, so no scored consequence (O11).
- `claim_denial_routing`: CO-50 claims now end in BELOW_APPEAL_THRESHOLD, NONCOVERED_NO_WAIVER or APPEALS_EXHAUSTED only (C8 closed). "The claim closes once no route remains" still meets roots that leave the claim denied (O3 kept).

### factor_ladders (revision_2)
42 factors (P1 6, P2 5, P3 4, P4 6, P5 6, P6 5, P7 4, P8 6); every policy has ≥ 2 parameter and ≥ 1 method factors, every factor reads the encounter account except `member_cost_share_netting` (claim PR lines). Structure re-checked against XF A/C:
- Independence (A1/A4): each factor owns one line family (method factors own their tariffs, e.g. P8 `case_rate`, P1/P5 `sched_*`) or one whole-value multiplier; every binding is read by the baseline path; no tier reads another factor's output — F1/F2 closed.
- Fall-throughs: every "otherwise" is reachable inside the commercial domain (Marketplace claims, other campuses, the other account class, single-day stays) and equals the declared baseline, which `baseline.rule` states — F4 closed. No condition restates scope — F3 closed.
- Method pairs (C14): every method ladder has a distinguishing input or operation per pair (packaged 0 / units × tariff / percentage; lesser-of adds MN; lines vs capped units vs units; band tariff vs capped hours × rate vs percentage) — F5 closed. Labels follow shape — F6 closed.
- New defects (findings F7, F8): payer-class tiers on the value of items the same rules declare covered by no payer (7 factors); a CT fee that turns on whether the stay crossed a calendar day.

### round-1 items — closure check (revision_2)
| item | status | evidence |
| --- | --- | --- |
| C1 | closed | P4/P8 split by account class and by MEMBER_APPEAL_WITH_AOR count; each root 0.00 on the other task's world |
| C2, C3 | closed | one writer per (reason, domain); NO_AUTHORIZATION_OBTAINED gone; tools write identical rows only across domains (O5 kept) |
| C4, C5, C6 | closed | exact code lists with revenue codes; remainder families in every root/refund |
| C7 | instance closed, class recurs | no rule calls labs packaged; same-class contradiction now on ketorolac and cefazolin (C16) |
| C8 | closed | no-authorization policies and tools removed; no authorization framing remains |
| C9, C10, C11, C12 | closed | commercial-only domains; member window > 0 tested; external review needs a filed member appeal; no program tiers; SAD rule limited to denied observation/ED claims |
| C13 | closed | waiver = NONCOVERED_SERVICE liability record test; "at the payer's request" removed |
| C14 | closed | scoped overwrite in P1 and P5 naming each other |
| C15 | closed | state-gate sentences carry the depended-on rule's exact scope |
| F1–F6 | closed | see factor_ladders (revision_2) |
| O1, O4, O6 | closed (O4 subject to C18 tie) | compute_basis complete; earliest-posted payment; cross_difficulty labels set |
| O2, O3, O5 | kept as observations | unchanged by design |

### findings (revision_2)
**C16 SOURCE-POLICY RED (recurrence of the C7 class) — the same drug is "packaged, no value of its own" in one rule and valued in another.** P6: "Ketorolac is packaged into the stay and keeps no value of its own when a Commercial HMO claim is for an Observation Stay Account"; P8 covers "a listed code that does not pass" among "the remaining charges and any open small items at the expected allowed percentage". P2: "Cefazolin is packaged into the surgical case and keeps no value of its own when a Commercial PPO claim is for an account that bills an arthroscopy code (29881 or 29882 under revenue code 0360)"; P4 values a non-passing J0690 the same way. Same situation (a J1885 line above the small-denial amount on an HMO observation account; a J0690 line above it on a PPO arthroscopy account): one rule says no value, the other values it at 52% / 58.5% of its charges. Both task worlds carry these codes below the threshold (they pass and are written off by P2/P6): no task consequence.

**C17 SOURCE-POLICY RED (check 3 / XF E21) — ordering word in tool docstrings.** `refund_surgery_claim_payment_239964f7` and `refund_payer_recovery_9b1903be`: "the payer's recovery of an earlier payment that Riverbend refunds to the payer after the payer denied the paid services". The skill bars ordering words such as "after" in docstrings. Bears on task 0 (step 8) and task 1 (step 8) as docstring text only.

**C18 SOURCE-POLICY RED (XF B7) — tie rule for "earliest-posted payer payment".** P1/P5 overwrite: "recorded against the remittance that carried the refunded payment (the claim's earliest-posted payer payment)"; `_Claims.first_payment` sorts by (posting_date, claim_txn_id). Two payments posted the same day are ordered by row id, which no rule states. Each task claim has one payment: no task consequence.

**F7 SOURCE-FACTOR RED (realism, unreal ladder) — payer-class tiers on items the rules say no payer covers.** P3: "Riverbend's agreements treat them as covered by no payer class"; P7: "Riverbend's commercial agreements exclude self-administered drugs". Yet the value written off for them is tiered by the patient's payer class: P3 `cold_therapy_unit_valuation` (PPO: units × self-pay price; HMO: lesser of charges and that value), `support_garment_self_pay_price` ("Riverbend's published self-pay price" 16.00 on a PPO claim, 18.00 on an HMO claim — a self-pay price that varies with the patient's insurer is not a self-pay price), `insured_noncovered_discount` (0.80 PPO at Grand Chute, 0.85 HMO at a hospital campus; Riverbend's own encounter charter gives an insured patient's non-covered items no discount on an Outpatient Surgery Account, `uninsured_discount_on_noncovered_insured: false`); P7 `oral_drug_valuation` (HMO observation: 9.50 per dispensing line from "Riverbend's self-pay dose price list"; PPO ED: lesser of charges and units × 7.00), `oral_dexamethasone_price` (4.00 HMO / 5.00 PPO), `inhalation_unit_dose_price` (3.10 HMO / 3.60 PPO), `sad_campus_factor` (0.90 HMO / 0.95 PPO at a hospital campus). The payer class is not a condition a hospital weighs when valuing an item no payer covers and the patient is not billed for; the tiers' values are not treatments Riverbend would publish. Bears on task 0 (P3 = 313.60 rests on three of these tiers) and task 1 (P7 = 26.28 rests on all four). Note: payer-class tiers on the same items existed in revision_1 (P3 units counted, later-unit share; P7 dose price, dispensing fee) and I did not raise this class then — a miss of revision_1, not a regression.

**F8 SOURCE-FACTOR RED (realism, condition not weighed) — P5 `ct_angiography_pricing`.** "The CT angiography is valued at its billed units times cta_fee_hmo when a Commercial HMO claim is for a stay spanning more than one calendar day ..., at the lesser of its billed units times cta_fee_ppo and its charges when a Commercial PPO claim is for such a stay, and at the payer class's expected allowed percentage of its charges otherwise." The rule treats the CT as a retained outpatient diagnostic; whether the observation stay crossed a calendar day is not a condition a payer weighs in pricing a CT angiogram. Bears on task 1: the same CT on a same-day stay would be valued 1809.60 (3480.00 × 52%) instead of 742.00, moving the refund by 1067.60.

### observations (revision_2)
- O2, O3, O5 kept (see revision_1).
- O7 Both worlds model a post-payment denial; the base lifecycle has no adjudicated→denied transition, so the seeded `denied` status is reached only through appealed→denied.
- O8 `claim_takeback` is written outside the blueprint claim's event_types list (judged above; within the write territory).
- O9 Duplicate factor ids across P2 and P6 (`antiemetic_unit_rate`, `iv_solution_unit_rate`) — a collision risk for per-factor KB documents.
- O10 Base "never written off as BELOW_APPEAL_THRESHOLD while an appeal window remains open" vs P2 on task 0: per code each passing charge ≤ 50.00 and the entry is 31.90; the passing charges total 180.00.
- O11 P4's "last internal level only as the member's own appeal" statement narrows base appeal practice; no appeal tool in scope.
- O12 Remittances still leave the non-covered lines unadjudicated (task 0: 623.00 of convenience items; task 1: 88.00 of self-administered drugs); a balanced 835 would carry them on a PR-204/CO line, and the task-0 surgery account is `closed` although the payer did not pay in full.

## closing_status (revision_2)
Both trees hold (3 prerequisite problems, 3 value_input + 1 state_gate edges each, owner=user root, acyclic); both derivations equal GT figure by figure (task files). The difficulty does not pass: open charter REDs C16, C17, C18, F7, F8 (F7 and F8 bear on the scored values of task 0 and task 1).

VERDICT revision_2: task0=RED task1=RED charter=C16,C17,C18,F7,F8

## revision_3

### charter_global (revision_3) — not blind
- Inputs (first 12): `claim.extended.yaml` ae8f10cede68, `task_tools.py` e48614b9837b, `tasks/0.json` 8b460aea44ac, `tasks/1.json` 2f8e65441340; views r3 `0.view.json` 455192878627b4ff, `1.view.json` 08fc4bb88ff01fb1 (initial_state identical to r2). All match the brief. Worklog REWORK round 3 read first (non-blind); figures recomputed from the charter on the r3 views (/tmp/audit_claims_0073/derive3.py) before the GT files were opened. Both charter hashes changed: touched policies re-derived; untouched policies re-swept mechanically.
- Mechanical sweeps: base section unchanged; every `compute_basis`, `replaced_by`, `baseline.rule` sentence and `policy_source` verbatim in its rule; every binding quoted; 42 factor ids unique, none a substring of a tool name; tools import only `erlbench`, each write tool creates and updates in its own body.

### round-2 items — closure check (revision_3)
| item | status | evidence |
| --- | --- | --- |
| C16 | closed | P2 `cefazolin_pricing` and P6 `ketorolac_pricing` now value the drug (lesser-of / units × fee / percentage); the remaining packaging statements (P1 typing on 0300, P4 ancillaries 0250/0272, P5 contrast Q9967, P8 general pharmacy 0250) cover lines no other rule of the same domain values (P4 excludes 0300; P8 excludes Q9967; P5 retains neither 0250 nor 0272) |
| C17 | closed | no ordering word left in any docstring (sweep for before/after/first/then/prior/until/once/later/following/earlier) |
| C18 | closed | P1/P5 overwrites: "when several payer payments share that earliest posting date, the one whose remittance trace number comes first in alphabetical order"; `_Claims.oldest_payment` sorts by (posting_date, remit_trace_number); docstrings say the same |
| F7 | closed as stated (payer class) | no payer-class condition remains in P3 or P7; but the replacement price bands are themselves unreal — F9 |
| F8 | closed | P5 `ct_angiography_pricing` keys on contrast (Q9967) billed with the scan; P8 `general_pharmacy_handling` on 8 or more G0378 hours; P4 `ancillary_packaging` on campus; no rule compares service end and start dates |
| O9 | closed | surgery_* / observation_* factor ids |

### cross-task exclusivity and regression (revision_3)
- Domains unchanged (P1–P4 Outpatient Surgery Account; P5–P8 Observation/ED); each task's policies evaluate 0.00 on the other task's world; one writer per (reason, domain); gates of the roots unchanged.
- Untouched policies (P1 refund except the tie sentence; P4 except ancillary; P5 except CT; P8 except pharmacy) re-swept: figures unchanged (11058.88, 9117.24, 4044.57, 2321.99) and every factor still moves its figure. Trees, edges, skip figures and order unchanged.
- XF re-check on touched policies (P2, P3, P4, P5, P6, P7, P8): A1–A5 hold (each factor owns its family or the whole-value multiplier; P3/P7 apply the encounter account-class rule as a stated plain binding); B6–B13 hold except as F9 notes; C14 pairs for the re-cut method factors each have a distinguishing input; D15–D17 unchanged; E18–E24 hold.

### findings (revision_3)
**F9 SOURCE-FACTOR RED (realism, unreal ladder) — the re-cut price bands of P3 and P7.** Each band factor sets an item's "price" from the item's own charge per billed unit, with a fixed price in the upper tiers and the charge itself in the fall-through:
- P3 `cold_pack_price_band`: charge ≥ 15.00 → 10.00; 5.00–14.99 → 6.00; below 5.00 → the charge. A cold pack charged 5.00 (or anything from 5.00 to 5.99) is valued 6.00, above its own charge, so the write-off exceeds the item's charge and the "convenience-item charges above the convenience value" remainder is negative. Charged 4.99 it is valued 4.99, charged 5.00 it is valued 6.00.
- P3 `support_garment_price_band`: ≥ 40.00 → 28.00; 20.00–39.99 → 16.00; below 20.00 → the charge. A garment charged 19.99 is valued 19.99, one charged 20.00 is valued 16.00.
- P7 `oral_dexamethasone_price_band`: ≥ 20.00 → 7.00; 10.00–19.99 → 4.00; below 10.00 → the charge (9.99 → 9.99; 10.00 → 4.00).
- P7 `inhalation_unit_dose_price_band`: ≥ 12.00 → 5.00; 6.00–11.99 → 3.10; below 6.00 → the charge (5.99 → 5.99; 6.00 → 3.10).
Probes on the task worlds (charter compute, one charge changed): P3 = 313.60 at A9273 5.00/unit with 6.00 counted for a 5.00 item; A4467 19.99 → 316.79 vs 20.00 → 313.60; P7 J8540 9.99 → 31.67 vs 10.00 → 26.28; J7613 5.99 → 31.48 vs 6.00 → 3.10-tier 26.28. A take-home or self-pay price list that values a cheaper-charged unit above a dearer one, or above its own charge, is not one Riverbend would publish. Bears on task 0 (step 12: A9273 at 9.00 and A4467 at 24.00 sit on the middle tiers) and task 1 (step 12: J8540 at 12.00 and J7613 at 8.00 sit on the middle tiers).

### observations (revision_3)
- O2, O3, O5, O7, O8, O10, O11, O12 kept.
- O13 P3's account-class clause ("by one less the account class's uninsured discount percentage where the account class gives such items the uninsured discount") can never take its discount branch inside P3's domain (Outpatient Surgery Account: `uninsured_discount_on_noncovered_insured: false`); in P7 it is live only on Emergency Department accounts.

## closing_status (revision_3)
Both trees hold; both derivations equal GT figure by figure (task 0: 11058.88 / 38.30 / 313.60 / 9117.24; task 1: 4044.57 / 12.33 / 26.28 / 2321.99). Open: F9, which carries the scored step 12 of both tasks.

VERDICT revision_3: task0=RED task1=RED charter=F9

## revision_4

### entry evidence (revision_4) — not blind
- Gate chain: `tail -n 1 worklog.md` = `REWORK round 4: gates 7/7 green`. `/tmp/erl0073_coord/snapshot.sh insurance_claims_and_denials 4` (executed, not read): views r4 `0.view.json` 455192878627b4ff, `1.view.json` 08fc4bb88ff01fb1 (masked keys as before; initial_state unchanged since r2); gate snapshot 2026-10-21T02:01:29 — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; sha256 a659e4a5147a claim.extended.yaml, e48614b9837b task_tools.py (unchanged), d504925fde56 tasks/0.json, a433b62d3600 tasks/1.json (I re-hashed both task files: match).
- Worklog round-4 section read first; figures recomputed from the charter on the r4 views (/tmp/audit_claims_0073/derive4.py) before the GT files were opened. Mechanical sweeps (verbatim quotes, compute_basis coverage, baseline sentences, unique factor ids) clean.

### round-3 items — closure check (revision_4)
| item | status | evidence |
| --- | --- | --- |
| F9 | closed | every charge band removed; my sweep of each item's unit charge across 0.50 … 400.00, every former band edge included (4.99/5.00/5.99/6.00/9.99/10.00/11.99/12.00/14.99/15.00/19.99/20.00/39.99/40.00), gives a non-decreasing value for E0218, A9273, A4467 (P3) and J8499, J8540, J7613 (P7), never above the item charges (P3 per item by construction; P7 capped at the drugs' charges) |
| O13 | closed | P3 now states the Outpatient Surgery Account class gives no uninsured discount; P7's clause stays live on ED accounts |
| other band ladders | checked | P5 contrast now keys on contrast billed with CT (no volume threshold); P8 observation case rate monotone in hours and capped at the observation charges; P2/P6 small-item test (≤ small-denial amount) and P8's 8-hour packaging test are route tests, not prices |

### regression and exclusivity (revision_4)
Untouched figures unchanged (11058.88 / 38.30 / 9117.24; 4044.57 / 12.33 / 2321.99); trees, edges, skip figures (0.00, 9214.11, unchanged; 0.00, 2357.06, unchanged) and order unchanged; each task's policies are 0.00 on the other task's world. XF on P3 and P7: A1/A2/A4/A5 hold; A3 fails in P7 (C19); B6–B13 hold; C14 pairs distinguished (units vs lines inputs; lesser-of caps); D unchanged; E unchanged.

### findings (revision_4)
**C19 SOURCE-POLICY RED (XF A3, non-commuting order) — P7 places neither the dispensing fee nor the charge cap.** The assembly sentence is "Each adjustment below either replaces the standard value of one drug code or multiplies the total; replacements are made first, the multiplier after them, and the total is then rounded once", but the new dispensing fee ("A dispensing fee is added for each self-administered drug line ...") is neither a replacement nor a multiplier, and "The self-administered drug value never exceeds the drugs' charges" is not placed relative to the multipliers. Compute: `MN(sad_charges, (val_J8499 + val_J8540 + val_J7613) * sad_factor * account_noncovered_factor)` — fee before the multiplier, cap last. Second readings: on task 1, fee added after the 0.90 setting factor gives (19.00 + 9.80) × 0.90 + 4 × 0.50 = 27.92 instead of 27.72; for a single one-unit J8499 line of 5.00 on a Neenah observation account, cap-then-multiply gives 4.50, multiply-then-cap 4.95 (compute). Bears on task 1 step 12.

**F10 SOURCE-FACTOR RED (realism) — re-cut factors whose conditions the business does not weigh for that quantity.**
- P7 `sad_dispensing_fee`: a per-line fee of 0.50 when the account's services are classified medically necessary, 0.75 when emergency, 0.00 otherwise. A pharmacy dispensing fee does not vary with the clinical classification of the stay, and adding a fee to the value of drugs the patient is never billed for and no payer covers has no business meaning (task 1: 4 lines × 0.50 enter the scored 27.72).
- P3 `cold_pack_take_home_share`: charges × 0.65 "when the account also bills the cold-therapy unit", × 0.80 with the garment only — the same co-billing fact `take_home_kit_share` already prices (× 0.80 when all three are billed, × 0.90 for two), so the pack's kit membership is discounted twice (task 0: 9.00 × 0.65 × 0.80). The skill: a ladder "that repeats another factor's condition because this customer already satisfies it" is not a factor.
- P3 `support_garment_take_home_share`: charges × 0.60 "when the account bills an arthroscopy code", × 0.75 with other operating-room lines, × 1 otherwise. The take-home value of a support garment does not depend on which procedure the patient had (task 0: 24.00 × 0.60).
Bears on task 0 step 12 (312.20) and task 1 step 12 (27.72).

### observations (revision_4)
- O2, O3, O5, O7, O8, O10, O11, O12 kept. O14 P7 bindings `j8540_price` (now a campus share over J8540 and J7613) and `j7613_price`/`val_J7613` (now the per-line dispensing fee) carry names of retired meanings.

## closing_status (revision_4)
Both trees hold; both derivations equal GT figure by figure (task 0: 11058.88 / 38.30 / 312.20 / 9117.24; task 1: 4044.57 / 12.33 / 27.72 / 2321.99). Open: C19, F10.

VERDICT revision_4: task0=RED task1=RED charter=C19,F10

## revision_5

### entry evidence (revision_5) — not blind
- Gate chain: `tail -n 1 worklog.md` = `REWORK round 5: gates 7/7 green`. `/tmp/erl0073_coord/snapshot.sh insurance_claims_and_denials 5` (executed, not read): views r5 `0.view.json` 7ebf1dbe0763df5d, `1.view.json` b27baf62fa936c45 (masked keys as before); gate snapshot 2026-10-21T05:52:30 — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; sha256 33c3157dfedb claim.extended.yaml, e48614b9837b task_tools.py (unchanged), 99a085a37abb tasks/0.json, d202558f3a22 tasks/1.json (re-hashed: match).
- World diff r4 → r5 (my diff of the views): only `units` on three charge lines — task 0 A9273 1 → 2, A4467 1 → 3; task 1 J8540 1 → 2; amounts, persona and frozen_time unchanged. No other computation reads those units (P4/P8 read amounts only).
- Worklog round-5 section read first; figures recomputed on the r5 views (/tmp/audit_claims_0073/derive5.py) before GT was opened. Sweeps: verbatim quotes, compute_basis coverage, baseline sentences, unique factor ids — clean.

### round-4 items — closure check (revision_5)
| item | status | evidence |
| --- | --- | --- |
| C19 | closed | P7 assembly: "replacements are made first, the per-line fees are added to them, the sum is then multiplied by the account class's own rule ..., the product is then capped at the drugs' charges, and the total is rounded once" = `RND(MN(sad_charges, (val_J8499 + val_J8540 + val_J7613 + val_fee) * account_noncovered_factor), 2)`. Class sweep: P1 "the sum is taken from the payment received (never below 0.00)"; P5 "the deduction after them (never below 0.00), the resulting retained payment is then taken from the payment received (never below 0.00)"; P2/P4/P6/P8 place their recovery limits; P3 replacements + one multiplier; P8 case-rate cap inside its own replacement — every sentence matches its compute |
| F10 | closed | P3 `cold_pack_quantity_share` / `support_garment_quantity_share` follow the quantity dispensed (take-home multi-pack pricing — a real lever); `take_home_kit_share` is the only co-billing reader; P7 `sad_pharmacy_dispensing_fee` follows the dispensing pharmacy (inpatient pharmacy for an observation stay at a hospital campus 0.50, ED cabinet 0.25, Chilton 0.00) — a dispensing fee set by who dispenses is real; the campus share and setting multiplier are gone |
| O14 | closed | bindings renamed to their meanings |
| tool rounding | no defect | amounts are posted as given; `round(float(x), 2)` leaves a two-decimal input unchanged |

### regression and exclusivity (revision_5)
- F9 unit-charge axis: my sweep (0.50 … 400.00 with every former band edge) is non-decreasing for all six items; P3 item values ≤ item charges by construction, P7 capped (tiny-charge probe 2.10 ≤ 2.10).
- Quantity axis (new levers): one line, 1 … 9 units at the seeded unit charge — non-decreasing for E0218, A9273, A4467, J8540, J7613 (n × share_n ≥ (n−1) × share_(n−1) holds for every tier boundary); **not for J8499** (F11).
- Untouched figures unchanged (11058.88 / 38.30 / 9117.24; 4044.57 / 12.33 / 2321.99); trees, edges, skip figures and order unchanged; each task's policies 0.00 on the other task's world. XF A–E hold on P3 and P7 apart from F11.

### findings (revision_5)
**F11 SOURCE-FACTOR RED (F9 class on the quantity axis; pre-existing since revision_3) — P7 `oral_drug_valuation`.** Tiers: "lesser of their charges and sad_line_price per dispensing line when they were dispensed on more than one line, ... the lesser of their charges and their billed units times sad_unit_price when they were dispensed on a single line of more than one unit, and at their charges otherwise." A single one-unit J8499 line is written off at its full charge, a single two-unit line at 2 × 7.00. Probe on task 1's world (J8499 collapsed to one line at the seeded 21.00 per unit): 1 unit → 38.50, 2 units → 31.50, 3 → 38.50 — one dose is valued 21.00, two doses 14.00. A self-pay dose price list that values one dose above two is not one Riverbend would publish; the fall-through (the charges) is not the list's own treatment of a single dose. My revision_4 F9 sweep covered unit charges only and missed this axis. Bears on task 1 step 12 (37.00 rests on this factor's multi-line tier).

### observations (revision_5)
- O2, O3, O5, O7, O8, O10, O11, O12 kept.

## closing_status (revision_5)
Both trees hold; both derivations equal GT figure by figure (task 0: 11058.88 / 38.30 / 312.56 / 9117.24; task 1: 4044.57 / 12.33 / 37.00 / 2321.99). Task 0 passes all four relationships on this revision; task 1 carries F11. Open: F11.

VERDICT revision_5: task0=PASS task1=RED charter=F11

## revision_6

### entry evidence (revision_6) — not blind
- Gate chain: `tail -n 1 worklog.md` = `REWORK round 6: gates 7/7 green`. `/tmp/erl0073_coord/snapshot.sh insurance_claims_and_denials 6` (executed): views r6 `0.view.json` 7ebf1dbe0763df5d, `1.view.json` b27baf62fa936c45 (unchanged since r5); gate snapshot 2026-10-21T06:17:23 — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; sha256 96ec20278b24 claim.extended.yaml, e48614b9837b task_tools.py, 99a085a37abb tasks/0.json (byte-identical to r5), e8a0d3559671 tasks/1.json (re-hashed: match).
- Worklog round-6 section read first; figures recomputed on the r6 views (/tmp/audit_claims_0073/derive6.py) before GT. Mechanical sweeps clean (verbatim quotes, compute_basis coverage, baseline sentences, unique factor ids).

### round-5 item — closure check (revision_6)
| item | status | evidence |
| --- | --- | --- |
| F11 | closed | `oral_drug_quantity_share` replaces `oral_drug_valuation` (share 1 / 0.60 / 0.45 for 1 / 2 / 3+ units; n × share_n non-decreasing). Probe on task 1's world with J8499 collapsed to one line at 21.00 per unit: 1 → 38.50, 2 → 42.70, 3 → 45.85, 4 → 55.30, 5 → 64.75. The method slot moves to `sad_pharmacy_dispensing_fee` (per line from the inpatient pharmacy / one fee per ED visit from the ED cabinet / none): per-line vs per-visit vs none differ in input, and a dispensing fee set by who dispenses is real |
| caps added in P1, P2, P4, P5, P6, P8 | checked | each assembly sentence now places "never above the billed charges of the lines it values"; computes match; no cap binds on either task world |

### exhaustive two-axis sweep (revision_6)
Scratch /tmp/audit_claims_0073/sweep6.py: for every charge line of each task's account and for each of the eight policies on its own handling-time world, the line's quantity 1 … 8 at its seeded unit charge and its unit charge over 0.01 … 8000.00 (29 points incl. every former band edge) at its seeded quantity; flags a write-off/close-out value that falls, a refund that rises, or a step larger than the charge step. 35 flags, all listed here:
- 28 are the small-item route test (P2 J2405/J1100/J0690/A4570/J7050; P6 J2405/J1885/J7050/A4216 on both axes) and the matching root steps (P4, P8): each flag is exactly the point where the code's charges pass the 50.00 small-denial amount, the code leaves the small-item write-off and its whole charges re-enter the root at the expected allowed percentage. The sum across the tree rises at every such point; this is a route switch stated by both rules, not a price. Not a defect.
- 1 is a defect: P8 `0762/G0378` quantity 7 → 8 hours at 68.00 per hour, 823.57 → 796.29 (finding F12). Hour sweep 1 … 60 at 20 / 40 / 68 / 120 per hour: the value falls at 7 → 8 hours for 20.00 (504.37 → 431.49), 40.00 (637.37 → 583.49) and 68.00 per hour; not at 120.00.
- No flag on any P1, P3, P5 or P7 line; no refund rises; no cap breach.

### task 0 regression (revision_6)
`tasks/0.json` byte-identical; P1–P4 recomputed on the charter with the new caps: 11058.88 / 38.30 / 312.56 / 9117.24, every single-factor and all-baseline figure unchanged, skips 0.00 / 9214.11 / unchanged; the only sweep flags in task 0's policies are small-item route switches. No regression. Cross-task: each task's policies 0.00 on the other task's world.

### findings (revision_6)
**F12 SOURCE-FACTOR RED (value falls as quantity rises; present since revision_4's case-rate cap) — P8 `general_pharmacy_handling` packages pharmacy without the case rate it packages into.** Tier: "The general pharmacy is packaged into the observation stay and carries no value when a Commercial HMO claim bills 8 or more observation hours (code G0378)". The case rate it is packaged into is "never above the observation charges" — the cap compares the case rate with the observation lines only, not with the pharmacy it absorbs — and the packaging tier does not require the case rate at all: a Commercial HMO observation stay at Riverbend Community Hospital - Chilton is priced at the expected allowed percentage of the observation charges (no case rate), yet its pharmacy is still "packaged into the observation stay" and carries no value. Consequences: at a low per-hour observation charge the close-out falls when the stay passes 8 hours (68.00/hour: 823.57 at 7 hours, 796.29 at 8); on an HMO Chilton stay the pharmacy is dropped with no package to absorb it. A lesser-of-charges contract compares the case rate with the billed charges of everything it packages, and packages only into a rate that is paid. Task 1 takes this tier (HMO, 46 hours, Neenah — case rate paid, cap not binding), so its step 14 figure rests on the factor; no second number arises on task 1's own world.

### observations (revision_6)
- O2, O3, O5, O7, O8, O10, O11, O12 kept.

## closing_status (revision_6)
Both trees hold; both derivations equal GT figure by figure (task 0: 11058.88 / 38.30 / 312.56 / 9117.24; task 1: 4044.57 / 12.33 / 45.00 / 2321.99). Task 0 passes; open: F12 (P8, task 1).

VERDICT revision_6: task0=PASS task1=RED charter=F12

## revision_7

### entry evidence (revision_7) — not blind
- Gate chain: `tail -n 1 worklog.md` = `REWORK round 7: gates 7/7 green`. `/tmp/erl0073_coord/snapshot.sh insurance_claims_and_denials 7` (executed): views r7 `0.view.json` 7ebf1dbe0763df5d, `1.view.json` b27baf62fa936c45 (unchanged); gate snapshot 2026-10-21T19:22:49 — all 7 OK; sha256 2080a4acf10f claim.extended.yaml, e48614b9837b task_tools.py, ca5aca9cc6bd tasks/0.json, f760feedf1c4 tasks/1.json (re-hashed: match).
- Worklog round-7 read first; figures recomputed on r7 (/tmp/audit_claims_0073/derive7.py) before GT. Mechanical sweeps clean; 42 unique factor ids.

### round-6 item — closure check (revision_7)
| item | status | evidence |
| --- | --- | --- |
| F12 | closed | P8: the observation case rate "packages the general pharmacy (revenue code 0250), is never above the billed charges of the observation and general pharmacy lines it packages"; the pharmacy carries no value only when that case rate is paid (`pharmacy_value = 0 if (obs_method == 2 and obs_hours > 0)`), otherwise it is valued at the expected allowed percentage. My joint sweep (below) finds no fall at 7 → 8 hours or anywhere along hours for any hourly charge |
| new/changed levers | judged real | P8 `sterile_supply_percentage` (0272 at 0.25 HMO / 0.33 PPO on an observation stay) — a contract supply percentage by supply class; P4 `crutch_take_home_rate` (E0114 31.50 PPO at Grand Chute / 36.00 HMO at a hospital campus / percentage, capped at charges) — a DME take-home rate; P4 ancillaries packaged only into the paid arthroscopy case rate, capped at the operating-room + ancillary charges; P1 typing packaged only when that case rate is paid (29882) |

### exhaustive sweep (revision_7)
1. Every charge line of both accounts × all eight policies on their handling-time worlds, quantity 1 … 8 and unit charge 0.01 … 8000.00 (sweep7.py): 34 flags, all the small-item route switch (an item's charges passing 50.00 leave the small-item write-off and re-enter the root) in P2/P6 and the matching steps in P4/P8 — not defects (revision_6 reasoning). The revision_6 G0378 member is gone; no other flag.
2. Joint packaging / case-rate / cap grids (joint7.py):
   - P8: G0378 hours 0 … 72 × hourly charge {5, 20, 40, 68, 120, 200} × general-pharmacy charge {0, 50, 186, 1000, 3000}, for HMO at Neenah (case rate), HMO at Chilton (percentage), PPO (hourly), Marketplace at Appleton — 8760 points. Falls: 6, all at hours 0 → 1 with a 3000.00 pharmacy line on HMO Neenah (1756.93 → 1205.93): billing the first observation hour turns on the case rate, which packages the pharmacy. A case rate is paid whatever the packaged charges; the switch is the rate's own condition (an observation stay with no hour billed has no case rate). Not a defect.
   - P4: 29882 charge {0 … 12000} × 29877 charge × ancillary charge {0 … 20000}, for PPO at Grand Chute, HMO at Appleton, Marketplace at Chilton — 630 points. Falls: 6, all on PPO when a 29882 line is added to an account with large ancillary charges (e.g. ancillaries 20000.00: 11020.58 → 8272.18): billing the repair turns on the arthroscopy case rate, which packages the ancillaries. Same reasoning: the case rate's own condition. Not a defect.
   - P5: 71275 charge {0 … 6000} × Q9967 millilitres {0 … 200}, for HMO, PPO, Marketplace — 144 points. Falls (refund rises, i.e. retained value falls) when contrast goes from 0 to 1 ml with the CT billed: HMO 3480.00 CT, refund 3010.57 → 4077.75; PPO 3010.57 → 3863.46 at the same CT (2625.66 → 3863.46). Finding F13.

### task 0 (revision_7)
Gold moved by the class sweep (P4 9117.24 → 9111.77: crutches at 31.50 instead of 64.00 × 58.5%), recomputed and equal; P1–P3 unchanged; skips 0.00 / 9208.65 / unchanged; every task-0 sweep flag is a route switch or the arthroscopy case-rate switch. Task 0 does not regress.

### findings (revision_7)
**F13 SOURCE-FACTOR RED (value moves against the billed service; condition present since revision_3) — P5 `ct_angiography_pricing`.** "The CT angiography is valued at its billed units times cta_fee_hmo when a Commercial HMO claim bills contrast (code Q9967) with it, at the lesser of its billed units times cta_fee_ppo and the charges of the scan and the contrast that rate packages when a Commercial PPO claim bills contrast with it, and at the payer class's expected allowed percentage of its charges otherwise." 71275 is the CT angiography code, contrast included by definition; whether a separate Q9967 line is coded does not move a payer from its per-code fee to a percentage of charges. Consequence on task 1's world: the same 3480.00 scan is retained at 1809.60 (52%) with no contrast line and at 742.00 + 0.42 with one millilitre, so billing contrast raises the refund from 3010.57 to 4077.75; on a PPO claim from 3010.57 to 3863.46. The fall-through is not a treatment a payer gives a CTA billed without a separate contrast line. Task 1 step 8 (4044.57) rests on this factor's HMO tier. I accepted this condition when it replaced F8 in revision_3; the joint sweep shows its effect.

### observations (revision_7)
- O2, O3, O5, O7, O8, O10, O11, O12 kept.

## closing_status (revision_7)
Both trees hold; derivations equal GT (task 0: 11058.88 / 38.30 / 312.56 / 9111.77; task 1: 4044.57 / 12.33 / 45.00 / 2317.43). Task 0 passes; open: F13 (P5, task 1).

VERDICT revision_7: task0=PASS task1=RED charter=F13

## revision_8

### entry evidence (revision_8) — not blind
- Gate chain: `tail -n 1 worklog.md` = `REWORK round 8: gates 7/7 green`. `/tmp/erl0073_coord/snapshot.sh insurance_claims_and_denials 8` (executed): views r8 `0.view.json` 7ebf1dbe0763df5d, `1.view.json` b27baf62fa936c45 (unchanged); gate snapshot 2026-10-21T19:50:37 — all 7 OK; sha256 5feb0e814cea claim.extended.yaml, e48614b9837b task_tools.py, a7b069e40ca7 tasks/0.json, 3708de7b0add tasks/1.json (re-hashed: match).
- Worklog round-8 read first; figures recomputed on r8 (/tmp/audit_claims_0073/derive8.py) before GT. Mechanical sweeps clean; 42 unique factor ids; every policy keeps ≥ 2 parameter and ≥ 1 method factors (P2: splint_pricing; P5: ecg_tracings_counted, retained_lab_pricing, contrast_handling).

### round-7 item — closure check (revision_8)
| item | status | evidence |
| --- | --- | --- |
| F13 | closed | P5 `ct_angiography_code_rate` (parameter): 71275 at billed units × its per-code rate (HMO 742.00 / PPO 798.00 / otherwise charges per unit × percentage) whether or not Q9967 is billed. My CT × contrast grid (71275 0 … 6000 × Q9967 0 … 200 ml × HMO / PPO / Marketplace, 144 points): the refund never rises as contrast or CT charges are added (0 falls of the retained value) |
| code-keyed tiers (reworker's sweep) | re-checked | my own list of every factor tier conditioned on another billed line: P1 typing (PPO, 29882 billed — packaged into the surgical case that the post-payment denial refunds: coherent); P3 kit share (the kit's own bundle); P4 arthroscopy case rate (its own code) with ancillaries packaged into it; P5 contrast (PPO) — finding F14; P8 pharmacy packaged into the paid observation case rate. P1 typing HMO tier and P2 `cefazolin_unit_rate` no longer read another line |

### exhaustive sweep (revision_8)
- Every charge line × all eight policies, quantity 1 … 8 and unit charge 0.01 … 8000.00 (sweep8.py): 34 flags, all the small-item route switch and its root steps (unchanged from revision_7; not defects).
- Joint grids (joint8.py): P8 hours × hourly × pharmacy × four payer/campus cases — 6 falls, all the hours 0 → 1 case-rate switch; P4 procedure × ancillary × three cases — 6 falls, all the 29882 case-rate switch (both judged in revision_7: the case rate's own condition, not defects); P5 CT × contrast — 0.
- Packaging probe (P5, beyond the grids): a PPO claim billing contrast with a CT that is not 71275 (a 70450 line of 1000.00): contrast retained 0.00 vs 51.48 with no CT line; on HMO 33.60 either way (finding F14).

### task 0 (revision_8)
`tasks/0.json` changed only in the renamed cefazolin factor and tier labels; figures recomputed: 11058.88 / 38.30 / 312.56 / 9111.77; every single-factor and all-baseline figure and skip equal; P2 `cefazolin_unit_rate` 59.98 at baseline. No regression.

### findings (revision_8)
**F14 SOURCE-FACTOR RED (packaging into a rate that is not paid; F12 class) — P5 `contrast_handling` PPO tier.** Rule: the contrast "is packaged into the per-code rate of the computed tomography it is billed with (revenue code 0350), and carries no value of its own, on a Commercial PPO claim that bills such a scan"; compute tests any 0350 charge (`XSUM(... revenue_code='0350') > 0`). The only computed tomography with a per-code rate is 71275; every other 0350 line is "every other charge ... by its charges" at the expected allowed percentage, so no rate absorbs the contrast. Probe on task 1's world switched to PPO with a 70450 line of 1000.00 and no 71275: 80 ml of contrast retain 0.00 (refund 4076.46 with or without the contrast), against 51.48 when no scan is billed. Hypothetical for task 1 (HMO, contrast on the per-millilitre tier) and absent from task 0's domain.

### observations (revision_8)
- O2, O3, O5, O7, O8, O10, O11, O12 kept.

## closing_status (revision_8)
Both trees hold; derivations equal GT (task 0: 11058.88 / 38.30 / 312.56 / 9111.77; task 1: 4044.57 / 12.33 / 45.00 / 2317.43). Task 0 and task 1 pass their four relationships on their own worlds; open charter RED: F14 (P5 PPO tier, no task consequence).

VERDICT revision_8: task0=PASS task1=PASS charter=F14

## revision_9

### entry evidence (revision_9) — not blind
- Gate chain: `tail -n 1 worklog.md` = `REWORK round 9: gates 7/7 green`. `/tmp/erl0073_coord/snapshot.sh insurance_claims_and_denials 9` (executed): views r9 `0.view.json` 7ebf1dbe0763df5d, `1.view.json` b27baf62fa936c45 (unchanged); gate snapshot 2026-10-21T20:22:59 — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; sha256 7b4dac40c14c claim.extended.yaml, e48614b9837b task_tools.py, a7b069e40ca7 tasks/0.json, 3708de7b0add tasks/1.json (both task files byte-identical to revision_8; re-hashed).
- Worklog round-9 read first; recomputed on r9 (/tmp/audit_claims_0073/derive9.py). Mechanical sweeps clean.

### round-8 item — closure check (revision_9)
| item | status | evidence |
| --- | --- | --- |
| F14 | closed | P5 `contrast_method` PPO tier now `F('variant_name') == 'Commercial PPO Claim' and XSUM(... revenue_code='0350', cpt_hcpcs_code='71275') > 0`; rule: "packaged into the CT angiography's per-code rate ... on a Commercial PPO claim that bills the CT angiography (71275), the only scan priced at a per-code rate covering the contrast"; `ct_value` caps at scan + contrast charges exactly when that tier packages. My probe (80 ml contrast, task 1 world) — contrast retained: PPO with 71275 3480.00 → 0.00 (packaged; CT at 798.00); PPO with 70450 only → 51.48; PPO no CT → 51.48; PPO with 71275 and 70450 → 0.00; PPO with 71275 at 500.00 (below its rate) → 88.00 (lesser of rate and scan + contrast charges); HMO → 33.60 and Marketplace → 41.80 in every combination |
| packaging tiers | re-checked | contrast → 71275 per-code rate (PPO, 71275 billed); ancillaries → arthroscopy case rate (`surgical_method == 2`); typing → the same case rate (PPO AND 29882 = the case-rate tier's condition); general pharmacy → observation case rate (`obs_method == 2 and obs_hours > 0`). Each packages only into a rate that is paid; no other rule packages a line |

### sweeps (revision_9)
- Every charge line × all eight policies, quantity 1 … 8 and unit charge 0.01 … 8000.00: 34 flags, all the small-item route switch and its root steps (unchanged; not defects).
- Joint grids: P8 6 and P4 6 falls, all the case-rate switch on its own condition (judged in revision_7); P5 CT × contrast × HMO / PPO / Marketplace: 0.
- Both tasks recomputed: 11058.88 / 38.30 / 312.56 / 9111.77 and 4044.57 / 12.33 / 45.00 / 2317.43, skips 0.00 / 9208.65 / unchanged and 0.00 / 2352.50 / unchanged — equal to the unchanged task files. No regression; cross-task exclusivity holds (each task's policies 0.00 on the other world).

### findings (revision_9)
None open. Observations O2, O3, O5, O7, O8, O10, O11, O12 kept (no scored consequence).

## closing_checklist (revision_9)
- Per-task files `0.md` and `1.md` correspond one-to-one with tasks 0 and 1; `_difficulty.md` alongside; revisions 1 … 9 appended, none rewritten (the revision_1 freeze-time line correction is recorded in place).
- Scope: task 0 = {surgery_post_payment_refund, surgery_small_item_closeout, noncovered_convenience_closeout, member_decision_closeout}; task 1 = {retrospective_denial_refund, observation_small_item_closeout, self_administered_drug_closeout, external_review_decision_closeout} — disjoint, jointly cover all eight extended policies and tools; each tool's uuid8 independent and frozen; tools judge nothing.
- Trees: each has 3 prerequisite problems, 3 value_input edges + 1 state_gate, an owner=user root, every prerequisite unmet at frozen_time, every value_input edge load-bearing; whole-difficulty graph acyclic.
- Factors: every computation declares 4–6 factors with ≥ 2 parameter and ≥ 1 method, a self-sufficient baseline stated in its rule, every factor load-bearing on its task's world, all-baseline figures different from gold; each task has multi-source and cross-difficulty (encounter) factors; every ladder's conditions and outcomes judged real across revisions 5–9 and swept for monotonicity, charge caps and packaging.
- Gates on the final form: coordinator snapshot 2026-10-21T20:22:59, all 7 OK (cited above; not re-run by the auditor per brief).

VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN

## revision_10

### entry evidence (revision_10) — not blind
- Gate chain: `tail -n 1 worklog.md` = `REWORK round 10: gates 7/7 green`. `/tmp/erl0073_coord/snapshot.sh insurance_claims_and_denials 10` (executed): views r10 `0.view.json` 7ebf1dbe0763df5d, `1.view.json` b27baf62fa936c45 (unchanged); gate snapshot 2026-10-21T21:25:09 — all 7 OK; sha256 a17e3ec30a41 claim.extended.yaml, e48614b9837b task_tools.py, 4e988804d476 tasks/0.json, d47d32af4fe5 tasks/1.json (re-hashed: match).
- Read in full: `audits/render_source/insurance_claims_and_denials/render_r1.md` (renderer items 1–6) and the worklog round-10 section. Recomputed on r10 (/tmp/audit_claims_0073/derive10.py); mechanical sweeps clean (verbatim quotes, compute_basis, baseline sentences in rules, 42 unique factor ids, 4–6 factors per policy).

### honest note on revision_9
All six renderer items were present when I issued `charter=CLEAN` in revision_9: items 1, 3 and 5 are rule-versus-compute mismatches my equivalence sweeps did not test at those inputs (per-line vs total cap, a definition stated twice, zero-unit edges); item 2 (CT cap reading the contrast tier) I examined in revision_7 and dismissed; item 4 (baseline naming quantities only one factor uses, XF A4) I did not check; item 6's "inpatient pharmacy / emergency department cabinet" wording I judged a real lever in revisions 5–6 without testing it against the records. I also did not re-check the P3/P7 quantity-share `tier_taken` labels after revision_5; the reworker reports and corrected false labels there (they now match the worlds: A9273 2 units "2 to 3", A4467 3 units "3 or more", J8499 3 "3 or more", J8540 2 "2 to 3", J7613 2 "2 to 5").

### renderer items — closure check (revision_10)
| item | status | evidence |
| --- | --- | --- |
| 1 ECG cap | closed | rule: "its counted units but no more than ecg_cap_per_line times its number of lines on a Commercial PPO claim" = compute `MN(MX(units,1), cap * lines)`; `ecg_value = MN(ecg_charges, counted * charges / MX(units,1) * pct)` — never above charges, as the assembly sentence says |
| 2 CT ↔ contrast coupling | closed as stated, with a regression | `ct_value = MN(cta_charges, MX(cta_units,1) * cta_rate)` reads only the CT; `contrast_handling` alone values Q9967. The PPO tier still packages the contrast into the 71275 rate, but that rate is now compared with the scan's charges only — finding F15 |
| 3 pre-operative tests defined twice | closed | definition and reading sentence both "every charge under revenue codes 0300 …, 0730 … and 0324 …", = `other_retained` |
| 4 baseline naming factor-only quantities | closed | every baseline reads its lines "by their charges" only (all 8 baselines read); units, line counts and hours are named in the sentence of the one factor that uses them, and compute_basis quotes those sentences; the member-decision and external-review "value is … plus …" sentences are removed (generic assembly sentence) |
| 5 zero/empty edges | closed | rate fall-throughs "its charges per counted unit times the expected allowed percentage", counted units = billed units or one; compute `MX(units,1)` with `MN(charges, …)`; at 0 units every rate family equals charges × pct (reworker's table, spot-checked in the computes); HMO contrast tier requires millilitres billed. (The frozen schema makes `units` a positive integer, so the edge is outside every real world.) |
| 6 SAD cap/lines and unrecorded framing | closed | `sad_charges` and `sad_lines` read only J8499, J8540, J7613; the dispensing fee is worded "on an Observation Stay Account at a hospital campus" / "on an Emergency Department Visit Account at such a campus" — the record tests the compute uses |

### sweeps (revision_10)
- Every charge line × all eight policies, quantity 1 … 8 and unit charge 0.01 … 8000.00: 34 flags, all the small-item route switch and its root steps (unchanged; not defects).
- Joint grids: P8 6 falls and P4 6 falls, all the case-rate switch on its own condition (judged in revision_7; P4 and P8 still cap each case rate at the charges of everything it packages: `MN(or_charges + ancillary_charges, …)`, `MN(case_rate, obs_charges + pharmacy_charges)`); P5 CT × contrast: HMO 0, Marketplace 0, **PPO 1** (F15).
- Both tasks recomputed: 11058.88 / 38.30 / 312.56 / 9111.77 and 4044.57 / 12.33 / 45.00 / 2317.43; skips 0.00 / 9208.65 / unchanged and 0.00 / 2352.50 / unchanged; every single-factor and all-baseline figure equals GT; tier labels match the worlds. Cross-task exclusivity holds. No task regression.

### findings (revision_10)
**F15 SOURCE-FACTOR RED (regression of the revision_9 fix; F12/F14 class — a packaging rate compared with charges that exclude what it packages) — P5 `ct_angiography_code_rate` + `contrast_handling` PPO tier.** The contrast "carries no value of its own on a Commercial PPO claim that bills the CT angiography (71275), whose per-code rate is the only scan rate covering the contrast", while the CT "is valued at its counted units times its per-code rate, never above its own charges". When the scan's charges are below its rate, the lesser-of pays the scan's charges and the packaged contrast gets nothing. Probes on task 1's world switched to PPO, 80 ml of contrast (88.00): 71275 at 500.00 or 700.00 → contrast retained 0.00 (revision_9: 88.00); and in the joint grid with 200 ml (220.00) of contrast, billing a 100.00 CTA lowers the retained value (refund 4532.76 → 4561.46): the contrast's 128.70 is packaged away into a rate capped at 100.00. A lesser-of contract compares its rate with the charges of everything it covers (the rule P4 and P8 follow). Task 1 is HMO (per-millilitre tier): no task consequence.

### observations (revision_10)
- O2, O3, O5, O7, O8, O10, O11, O12 kept.

## closing_status (revision_10)
Renderer items 1–6 closed; one member created by the item-2 fix is open. Both tasks pass their four relationships on their own worlds; open charter RED: F15.

VERDICT revision_10: task0=PASS task1=PASS charter=F15

## revision_11

### entry evidence (revision_11) — not blind
- Gate chain: `tail -n 1 worklog.md` = `REWORK round 11: gates 7/7 green`. `/tmp/erl0073_coord/snapshot.sh insurance_claims_and_denials 11` (executed): views r11 `0.view.json` 7ebf1dbe0763df5d, `1.view.json` b27baf62fa936c45 (unchanged); gate snapshot 2026-10-21T22:05:31 — all 7 OK; sha256 6836da5cbc46 claim.extended.yaml, e48614b9837b task_tools.py, 4e988804d476 tasks/0.json, d47d32af4fe5 tasks/1.json (both byte-identical to revision_10; re-hashed).
- Worklog round-11 read first; recomputed on r11 (/tmp/audit_claims_0073/derive11.py); mechanical sweeps clean. Only P5 changed (contrast_handling PPO tier, its compute_basis and ladder text).

### round-10 item — closure check (revision_11)
| item | status | evidence |
| --- | --- | --- |
| F15 | closed in value | `contrast_value` PPO branch `MX(0, MX(cta_units,1) * K('cta_fee_ppo') - cta_charges)` inside `MN(contrast_charges, …)`; with the CT on its PPO rate, CT + contrast = lesser of (units × 798.00, scan + contrast charges). Probes (task-1 world on PPO, 80 ml = 88.00): CTA 500.00 → contrast 88.00; CTA 3480.00 → 0.00. P5 CT × contrast grid (HMO / PPO / Marketplace): 0 falls |
| re-coupling | not closed — finding F16 | the contrast tier now restates the CT factor's PPO tier (its rate `cta_fee_ppo`, its counted units and charges) |

### sweeps (revision_11)
- Every charge line × all eight policies, both axes: 34 flags, all the small-item route switch and its root steps (unchanged; not defects).
- Joint grids: P8 6 and P4 6 falls, all the case-rate switch on its own condition (judged in revision_7); P5: 0 for HMO, PPO and Marketplace.
- Both tasks recomputed: 11058.88 / 38.30 / 312.56 / 9111.77 and 4044.57 / 12.33 / 45.00 / 2317.43; skips 0.00 / 9208.65 / unchanged and 0.00 / 2352.50 / unchanged; equal to the unchanged task files. Cross-task exclusivity holds. No task regression.

### findings (revision_11)
**F16 SOURCE-FACTOR RED (XF A1/A4 — one factor's tier carries another factor's tier) — P5 `contrast_handling` PPO tier vs `ct_angiography_code_rate`.** Mechanically the contrast factor reads no binding of the CT factor, but its PPO tier is "packaged into the scan's per-code rate, compared with the scan and contrast charges together: the part of the CT angiography's counted units x cta_fee_ppo its own charges leave unused" — the CT factor's PPO tier value (`cta_fee_ppo`, the only param used by two factors' ladders), the CT's counted units and the CT's charges. It therefore does not stand alone: substitution test on task 1's world switched to PPO — with the CT factor set to its baseline (the scan at 58.5% of its charges, no per-code rate paid), the contrast is still valued as the remainder of the 798.00 rate: CTA 3480.00 → contrast 0.00 (packaged into a rate the substituted CT does not use), CTA 500.00 → contrast 88.00 against a scan valued at 292.50. The contrast's computation document would have to state the CT angiography's PPO rate, which is the coupling the renderer's item 2 named. The packaging lesser-of covers two lines, so it couples them wherever it is split across two factors; P4 (ancillaries in the arthroscopy case rate) and P8 (pharmacy in the observation case rate) keep each package inside the one factor that owns both families. Task 1 is HMO (per-millilitre tier): no task consequence.

### observations (revision_11)
- O2, O3, O5, O7, O8, O10, O11, O12 kept.

## closing_status (revision_11)
F15 closed in value; its closure re-couples the CT and contrast factors (F16). Both tasks pass their four relationships on their own worlds; open charter RED: F16.

VERDICT revision_11: task0=PASS task1=PASS charter=F16

## revision_12

### entry evidence (revision_12) — not blind
- Gate chain: `tail -n 1 worklog.md` = `REWORK round 12: gates 7/7 green`. `/tmp/erl0073_coord/snapshot.sh insurance_claims_and_denials 12` (executed): views r12 `0.view.json` 7ebf1dbe0763df5d, `1.view.json` b27baf62fa936c45 (unchanged); gate snapshot 2026-10-21T22:24:23 — all 7 OK; sha256 e1af5953534e claim.extended.yaml, e48614b9837b task_tools.py, 4e988804d476 tasks/0.json (byte-identical), b6a28533b8d1 tasks/1.json (re-hashed: match).
- Worklog round-12 read first; judged as the coordinator's accepted route (one factor owns the CT-angiography family; one added lever under T1/T2). Recomputed on r12 (/tmp/audit_claims_0073/derive12.py); mechanical sweeps clean; 42 unique factor ids; P5 has 6 factors (3 parameter, 3 method).

### round-11 item — closure check (revision_12)
| item | status | evidence |
| --- | --- | --- |
| F16 | closed | `ct_angiography_family_pricing` (method, binding `cta_method`) owns 71275 + Q9967 on every payer: PPO with 71275 — `MN(scan + contrast charges, MX(units,1) × cta_fee_ppo)`; HMO — scan `MN(charges, units × cta_fee_hmo)` + contrast `MN(charges, ml × contrast_ml_hmo)` (percentage when no ml); otherwise the family at the percentage = baseline. `ct_angiography_code_rate` and `contrast_handling` are gone; no param is used by two factors' ladders; no other factor reads 71275 or Q9967. Rule sentence ("Riverbend's imaging agreements price the CT angiography … and the contrast supply line (Q9967) as one family …") = compute. Tiers differ in shape (one lesser-of over both lines / two per-line rates / percentage) |
| added lever `diagnostic_campus_factor` | real; T1/T2 pass | provider-based campus differential on the sum of retained test values (Neenah 0.95, Chilton 1.04, Appleton 1), the same differentials as P8's campus factor; retained value capped at the diagnostic charges, the multiplier's place stated in the assembly sentence. T1: at its baseline task 1's refund is 4044.57 vs gold 4121.86. T2: with every other P5 factor at baseline, 2264.10 (Neenah) vs all-baseline 2096.92 |

### sweeps (revision_12)
- Every charge line × all eight policies, both axes: 34 flags, all the small-item route switch and its root steps (unchanged; not defects).
- P5 CT × contrast grid, now × campus: 71275 {0 … 6000 incl. 741.99/742/797.99/798/798.01} × Q9967 {0 … 200 ml} × HMO / PPO / Marketplace × Neenah / Appleton / Chilton — 756 points, 0 falls of the retained value. P8 6 and P4 6 falls: the case-rate switch on its own condition (judged in revision_7).
- Task 1 gold move checked: step 8 = 5440.52 − (1545.9535 × 0.95 − 150.00) = 4121.86 (my recomputation 4121.86); steps 10/12/14 unchanged (12.33 / 45.00 / 2317.43), recovery limits 4121.86 and 4109.53 not binding; terminal payer balance 1835.10; P5 `factor_sensitivity` 3646.10 / 4044.80 / 3992.70 / 3096.09 / 4044.57 / 3971.86 and all-baseline 2096.92 equal mine; tier labels match the world; closure `flips_to_true_by` texts carry 4121.86; the remaining "4044.57" strings in tasks/1.json are the campus factor's baseline result (correct), no stale 1757.81.
- Task 0: 11058.88 / 38.30 / 312.56 / 9111.77, skips unchanged; tasks/0.json byte-identical. Cross-task exclusivity holds.

### findings (revision_12)
None open. Observations O2, O3, O5, O7, O8, O10, O11, O12 kept (no scored consequence).

## closing_checklist (revision_12)
- Per-task files `0.md` / `1.md` ↔ tasks 0 / 1; `_difficulty.md` alongside; revisions 1 … 12 appended, none rewritten (revision_1 freeze-time line correction recorded in place).
- Scope: task 0 = {surgery_post_payment_refund, surgery_small_item_closeout, noncovered_convenience_closeout, member_decision_closeout}; task 1 = {retrospective_denial_refund, observation_small_item_closeout, self_administered_drug_closeout, external_review_decision_closeout}; disjoint, jointly cover all eight extended policies and tools; uuid8s independent and frozen; tools judge nothing.
- Trees: 3 prerequisite problems each, 3 value_input + 1 state_gate edges, owner=user roots, every prerequisite unmet at frozen_time, every value_input edge load-bearing; graph acyclic.
- Factors: 4–6 per computation with ≥ 2 parameter and ≥ 1 method; self-sufficient baselines stated in their rules; every factor load-bearing on its task's world, all-baseline ≠ gold; multi-source and cross-difficulty (encounter) factors in each task; ladders swept for realism, monotonicity in quantity and unit charge, billed-charge caps, packaging into paid rates, and factor coupling.
- Gates on the final form: coordinator snapshot 2026-10-21T22:24:23, all 7 OK (cited; not re-run by the auditor per brief).

VERDICT revision_12: task0=PASS task1=PASS charter=CLEAN

## revision_13

### entry evidence (revision_13) — not blind
- Gate chain: `tail -n 1 worklog.md` = `REWORK round 13: gates 7/7 green`. `/tmp/erl0073_coord/snapshot.sh insurance_claims_and_denials 13` (executed): views r13 `0.view.json` 14bff4b24bcb11ed (seed changed), `1.view.json` b27baf62fa936c45 (unchanged); gate snapshot 2026-10-22T00:10:47 — all 7 OK; sha256 b4b478fb4fbe claim.extended.yaml, e48614b9837b task_tools.py, 6769ef6a9d7a tasks/0.json, b6a28533b8d1 tasks/1.json (byte-identical; both re-hashed).
- Read: the Source-side items section of `audits/policy_kb/insurance_claims_and_denials/_difficulty.md` (src-1 … src-3), the worklog round-13 section, and the published encounter docs `insured_account_payoff_in_full`, `insured_payoff_amount_calculation`, `insured_payoff_days_to_pay_schedule`, `insured_payoff_paperless_allowance`, `insured_payoff_liability_size_points`, `insured_payoff_noncovered_share_points`, `check_in_payment_allowance_insured`, `insured_estimate_variance_credit`, `prompt_pay_terms`, `prompt_pay_discount_policy`. `audits/runtime_context/` not read.

### honest note
In revisions 1–12 I judged the task-0 ED payoff rows against the base encounter charter (10% prompt-pay discount), which the published encounter KB marks "no longer in force" (`prompt_pay_discount_policy` §2); I had not read the encounter difficulty's extended rule. src-2 is my O12, which I kept as an observation throughout.

### KB source items — closure check (revision_13)
| item | status | evidence |
| --- | --- | --- |
| src-1 | closed | ED account 33a1a49e is COMMERCIAL, so the published insured payoff rule applies (`insured_account_payoff_in_full`). Records: balance standing 420.00 (DEDUCTIBLE liability fbcef3a7); Emergency Department class 10%, window 30 days, minimum 100.00 (`prompt_pay_terms`) — met; PORTAL_CARD eligible; no charity adjustment, no plan; days to pay 2025-12-08 → 2025-12-20 = 12 → +2 (`…days_to_pay_schedule`: 11–20); latest summary statement 220581cd by PATIENT_PORTAL → +1; liability total 420.00 < 1000.00 → 0; non-covered share 0 → 0; no point-of-service payment → 0; no linked insured estimate (no estimate tables in the world) → no credit; no non-covered liability, so the "fixed only after an uninsured discount" sentence does not bite. 13% of 420.00 = 54.60, half-up exact; payment 365.40. Seed rows now 6a39fe5d payment 365.40 and d181e508 PROMPT_PAY_DISCOUNT 54.60 sourced to that payment; patient_balance 0.00 = 420.00 − 365.40 − 54.60; account closed 2025-12-20; claim 14955304 rows unchanged (PR-1 420.00). No "378.00" left in tasks/0.json; the seed_consistency line states the insured payoff derivation. Other cross-category payoffs re-checked against the same docs: task-1 observation copay 150.00 below the 250.00 Observation minimum (no discount — correct); clinic copay paid at point of service before any statement (no prompt-pay — correct); task-0 surgery account carries no patient liability. |
| src-3 | closed | P1 rule: "keep no value of their own when a Commercial PPO claim bills code 29882 under revenue code 0360 (Riverbend's PPO agreements bundle pre-operative typing with that knee procedure)"; ladder tier "bundled with that procedure under the PPO agreements: no value"; the compute is unchanged (PPO AND 29882 record test). Sweep of every rule and ladder for references to another policy's quantity ("case rate", "per-code rate", member-decision / close-out / refund / small-item / convenience / drug value, outside the sibling-scope overwrite restatements): every remaining mention is in its own policy (P4 arthroscopy case rate, P8 observation case rate). tasks/0.json `tier_taken` for this factor carries the new tier text; figure 11023.78 unchanged. |
| src-2 | not closed — kept as observation O12 (structural, outside this audit's RED threshold) | Both remittances still leave the non-covered lines as payer balance with no remittance line (task 0: 623.00 = E0218 590.00 + A9273 9.00 + A4467 24.00; task 1: 88.00 = the four 0637 lines). I accept the reworker's analysis that the frozen claim schema has no row that records a reported-but-unposted PR-204 line: a `claim_patient_resp_transferred` PR-204 (with its encounter NONCOVERED_SERVICE liability) would release the items to the patient, contradicting base routing without a waiver and switching off P3/P7 ("no non-covered patient liability"); a CO-45/CO-96 `claim_contractual_adjustment` would take the amount off the payer balance before the write-off, which would then drive payer_balance to −623.00 / −88.00; a 0.00 row breaks the amount format. No scored figure, tree edge or unique-solution reading depends on the missing line (P3/P7 value the items from their charges). Resolution lies at blueprint level (a remittance-line event that does not move payer_balance, or remit fields on the write-off) or in a rule-plus-tool change (non-covered write-offs carrying carc PR-204); both are outside this difficulty's seed-only round. Reported, not counted as a RED. |

### regression (revision_13)
- Mechanical sweeps clean; compute and params of all 8 policies unchanged in effect.
- Recomputed: 11058.88 / 38.30 / 312.56 / 9111.77 and 4121.86 / 12.33 / 45.00 / 2317.43; skips 0.00 / 9208.65 / unchanged and 0.00 / 2352.50 / unchanged; terminal payer balances 2219.25 / 1835.10; GT `expected` and `baseline_result` equal mine. No gold move (no task policy reads another account's payments or adjustments).
- Sweeps: every line × eight policies × both axes — 34 flags, all the small-item route switch; joint grids — P8 6 / P4 6 case-rate switches (judged in revision_7), P5 0. Cross-task exclusivity holds (each task's policies 0.00 on the other world).

### findings (revision_13)
None open as a RED. Remaining reported item: src-2 / O12 (above). Other observations O2, O3, O5, O7, O8, O10, O11 kept.

## closing_checklist (revision_13)
Unchanged from revision_12, with the task-0 cross-category seed now priced under the published insured payoff rule; gates on the final form: coordinator snapshot 2026-10-22T00:10:47, all 7 OK.

VERDICT revision_13: task0=PASS task1=PASS charter=CLEAN

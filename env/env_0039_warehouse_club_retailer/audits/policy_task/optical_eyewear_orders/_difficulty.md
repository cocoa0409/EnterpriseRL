# Policy-task audit — optical_eyewear_orders / charter-global

## charter_global_frozen

- Scenario: `env/env_0039_warehouse_club_retailer`; difficulty `optical_eyewear_orders`; category `optical`; M = 2.
- Frozen inputs (sha256 re-computed by the auditor at audit start, all equal to the brief):
  - `tasks/optical_eyewear_orders/optical.extended.yaml` 94a1609de3a7665e94ff6a5ab93ecee7af2f43b8740c35dcbf5351e9584b8b8f
  - `tasks/optical_eyewear_orders/task_tools.py` 8a14b96eb52b01e45df06698e7c7a738872cb52035ab6917c240d4ccd5e45722
  - `audits/views/policy_task/optical_eyewear_orders/0.view.json` e18646cbf7e2b76aab4f549f8183ea55b42a4de056e664dfb01f8587448b1f9f
  - `audits/views/policy_task/optical_eyewear_orders/1.view.json` 144a709f93ab3e09958ae9815ea282eb4c6ff8c212f866a6edc2ea1c49dde90b
- Freeze time: 2026-10-05T21:33:53Z. Auditor: independent policy-task auditor (Claude agent); not the author of the artifacts.
- Read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/optical.yaml` (plus the membership/card/order charters only to check the cross-difficulty seeds against their own charters), the extended charter, `task_tools.py`, the two masked views, and the compute evaluator in `skills/erl-task-instantiate/scripts/check_compute.py` (to learn the semantics of `MONTHS`/`DAYS`/`XSUM`/`CFIELD`/`P`).
- Masked and NOT read at the time of writing this file: `tasks/optical_eyewear_orders/tasks/{0,1}.json` (all of `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`), `worklog.md` (never opened), any earlier audit. No recursive search touched `env/env_0039_warehouse_club_retailer/tasks/`.
- Entry conditions (Step 0): gate snapshot supplied with the brief — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; TRACEABILITY NOT OK, declared as expected (depends on the KB `docs/` not yet rendered, deferred to step 3). Masked views supplied with hashes. Entry accepted; the traceability gate stays open and is carried into `closing_checklist`.
- This file was written before either task's GT was revealed and contains nothing derived from GT. Anything added after the reveal is under `## closing_checklist`.

### policy_conflict_scan

Base copy: lines 1–881 of the extended charter are byte-identical to `blueprint/products/optical.yaml` (`diff` shows only the 4 trailing banner lines added after line 881). Base is not rewritten.

Extended policies (7) and their claimed writes:

| id | target_tool (owner) | computes | trigger | prerequisite |
| --- | --- | --- | --- | --- |
| P1 `optical_ext_switch_difference_credit` | `post_switch_difference_credit_2fd39c69` (agent) | switch_credit_usd | state_due | [] |
| P2 `optical_ext_late_rx_remake_waiver` | `waive_remake_overcharge_01693abf` (agent) | waived_amount_usd | state_due | [] |
| P3 `optical_ext_accidental_replacement_charge` | `authorize_damage_replacement_0a7f54ae` (user) | replacement_charge_usd | on_request | P1 (value_input, rd_lens_net), P2 (value_input, rd_paid_remakes) |
| P4 `optical_ext_frame_return_refund` | `confirm_eyewear_cancellation_a25e55a5` (user) | frame_refund_usd | on_request | [] |
| P5 `optical_ext_option_cancellation_refund` | `refund_lens_option_d067b0d2` (agent) | option_refund_usd | on_request | [] |
| P6 `optical_ext_material_cancellation_refund` | `refund_lens_material_ad7f47c2` (agent) | material_refund_usd | on_request | [] |
| P7 `optical_ext_lens_cancellation_refund` | `post_lens_cancellation_refund_d976b5a7` (agent) | lens_refund_usd | on_request | P4 (state_gate, optical_holdings.status), P5 (value_input, rt_pool), P6 (value_input, rt_pool) |

Overlap scan:
- Subjects/charges written: P1 a `return_refund` credit on the base-lens charge (dispensed, switched-down job); P2 a `remake_charge_waived` credit on a prescription-change remake charge; P3 an `accidental_damage` remake charge; P4 status → cancelled + `cancellation_refund` on the frame charge; P5 on an option charge; P6 on the material charge; P7 on the base-lens charge of a cancelled job. No two policies write the same `(charge, credit_reason)` pair in the same lifecycle state: P1 and P7 both credit the base-lens charge, but P1 needs a dispensed, remade job and P7 a job cancelled in the lab — disjoint states (`dispensed`/`remake_in_lab` vs `in_lab`→`cancelled`).
- Eligibility/time anchors: P1/P2/P3 read the dispensed date and remake rows; P4–P7 read the order date and the lab state. No shared anchor reaches opposite conclusions.
- Cross-category reads: membership `opened_date` (P1, P2, P4, P7), card `status` (P2, P7), card `card_transactions.qualifying_spend` (P3, P5), order `order_lines.line_amount` (P1, P6). All read-only; no policy writes another category.
- Terminal states: P3 leaves the job `remake_in_lab`; P4 leaves it `cancelled`; the others only add credits. No conflict.
- Scope partition: the prerequisite graph has exactly two connected components, {P1, P2, P3} (root P3) and {P4, P5, P6, P7} (root P7). Two tasks, two trees → the natural partition is mutually exclusive and jointly covers all 7 extended policies. (Whether each task's declared `charter_scope` matches is checked after the reveal, in each task file.)

### rule_compute_equivalence

Mechanical sweep (auditor script, whitespace-normalised): every `compute_basis` quotation of all 7 policies is a verbatim substring of its own `rule`; every `baseline.rule` sentence is in the `rule`; every `overwrite.replaced_by` sentence is in the `rule`; every `superseded_clause` is verbatim in the named base policy's rule.

Sentence-by-sentence semantic sweep (both directions):
- P1: gap = original base-lens charge (remake 0) − all base-lens credits − current design's `base_lens_price_usd`, floored at 0 ✓; days = DAYS(dispensed, latest non-adapt remake) ✓; method ladder (first remake ∧ within window → whole; within window ∧ not first → pro-rata; else half) ✓; courtesy 10/5/0 by whole months held ✓; spend bonus on 12-month net sale − return lines ✓ (`XSUM ... within_months=12` = `0 <= MONTHS < 12`, i.e. "dated less than twelve whole months before"); refit 0 (≤30) / 7.50 (31–60) / 15.00 ✓; order uplift → +bonus → −fee → floor → round once ✓. Edge (observation O7): pro-rata branch divides by `P('non_adapt_window_days')`, which is 0 for Single Vision; a not-first switch down to Single Vision opened on day 0 gives a division by zero — no sentence of the rule covers a zero-length window.
- P2: **two gaps (finding G1, G3 below)**. (a) The rule's fall-through tier is a fixed "40 percent of the base lens price"; compute's fall-through is `P('remake_charge_pct_outside_coverage')`, which is 40 only for Premium/Freeform and 50 for Single Vision, Lined Bifocal, Lined Trifocal and Standard Progressive. The factor `rx_late_share_ladder.baseline` also binds `P(...)`, while `baseline.rule` says 40. (b) The rule's window-start tier 1 is "the opening date of the latest such non-adapt remake" (= latest non-adapt remake opened before the prescription-change remake); compute takes `LATEST(... non_adapt)` over the whole job and then tests `rx_na_date < rx_remake_date`, so a non-adapt remake opened after the prescription-change remake masks an earlier qualifying one. All other bindings ✓ (late share 20/30 bands, material re-bill whole/half, loyalty 15/10 with active linked card, fresh-prescription 10/5, handling fee 0/4.95/9.95, combined single reduction, round once). Observation: `rx_booked` sums every prescription-change remake charge while `rx_remake_date` is the latest one only — the rule speaks of "the" prescription-change remake; multi-rx-change jobs are not described by the rule.
- P3: basis = frame net + base-lens net ✓; clock anchor rx-change → non-adapt → dispensed ✓; pct 20 (≤6 whole months) / 25 (7–9) / `P('accidental_damage_charge_pct')` (=30 on every design with accidental coverage; designs without coverage are excluded by the rule's own eligibility) ✓; history lowering 10/5 points on net remake charges ✓; card reduction 10/5 on 12-month Northgate qualifying spend ✓; surcharge 25/10 ✓; fitting fee 0/7.50/15 ✓; order ✓.
- P4: net frame ✓; restock method pct (frame ≥150) / flat 12 (75–150) / 0 ✓; pct 5/10/15 by days from order date ✓; shipping 6/3/0 (material ∧ option / exactly one) ✓ — compute counts AR as an "option", consistent with P5's enumeration (observation O9); courtesy 5/2.50/0 ✓; order ✓.
- P5: **gap (finding G2)**. Rule: "each light-adaptive, blue-light filtering or anti-reflective option charge on it is refunded on its own". Compute has a single `op_option_net = op_pc_net if op_pc_net > 0 else (op_bl_net if op_bl_net > 0 else op_ar_net)` and `op_refundable` keyed on the photochromic count, so on a job carrying two options it only ever evaluates the light-adaptive one (and because that refund is pro-rata, `op_pc_net` stays > 0 after it is posted). Single-option jobs ✓: window 21/18/14 ✓, pro-rata on days from the light-adaptive charge date capped at the window ✓, blue-light − 12 floored ✓, card courtesy 10/5 % of net option charge ✓, fee 0/3/6 ✓, order ✓.
- P6: refundable method poly/Trivex (net − design's polycarbonate upgrade price, floored) / high index (half) / full ✓; share 100/80/60 ✓; spend bonus 5/2.50 on 12-month net order lines ✓; treated-blank 5/2.50/0 ✓; order ✓.
- P7: pool = base + material + option nets ✓; lab-day start latest post-order charge / rx issue date if after order / order date ✓; pct 35/45 (with material) else design's in-lab retained pct ✓; loyalty 5/2 points with active linked card ✓; fresh-exam 3/1 ✓; fee 10/7.50/5 on base-lens charge ✓; order ✓.

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one policy (7 distinct tools, 7 distinct `computes`).
- Every tool body only writes (`ctx.create` / `ctx.update`) with the values passed in; none reads the ledger, checks a status, validates an amount or returns a hint. No tool judges a prerequisite.
- Share tools (`blueprint/share_tools.py`) contain finders plus `verify_customer_identity` and `transfer_to_human_agent` only; no share write sets an eyewear job's status or posts an optical credit, so each waited-on state has exactly one producing write in this difficulty.
- Docstrings name no other tool and no position in a sequence by an ordering word ("first" occurs only as the ordinal "1 for the first remake"). Observation O2: `refund_lens_option_d067b0d2` and `refund_lens_material_ad7f47c2` say "of an eyewear job that is being cancelled" and `post_lens_cancellation_refund_d976b5a7` says "Refund the base-lens charge of a cancelled eyewear job" — the docstring restates the P7 state gate on a non-policy surface.
- **Finding G4 (tool module):** every amount argument's docstring carries a concrete example ("pass a number such as 57.50 / 21.29 / 55.81 / 147.50 / 50.52 / 9.50 / 81.95"). Whether these coincide with the values the policy entails on the task worlds is a per-task fact, demonstrated in `0.md` and `1.md`.
- uuid8s: 2fd39c69, 01693abf, 0a7f54ae, a25e55a5, d067b0d2, ad7f47c2, d976b5a7 — seven distinct values, no shared prefix or suffix, no sequential/adjacent pattern, none appearing in the blueprint. (Other difficulties' tool modules are outside the read domain and were not compared.)

### prerequisite_graph

- `prerequisite` present on all 7 policies (`[]` on P1, P2, P4, P5, P6).
- Edges: P3→P1, P3→P2, P7→P4, P7→P5, P7→P6. Every `problem` is an extended policy id of this file; none points at a base policy or at itself. Graph acyclic (the blockers P3, P7 are depended on by nothing).
- Every `policy_source` is verbatim in the blocked policy's own `rule` (script check) and is not restated in the depended-on policy's rule.
- All five edges `form: state`, no `fallback_reason` (correct: fallback only on action form).
- `resolved_by` = the depended-on policy's `target_tool` on all five edges; each tool's effect makes the `condition` hold (P1/P2/P5/P6 tools add the credit the condition names; P4's tool sets `status=cancelled`, `closed_date=today`).
- `kind`/`gate`: P3/P1 `value_input` → `rd_lens_net` (exists, reads base-lens credits); P3/P2 `value_input` → `rd_paid_remakes` (exists, reads `remake_charge_waived` credits); P7/P4 `state_gate` → `optical_holdings.status` (a real eligibility state); P7/P5 and P7/P6 `value_input` → `rt_pool` (exists, reads option and material credits).
- `condition` texts are general (no "in this task / at the opening") and match the sentences' strength: P7/P5 "every ... option charge" ↔ "each ... option charge" ✓; P3/P2 "every prescription-change remake charge ... no higher than the late ... charge" ↔ "each ... stands no higher than" ✓.
- Tree shapes: {P3; P1, P2}: n = 2, 2 `value_input` ≥ max(1,1) ✓, one owner=user write (P3's own tool). {P7; P4, P5, P6}: n = 3, 2 `value_input` ≥ max(2,1) ✓, one owner=user write (P4).

### prerequisite_sentences

| edge | sentence (verbatim) | connective | waited-on state (record-visible) | single producing write | derivation |
| --- | --- | --- | --- | --- | --- |
| P3→P1 | "The accidental replacement charge is fixed only after the original base-lens charge carries the switch-down credit owed for any lower-priced lens design the job has been remade in." | only after | a refund credit against the original base-lens charge (`optical_transactions` credit with `source_txn_id` = that charge) | P1 is the only policy whose rule posts a credit on the base-lens charge of a remade job ("is posted as one refund credit against that original base-lens charge") | reader sees base-lens charge 199.99-type vs current design price; P1's rule defines "switch-down credit" and its amount → post it, then price P3 |
| P3→P2 | "The accidental replacement charge is not fixed until each prescription-change remake charge on the job, less any waiver posted against it, stands no higher than the late prescription-change remake charge it is owed at." | not ... until | net of waiver credits on each prescription-change remake charge ≤ late charge | P2 is the only policy whose rule posts a waiver on a prescription-change remake charge | reader compares booked charge with P2's "late prescription-change remake charge" → P2's waiver closes the gap |
| P7→P4 | "The lens cancellation refund is not posted until the eyewear job stands cancelled on its record." | not ... until | `optical_holdings.status = cancelled` | only P4's tool sets status cancelled (no share write does) | P4's rule: "When a member confirms the cancellation ... the member's confirmation books one refund credit against the frame charge" → hand the confirmation to the member |
| P7→P5 | "The lab retention is worked out only after each light-adaptive, blue-light filtering or anti-reflective option charge on the job carries its option cancellation refund." | only after | a cancellation refund credit on each option charge | only P5 credits option charges | P5's rule gives the option refund |
| P7→P6 | "The lab retention is not worked out before the material upgrade charge of the job carries its material cancellation refund." | not ... before | a cancellation refund credit on the material charge | only P6 credits the material charge | P6's rule gives the material refund |

Four-point test: each sentence joins the blocked policy's own result to its waited-on state with an ordering connective; each names a state in business/record words with no performer and no tool; none names a tool, policy id, snake_case token or row id; each is at the strength of its `condition`. Each blocked rule carries no second wording of the dependency.

Undeclared cross-problem order (observation O3): P5's rule opens "When an eyewear job in the lab is cancelled, each ... option charge on it is refunded on its own" and P6's "When an eyewear job in the lab is cancelled, its lens material upgrade charge is refunded" — a timing connective relating the option/material refund to the cancellation (P4's write), grounding no declared edge. Both orders (P4 before or after P5/P6) produce the same terminal state, because P5's and P6's computes read neither the job status nor the frame credit (demonstrated on task 1's world in `1.md`); no demonstrable consequence, so observation only. No base rule sentence grounds an edge.

### override_declarations

Sentence-by-sentence over each `base_policy_refs` entry (quantity actually scored):

- P1 (refs: discount_stacking, vision_plan_billing, remake_guarantees, cancellation, satisfaction_returns). remake_guarantees "when the new design's base_lens_price_usd is lower the difference on the base_lenses charge is credited as a return_refund" — handled differently (half / whole / pro-rata, uplift, bonus, refit fee) → declared in `overwrite[0]` ✓. "when it is higher the member pays the difference as the remake charge" — not touched. Credits "never exceed that charge's optical_msr_charge_net" (cancellation) — followed via the net-of-credits gap. Other refs' sentences (one discount route, plan allowances, satisfaction window) — followed / not touched.
- P2. remake_guarantees "A prescription_change remake is free only when ... within rx_change_remake_window_days calendar days of the dispensed date ..." — handled differently (window start may move to the latest non-adapt remake or to the prescription issue date) → declared `overwrite[1]` ✓ (the `replaced_by` quotes only the non-adapt anchor sentence; the issue-date anchor departs from the same named base sentence — observation O8). "Any other remake, or one past its window or count, costs remake_charge_pct_outside_coverage of the job's base_lenses price." — handled differently for prescription-change remakes → declared `overwrite[0]` ✓. The merged semantics are unique except where G1 applies (rule 40 vs compute P = 50).
- P3. remake_guarantees "An accidental_damage remake is available only within accidental_damage_coverage_months, at most accidental_damage_replacements_allowed times, for accidental_damage_charge_pct of the job's frame and base_lenses charges." — eligibility half followed verbatim in P3's rule; amount half handled differently → declared ✓. discount_stacking/job_pricing: followed. reward_flag "remake charges never earn" — followed (tool writes `reward_eligible=False`).
- P4. cancellation "the frame, which returns to stock, and the rest of the lens charges are credited" — frame part handled differently (restocking/shipping kept) → declared ✓.
- P5, P6. cancellation "and the rest of the lens charges are credited" — option/material parts handled differently → declared (same clause, each for its own charges) ✓.
- P7. cancellation "A job cancelled while in the lab keeps in_lab_cancellation_retained_pct of optical_msr_original_lens_charges" — handled differently (pool net of option/material refunds, lowered percentage, fee, retained out of the base-lens credit) → declared ✓.
- Across P4–P7 the whole in-lab cancellation sentence of base is covered by declared overrides; "A job not yet submitted to the lab is cancelled with every charge credited in full", "Every refund credit is posted against the exact charge it returns and never exceeds that charge's optical_msr_charge_net", "Ready or dispensed eyewear is not cancelled" are inherited and not weakened.
- Disguised forms searched: no anonymous intermediate (every deviation is under a named binding quoted from the rule), no 0/1 multiplier zeroing a base quantity, no dropped branch. No author language calling base's output wrong.
- Observation O4: base `lifecycle.transitions` marks `in_lab → cancelled` and `dispensed → remake_in_lab` as `by: agent`, while P4's and P3's tools are `owner=user`; lifecycle is not a policy sentence, so recorded as observation.

### factor_ladders

| policy | factor | label | decides | tiers (fall-through last) | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | switch_gap_credit_method | method | sw_gap_credited | whole gap / pro-rata unused window / half | yes (remake-number on charge row ∧ days from holding date) | – |
| P1 | switch_courtesy_uplift | parameter | sw_courtesy_pct | 10 / 5 / 0 | no | membership |
| P1 | switch_spend_bonus | parameter | sw_spend_bonus | 5.00 / 2.50 / 0 | no | order |
| P1 | switch_refit_fee | parameter | sw_refit_fee | 0 / 7.50 / 15.00 | no | – |
| P2 | rx_window_start_anchor | method | rx_window_start | latest prior non-adapt date / rx issue date / dispensed date | yes (tier 2: no prior non-adapt ∧ rx age > 12) | – |
| P2 | rx_late_share_ladder | parameter | rx_late_share | 0 (not past) / 20 / 30 / 40 (rule) vs P (compute) | no | – |
| P2 | rx_material_rebill_share | parameter | rx_material_rebill | whole net / half net / 0 | yes (holding material ∧ charge row) | – |
| P2 | rx_loyalty_reduction | parameter | rx_loyal_pct | 15 / 10 / 0 | yes (membership ∧ card) | membership, card |
| P2 | rx_fresh_prescription_reduction | parameter | rx_fresh_pct | 10 / 5 / 0 | no | – |
| P2 | rx_lab_handling_fee | parameter | rx_handling_fee | 0 / 4.95 / 9.95 | no | – |
| P3 | replacement_clock_anchor | method | rd_clock_start | latest rx-change date / latest non-adapt date / dispensed | yes (tier 2: no rx-change ∧ a non-adapt) | – |
| P3 | replacement_percentage_ladder | parameter | rd_pct | 20 / 25 / 30 | no | – |
| P3 | replacement_remake_history_lowering | parameter | rd_history_points | 10 / 5 / 0 points | no | – |
| P3 | replacement_card_spend_reduction | parameter | rd_card_pct | 10 / 5 / 0 | no | card |
| P3 | replacement_material_surcharge | parameter | rd_material_surcharge | 25 / 10 / 0 | yes (holding material ∧ charge row) | – |
| P3 | replacement_fitting_fee | parameter | rd_fitting_fee | 0 / 7.50 / 15.00 | no | – |
| P4 | frame_restocking_method | method | fr_restock | % of net frame / flat 12 / none | no | – |
| P4 | frame_restocking_percentage | parameter | fr_restock_pct | 5 / 10 / 15 | no | – |
| P4 | frame_lab_shipping_handling | parameter | fr_ship | 6 / 3 / 0 | yes (material charge ∧/∨ option charge) | – |
| P4 | frame_courtesy | parameter | fr_courtesy | 5 / 2.50 / 0 | no | membership |
| P5 | option_refund_method | method | op_refundable | pro-rata window / net − 12 / net in full | no | – |
| P5 | option_window_length | parameter | op_window | 21 / 18 / 14 | yes (holding material ∧ charge row) | – |
| P5 | option_card_courtesy | parameter | op_card_pct | 10 / 5 / 0 | no | card |
| P5 | option_handling_fee | parameter | op_fee | 0 / 3 / 6 | no | – |
| P6 | material_refundable_method | method | mt_refundable | net − design poly price / half / full | no (rule tiers on material only) | – |
| P6 | material_refund_share | parameter | mt_share | 100 / 80 / 60 | no | – |
| P6 | material_spend_bonus | parameter | mt_spend_bonus | 5 / 2.50 / 0 | no | order |
| P6 | material_treated_blank_deduction | parameter | mt_treated | 5 / 2.50 / 0 | yes (tier 2: no light-adaptive ∧ blue-light) | – |
| P7 | lab_day_start_anchor | method | rt_lab_start | latest post-order charge / rx issue date / order date | yes (tier 2: no later charge ∧ rx after order) | – |
| P7 | lab_retention_percentage | parameter | rt_pct | 35 / 45 / design in-lab pct | yes (lab days ∧ material charge) | – |
| P7 | retention_loyalty_lowering | parameter | rt_loyal_points | 5 / 2 / 0 | yes (membership ∧ card) | membership, card |
| P7 | fresh_exam_lowering | parameter | rt_fresh_points | 3 / 1 / 0 | no | – |
| P7 | lab_cancellation_fee | parameter | rt_fee | 10 / 7.50 / 5 | no | – |

Counts: P1 4 (1 method, 3 parameter); P2 6 (1, 5); P3 6 (1, 5); P4 4 (1, 3); P5 4 (1, 3); P6 4 (1, 3); P7 5 (1, 4) — all within 4–6 with ≥2 parameter and ≥1 method. Each factor's `bindings` are disjoint from every other factor's in the same policy; every `decides` is an input binding, never `result`. Every ladder has ≥3 pairwise-disjoint tiers as stated, every tier is a sentence of the `rule` and a branch of the `decides` binding (the only face mismatch is G1's fall-through value). No two tiers of one ladder select the same value or method (G1 aside, P2's 40 vs the "not past" 0 and 20/30 are distinct). Every fall-through equals the factor's `baseline` binding. Per tree: {P1,P2,P3} has multi-source factors (P1 gap method, P2 loyalty, P3 surcharge…) and cross-difficulty membership/card/order; {P4..P7} has multi-source factors (P4 shipping, P7 retention pct, P7 loyalty…) and cross-difficulty membership/card/order.

Labels: each `method` ladder has at least one tier that changes the algorithm (pro-rata in P1 and P5, a different anchor date in P2/P3/P7, percentage-vs-flat in P4, subtraction-vs-halving in P6). Observation O5: within those ladders some tier pairs differ only by a number (P1 whole vs half; P5 "net − 12" vs "net in full").

Realism: the conditions are ones an eyewear retailer plausibly weighs (tenure, co-brand card, spend, days in lab, special-order material, remake history, option type). Observation O6 (borderline): P7 `fresh_exam_lowering` — how recent the prescription was when the job was ordered lowers the in-lab cancellation retention, which compensates lab work already started; prescription freshness has no evident bearing on that cost. P2's fresh-prescription reduction on a late prescription-change remake is more defensible (a quick change after a fresh exam). Recorded as observation, not as a red light, because no re-checkable consequence beyond the auditor's industry judgement is available and P7 keeps 4 qualifying factors without it.

### findings

- **G1 — SOURCE-POLICY RED (charter-global; P2 rule ↔ compute fall-through).** Symptom: P2's rule states "A prescription-change remake past its window costs 40 percent of the base lens price of the lens design the job carries, plus a lab handling fee of 9.95, rounded to the cent." and its `baseline.rule` repeats it; compute `rx_late_share` falls through to `P('remake_charge_pct_outside_coverage')` and the factor baseline is `0 if rx_days_past <= 0 else P('remake_charge_pct_outside_coverage')`. Root cause: a fixed number in the rule vs a per-design parameter in compute. Evidence: optical.extended.yaml P2 `rule`, `compute.rx_late_share`, `factors[rx_late_share_ladder].baseline`; base variants give `remake_charge_pct_outside_coverage` 50 for Single Vision, Lined Bifocal, Lined Trifocal, Standard Progressive. Demonstrated consequence: a Standard Progressive job (base price 99.99) whose prescription-change remake is >90 days past its window with no material, no reductions and no other remake — rule: 0.40 × 99.99 + 9.95 = 49.95; compute: 0.50 × 99.99 + 9.95 = 59.945 → 59.94 (as the evaluator rounds). Bears on task 0 (claims P2): on task 0's Premium Progressive job both faces give 40, so no scored-value consequence there (see `0.md`).
- **G2 — SOURCE-POLICY RED (charter-global; P5 rule ↔ compute, and P7's prerequisite).** Symptom: P5's rule refunds "each light-adaptive, blue-light filtering or anti-reflective option charge ... on its own"; P7's prerequisite waits on "each ... option charge on the job carries its option cancellation refund"; P5's compute evaluates one option only (`op_option_net` precedence photochromic > blue-light > AR, `op_refundable` keyed on photochromic existing). Demonstrated consequence: an in-lab Standard Progressive job with an AR charge 35.00 and a light-adaptive charge 80.00 — the rule requires a second credit on the AR charge (35.00 net in full, ± courtesy and fee); no evaluation of the compute can yield it, because after the pro-rata light-adaptive refund `op_pc_net` is still > 0 and the compute returns the light-adaptive figure again. Bears on task 1 (claims P5): task 1's job has one option only (Premium includes AR), so no scored-value consequence there (see `1.md`).
- **G3 — SOURCE-POLICY RED (charter-global; P2 window-start filter).** Symptom: rule "Where an earlier non-adapt remake was opened on the job before the prescription-change remake, the window start is the opening date of the latest such non-adapt remake"; compute `rx_na_date = LATEST(... remake_reason='non_adapt')` over all non-adapt remakes, then `rx_na_date < rx_remake_date`. Demonstrated consequence: a Premium Progressive job (rx-change window 90 days) with non-adapt remake #1 on day 20, prescription-change remake #2 on day 130, non-adapt remake #3 on day 140, prescription 2 months old — rule: window start = day 20 → days past = 110 − 90 = 20 → late share 20 %; compute: `rx_na_date` = day 140 ≥ day 130 → condition false → window start = dispensed date → days past = 130 − 90 = 40 → late share 30 %. Bears on task 0: one non-adapt remake only, no consequence there.
- **G4 — tool docstring example amounts (tool module).** Finding stated here; whether the examples equal the values the policy entails on each world, and the resulting class, is demonstrated in `0.md` and `1.md`.
- Observations O2–O9 as listed in the sections above (docstrings restating the P7 gate; P5/P6 "When ... is cancelled" timing with order-independent terminal state; lifecycle `by: agent` vs user tools; method-label tier pairs differing only by a number; P7 fresh-exam realism; P1 zero-length window division; P2 overwrite[1] replaced_by quoting one of two anchor departures; AR counted as an "option" in P4/P5 while base pricing distinguishes "coatings and options").

## closing_checklist

Written after both tasks' frozen derivations (mtimes ≤ 21:37:58Z) and reveals (21:38:02Z, 21:39:35Z). The charter-global sections above were written before any reveal and were not changed by it.

Status: **NOT CLOSED** — the four relationships do not all PASS (Step 4 requires them to). Per-task verdicts:

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 (`0.md`) | SOURCE-POLICY RED (G1, G3 in P2; no consequence on its world) | SOURCE-CHAIN RED (T0-6, false proof assertion; tree itself holds) | SOURCE-FACTOR RED (T0-4 docstring examples) | SOURCE-TASK RED (T0-4) |
| 1 (`1.md`) | SOURCE-POLICY RED (G2 in P5/P7; no consequence on its world) | SOURCE-CHAIN RED (T1-1 customer names the cancellation prerequisite; T1-5, T1-6 false proof assertions) | SOURCE-FACTOR RED (T1-3) | SOURCE-TASK RED (T1-3) |

Checklist items, as far as they can be ticked:
- Audit files one-to-one with tasks (`0.md`, `1.md`) with `_difficulty.md` alongside: yes; no older revisions exist (first audit).
- Coverage and scope: GT `charter_scope` — task 0 {switch credit, late rx waiver, accidental replacement}, task 1 {frame return, option, material, lens cancellation refunds}; pairwise disjoint, jointly all 7 extended policies and all 7 task tools; each scope is exactly one connected component of the prerequisite graph (root plus all its prerequisites). Yes.
- uuid8s independently generated and frozen: no defect found (`#action_binding_and_uuids`).
- Trees: task 0 n = 2 (2 value_input), task 1 n = 3 (2 value_input); each has an owner=user write; whole-difficulty graph acyclic. Yes (structure); task 1's state-gate hop is conveyed by the customer (T1-1).
- Factors: every computation 4–6 factors with ≥2 parameter, ≥1 method; per task ≥1 multi-source and ≥1 cross-difficulty with seeded rows; every factor bears weight against an honest baseline on its world and every whole-baseline number is definite and ≠ gold — yes on the policy surface; voided against an agent that reads the tool docstrings (G4 → T0-4, T1-3).
- Instantiation gates re-run on the final form: not performed by this audit (the difficulty is not at closing; the brief's snapshot stands, with TRACEABILITY still NOT OK pending the KB render).

## revision_2

### charter_global_frozen (revision 2)

- Re-audit round 2 requested by the coordinator after rework. Inputs re-hashed by the auditor (equal to the brief): `optical.extended.yaml` 1cfbd05c7bf34f6f1497ed703ba1939c461fbbbee5ae1b19836590e18d6b29fe (round 1: 94a1609d…), `task_tools.py` 774aca6e7a24af53a80297e2979ee7342fa37e934d6115162060edb2eafcfee1 (round 1: 8a14b96e…), views `0.view.json` 4c6f4286…, `1.view.json` f8c49762…. Both shared inputs changed → every charter-global section re-derived in full (not carried forward).
- Freeze start 2026-10-05T22:31:31Z; this revision_2 charter-global block was written before either round-2 task file was opened. Text of round 1 above is untouched.
- Gate snapshot supplied (all OK; traceability deferred, KB not rendered). Masked/unread at writing: `tasks/{0,1}.json` (round 2), `worklog.md` (never opened).
- contamination_disclosure: this auditor read the round-1 GT of both tasks in round 1. Nothing from round-2 GT was read before this block. Charter-global checks do not depend on GT.

### policy_conflict_scan (r2)

Base section still byte-identical to `products/optical.yaml` (lines 1–881). Extended policies (7):

| id | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- |
| P1 switch_difference_credit | post_switch_difference_credit_2fd39c69 (agent) | switch_credit_usd | [] |
| P2 late_rx_remake_waiver | waive_remake_overcharge_01693abf (agent) | waived_amount_usd | [] |
| P3 accidental_replacement_charge | authorize_damage_replacement_0a7f54ae (user) | replacement_charge_usd | P1 value_input rd_lens_net; P2 value_input rd_paid_remakes |
| P4 frame_return_refund | **refund_frame_to_stock_fae456d1 (agent)** — new | frame_refund_usd | [] |
| P5 option_cancellation_refund | refund_lens_option_d067b0d2 (agent) | option_refund_usd | [] |
| P6 material_cancellation_refund | refund_lens_material_ad7f47c2 (agent) | material_refund_usd | [] |
| P7 lens_cancellation_refund | **confirm_eyewear_cancellation_51323feb (user)** — new; cancels the job and books the base-lens refund | lens_refund_usd | P4 **state_gate** gate `optical_transactions.source_txn_id`; P5 value_input rt_pool; P6 value_input rt_pool |

Retired tools: `confirm_eyewear_cancellation_a25e55a5`, `post_lens_cancellation_refund_d976b5a7`. Overlap scan: no two policies write the same (charge, credit_reason) in the same state (P1 and P7 both credit a base-lens charge but in disjoint lifecycle states — remade/dispensed vs in-lab cancellation); only P7's tool sets `cancelled`; only P4's credits the frame. Cross-category reads unchanged in kind (P7 now also reads card statements). Components: {P1,P2,P3} and {P4,P5,P6,P7} — two trees, mutually exclusive, jointly complete.

### rule_compute_equivalence (r2)

Mechanical: every `compute_basis` quotation verbatim in its rule; compute_basis keys = compute keys; every `baseline.rule` sentence in the rule; every overwrite `superseded_clause` verbatim in base and every `replaced_by` sentence in the rule — all 7 policies.

Semantic re-sweep, changes since round 1:
- P1: pro-rata tier now "the window being at least one day long" and compute guards `P('non_adapt_window_days') > 0` → round-1 O7 (division by zero) **closed**. Rest unchanged ✓.
- P2: fall-through now "the outside-coverage remake percentage of the lens design the job carries, applied to that design's base lens price" in rule, `baseline.rule`, overwrite and ladder; compute `P('remake_charge_pct_outside_coverage')` → **G1 closed** (Standard Progressive example: both faces 50 % → 59.94). Window-start tier 1 now "Where the latest non-adapt remake on the job was opened before the prescription-change remake, the window start is the opening date of that latest non-adapt remake", tier 2 "the job carries no non-adapt remake, or its latest non-adapt remake was not opened before ..." — exactly compute's `rx_na_date` (latest overall) `< rx_remake_date` → **G3 closed** (round-1 example: rule and compute now both fall to the dispensed date). Overwrite[1] `replaced_by` now quotes both anchor sentences → **O8 closed**. Observation kept: `rx_booked` sums all prescription-change remake charges while the date is the latest one's.
- P3: unchanged ✓.
- P4: rule now "In an in-lab cancellation the frame goes back to stock, and its frame return refund is booked as one refund credit against the frame charge"; "a lens option charge (a light-adaptive, blue-light filtering or anti-reflective coating charge)" defines the option set compute counts → **O9 closed**. Ladders unchanged ✓.
- P5: rule now settles options "one at a time in a fixed order: the option being refunded is the first of the light-adaptive, the blue-light filtering and the anti-reflective option charge that carries no cancellation refund yet"; compute `op_pc_open` / `op_bl_open` test for an existing `cancellation_refund` credit on that component. Demonstrated on round 1's hypothetical (task 1's job plus an AR charge 35.00): first evaluation → light-adaptive (50.52); after that credit → AR, refundable 35.00, result 33.75 = rule's "net in full + 5 % courtesy − 3.00 fee". **G2 closed.** Edge observation: once every option carries a refund the rule names no option, while compute falls to `op_ar_net` (0 here) — no write is owed, consistent.
- P6: wording "In an in-lab cancellation" (was "When ... is cancelled") ✓; ladders unchanged.
- P7: rule restructured — the member's confirmation records the cancellation and books the lens refund; `fresh_exam_lowering` removed and replaced by `retention_card_spend_lowering` ("Northgate qualifying spend ... in statement entries dated less than twelve whole months before the day the cancellation is confirmed": ≥1,500 → 3 points, ≥500 → 1 point), compute `rt_spend_points` from `XSUM('card','card_transactions','qualifying_spend', within_months=12, ..., spend_category='northgate_purchases')` ✓ → **O6 closed**. All other bindings ✓.

### action_binding_and_uuids (r2)

- 7 policies, 7 distinct `(target_tool, computes)`. Bodies only create/update with passed values; none reads the ledger, checks status or returns a hint.
- uuid8s: 2fd39c69, 01693abf, 0a7f54ae, d067b0d2, ad7f47c2, fae456d1 (new), 51323feb (new) — distinct, no shared prefix/suffix or sequence; the retired a25e55a5/d976b5a7 are not reused.
- Docstrings: no amount example remains (grep for `\d+\.\d\d` over `task_tools.py`: no hit) → **G4 closed**. "being cancelled" / "of a cancelled eyewear job" phrasing gone (option/material tools now say "as a cancellation refund") → **O2 closed**. The only "cancelled" words are in the new user tool's own effect description. No ordering words, no other tool named.
- Share tools unchanged: no share write cancels a job or credits an optical charge.

### prerequisite_graph (r2)

Edges P3→P1, P3→P2, P7→P4, P7→P5, P7→P6; all ids in this file; acyclic; all `form: state`, no fallback; every `policy_source` verbatim in the blocked rule and not in the depended-on rule; `resolved_by` = depended-on target tool on all five. P7→P4 now `state_gate` with gate `optical_transactions.source_txn_id` (a credit on the frame charge) and condition "The job's frame charge carries a cancellation refund credit for its frame return refund" — produced only by `refund_frame_to_stock_fae456d1`. Trees: {P3; P1,P2} n = 2, 2 value_input, user write P3; {P7; P4,P5,P6} n = 3, 2 value_input, user write P7 (the root itself).

### prerequisite_sentences (r2)

| edge | sentence | connective | producing write |
| --- | --- | --- | --- |
| P3→P1 | (unchanged) "The accidental replacement charge is fixed only after the original base-lens charge carries the switch-down credit owed for any lower-priced lens design the job has been remade in." | only after | P1 only |
| P3→P2 | (unchanged) "... not fixed until each prescription-change remake charge ... stands no higher than the late prescription-change remake charge it is owed at." | not … until | P2 only |
| P7→P4 | "The cancellation of an in-lab job is not confirmed until its frame charge carries the frame return refund." | not … until | P4 only |
| P7→P5 | (unchanged) "The lab retention is worked out only after each ... option charge on the job carries its option cancellation refund." | only after | P5 only |
| P7→P6 | (unchanged) "The lab retention is not worked out before the material upgrade charge of the job carries its material cancellation refund." | not … before | P6 only |

Four-point test passes on all five (state named in record words; no tool/id/snake_case; strength = condition). Derivation for the new edge: the root's own result (the member's confirmation) waits on a frame credit → P4's rule is the only one booking a frame credit ("its frame return refund is booked as one refund credit against the frame charge") → post it, then hand over the confirmation. Undeclared orders: P4/P5/P6 now open "In an in-lab cancellation, ..." (a scope phrase, no ordering connective) → **O3 closed**. No base sentence grounds an edge.

### override_declarations (r2)

Same sentence-by-sentence result as round 1 for P1, P3, P5, P6; P2's two overwrites now name the base sentences and quote every replacing sentence (outside-coverage percentage of the design; both window anchors); P4 replaces "the frame, which returns to stock, and the rest of the lens charges are credited" (frame part); P7 replaces "A job cancelled while in the lab keeps in_lab_cancellation_retained_pct of optical_msr_original_lens_charges". No undeclared override, no disguised form. O4 (lifecycle `by: agent` for `in_lab → cancelled` while the cancelling tool is now `owner=user`) remains an observation.

### factor_ladders (r2)

Unchanged from round 1 for P1–P6 (counts P1 4 = 1m+3p, P2 6 = 1m+5p, P3 6 = 1m+5p, P4 4, P5 4, P6 4 = 1m+3p each). P5 `option_refund_method` now binds `op_pc_refunds, op_pc_open, op_refundable` with tiers keyed on "the option being refunded" ✓. P7: 5 factors — lab_day_start_anchor (method), lab_retention_percentage (multi-source: lab days ∧ material), retention_loyalty_lowering (multi-source membership ∧ card; cross-difficulty), **retention_card_spend_lowering** (3 / 1 / 0 points; cross-difficulty card), lab_cancellation_fee — 1 method, 4 parameter. Bindings disjoint in every policy; every tier stated in the rule and branched in compute; no two tiers share an outcome; every fall-through equals the factor baseline. Realism: the card-spend lowering is a loyalty concession of the same kind as P3's/P5's card tiers; O6's doubt (prescription freshness lowering a lab retention) no longer applies. O5 (method ladders where one tier pair differs only by a number) remains an observation.

### findings (r2, charter-global)

- G1, G2, G3, G4 — **closed** (evidence above).
- O2, O3, O6, O7, O8, O9 — **closed**.
- O4, O5, summed prescription-change remake charges — remain observations (as the reworker stated).
- **O10 (new, observation).** The in-lab cancellation tree now books the frame, option and material refunds on a job whose status is still `in_lab`, before the member's confirmation records the cancellation (P7's own sentence "The cancellation of an in-lab job is not confirmed until its frame charge carries the frame return refund"). The charter says nothing about the refunds if the member then does not confirm. No relationship is broken on the task worlds (the persona confirms), and the order is stated by a declared edge; recorded as an observation on business realism.
- No new SOURCE-POLICY defect found.

### closing_checklist (revision 2)

Written after both round-2 frozen derivations (22:35:03Z) and reveals (22:35:10Z).

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 (`0.md#revision_2`) | PASS | PASS | PASS | PASS |
| 1 (`1.md#revision_2`) | PASS | PASS | PASS | PASS |

- Audit files one-to-one with tasks, `_difficulty.md` alongside; round 1 kept verbatim above each `## revision_2`; every round-2 comparison carries PASS.
- Coverage/scope: GT `charter_scope` — task 0 {P1, P2, P3}, task 1 {P4, P5, P6, P7}; pairwise disjoint, jointly all 7 extended policies and all 7 task tools; each scope is one whole prerequisite tree.
- uuid8s independent and frozen (two new: fae456d1, 51323feb; retired ones not reused).
- Trees: task 0 n = 2 (2 value_input, user write P3); task 1 n = 3 (2 value_input, user write P7); whole graph acyclic.
- Factors: every computation 4–6 factors (≥2 parameter, ≥1 method); per task ≥1 multi-source and ≥1 cross-difficulty factor with seeded rows; every factor bears weight against an honest baseline; every all-baseline number definite and ≠ gold; a genuine near-miss in every computation.
- Round-1 REDs: G1, G2, G3, G4, T0-4/T0-6, T1-1, T1-3, T1-5, T1-6 — all closed; round-1 observations O2, O3, O6, O7, O8, O9, T0-3, T0-5, T0-7, T1-4 closed; O4, O5 and the summed prescription-change remake charge remain observations; one new observation O10. No regression found.
- Instantiation gates on the final form: coordinator's post-rework snapshot (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK) taken on the same hashes this revision audited; TRACEABILITY deferred until the KB is rendered (step 3). Not re-run by the auditor.
- Contamination: this auditor saw round-1 GT; round-2 derivations are disclosed as non-blind in each task file, with every step shown and recomputed.

**Difficulty status: source-layer audit PASS (revision 2)**, subject to the deferred traceability gate.

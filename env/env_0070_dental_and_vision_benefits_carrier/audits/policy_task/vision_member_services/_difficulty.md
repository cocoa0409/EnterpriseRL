# Policy-task audit — vision_member_services / charter-global

## revision_1

## charter_global_frozen
- Frozen 2026-10-18T03:26 (before any task GT was revealed). Auditor: independent policy-task auditor (erl-task-policy-audit), round 1.
- Inputs hashed: `vision.extended.yaml` sha256=aa72f8507cf08847bf39289c9db103ac31ad0883309b8c9693dd50aaf3e8c6c6; `task_tools.py` sha256=ff75e2a2dc391f69059866dce1fe22e1ec4f8d4819f732986446be29b0eeb42b (both re-hashed by the auditor, equal to the brief).
- Read: blueprint.yaml, db_schema.json, share_tools.py (function list), products/vision.yaml (full), products/savings.yaml / dental.yaml / billing.yaml (parameters and rules needed for cross-category reads), the extended charter, task_tools.py, `audits/render_source/XF_recipe.md`, the coordinator notes, the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (semantics of LATEST/COUNT/CFIELD/MONTHS/RND).
- Masked and unread at freeze: raw `tasks/*.json`, the difficulty worklog, every `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, db_closure fields. Nothing in this section derives from GT.
- Gate snapshot (brief, 2026-10-18T02:55:34): check_extended / check_task_tools / replay_tasks / check_solvability / check_compute / check_grounding / check_cross_fire all rc=0. Masked views supplied with hashes (task_0 f8876b2b…, task_1 afd45d33…), verified equal. Entry conditions complete.
- Probes: scratch evaluator `/tmp/audit_vision_member_services_0070/ev.py` + `probe.py` run the charter's own compute (check_compute.build_env) on copies of the masked worlds; probe outputs quoted below as P1–P5b.

### policy_conflict_scan
Six extended policies, one per write tool:

| policy | target_tool (owner) | computes | subject | prerequisites |
| --- | --- | --- | --- | --- |
| vision_ext_frame_member_share | decide_frame_order_646cd942 (agent) | member_paid | vision_frame_claim | lens (value_input `lens_with_copay`), exam (value_input `ex_same`) |
| vision_ext_lens_member_share | decide_lens_order_308134ce (agent) | member_paid | vision_lens_claim (participating) | OON lens (value_input `pl_date`), exam (value_input `vx_same`) |
| vision_ext_exam_plan_payment | decide_exam_service_5f5caac3 (agent) | plan_paid | vision_exam_claim routine exam (participating) | [] |
| vision_ext_oon_lens_reimbursement | file_oon_lens_claim_87fedf94 (user) | plan_paid | vision_lens_claim (out of network) | [] |
| vision_ext_oon_contacts_reimbursement | file_oon_contacts_claim_522b92fb (user) | plan_paid | vision_contacts_claim (out of network) | [] |
| vision_ext_fitting_member_share | decide_contact_fitting_9468302b (agent) | member_paid | vision_exam_claim fittings | OON contacts (value_input `tl_date`) |

- Base copy: lines 1–969 of the extended file are byte-identical to `blueprint/products/vision.yaml` (diff empty).
- Scope: lens rule and OON-lens rule split vision_lens_claim by channel; exam rule and fitting rule split vision_exam_claim by exam_type. No two policies claim the same `(target_tool, computes)`. Claimed event types vision_claim_reversal, vision_tier_change, vision_terminate_voluntary, vision_free_look_cancel, vision_reinstate are not touched by any extended policy (stay under base). M-task coverage of the six policies is checked after reveal (closing_checklist).
- Trigger rule (XF-14): every task tool only updates a `vision_claims` row; the events those rows carry (vision_exam_claim, vision_lens_claim, vision_frame_claim, vision_contacts_claim) all have `triggers: []` in base. No write books rows in another category. PASS.
- Conflicts found across policies: C1–C4 below (contacts-in-lieu dropped, not-covered branch dropped, undeclared month counting + sibling overwrites, reversal-by-claim-number).

### rule_compute_equivalence
- Mechanical sweep (scratch, whitespace-normalised): every `compute_basis` quote of all six policies is verbatim in its own rule; every compute binding has a basis and every basis a binding; every baseline.rule sentence is in the rule; every prerequisite `policy_source` and every overwrite `replaced_by` is verbatim in the rule. PASS for XF-9 quoting.
- Rule words vs compute, branch by branch — defects (each a charter-global member, see findings):
  - C5: history reads (LATEST/COUNT) are keyed to the current enrollment (`check_compute.build_env`: `eq[holding_pk] = HID`), while every rule says "of the person / of the patient" and base `vision_evt_frequency` (not overwritten) says "Services of a person under an earlier Cascade vision enrollment count".
  - C7: same-date tie reads `pf_claim`, `pl_claim`, `pe_claim`, `pu_claim`, `pc_claim` filter only `date_of_service`, while the rule ties "two such services" (PAID/PAID_OON); fitting `tl_reason` reads any contacts row of `tl_date` while the rule names "the paid contact-lens service".
  - C8: `st_last` (exam) and `nw_last` (fitting) admit a paid service dated after the service being settled (negative MONTHS < 36), while the rules say "within thirty-six whole months before"; `tl_in_window` tests only the overall latest paid contacts, while the rule picks "the latest among those dated within" the window.
  - Lens pair_build: rule "decided without the frame benefit" vs compute counting only DENIED_FREQUENCY / DENIED_CONTACTS_IN_LIEU (a DENIED_NOT_COVERED frame scores 0 points instead of `pair_points_full`) — folded into C2 (only reachable on a plan without a frame benefit).
- Rounding: every rule says "rounded half up to the cent"; RND is Python `round(float, 2)` (banker's/float). Placement matches the rule; mode can differ only on an exact half-cent (observation O1; no task value is a half cent).
- Month convention: MONTHS() counts a month only when day(d2) ≥ day(d1), exactly as every rule's "a whole month being counted only when the day of the month of the order is not earlier than that of the last paid service". Benefit-year index `MONTHS('2000-'+mmdd, d)//12` matches "each benefit period beginning on the enrollment's benefit-period reset day" (stated in the frame rule only; the other rules rely on base `benefit_period_start_mmdd`).

### action_binding_and_uuids
- uuid8s: 5f5caac3, 308134ce, 646cd942, 87fedf94, 522b92fb, 9468302b — no shared prefix, no sequence, no reuse. PASS.
- No docstring names another tool, a sequence position or an ordering word ("After the call…" describes the tool's own effect). No concrete example values in docstrings or argument descriptions. No factor id is a substring of a tool name. PASS (XF-10).
- Defect C15: `decide_exam_service_5f5caac3` docstring: "Record Cascade's decision on one eye exam or contact-lens fitting service of a vision claim … the amount the plan pays for it", while `decide_contact_fitting_9468302b` records the decision on "one contact-lens fitting and evaluation service". The tool surface admits two business readings for a fitting decision (plan_paid via the exam tool, member_paid via the fitting tool); the fitting policy targets only the latter.
- Tool bodies judge nothing (pure `ctx.update`; `file_oon_contacts_claim` only reports a non-existent claim number). PASS.

### prerequisite_graph
Edges: frame→lens, frame→exam, lens→oon_lens, lens→exam, fitting→oon_contacts. All `problem` ids are extended policies of this file, none self, graph acyclic (exam, oon_lens, oon_contacts are sinks). Every `policy_source` verbatim in the blocked rule; all `form: state`, no `fallback_reason` (none needed). `kind: value_input` with gates `lens_with_copay`, `ex_same`, `pl_date`, `vx_same`, `tl_date` — all real bindings of the blocked compute. `resolved_by` equals the depended-on `target_tool` in all five. Conditions match the sentences in strength and scope. No authoring-viewpoint phrasing. PASS.

### prerequisite_sentences
| edge | sentence (blocked rule) | test |
| --- | --- | --- |
| frame→lens | "The member share of a frame order is fixed only after the spectacle-lens service carrying the same claim number no longer awaits a decision." | connective "only after"; record state (remark non-empty); no tool/id; one write brings it about for an in-network same-claim lens (lens member-share rule → decide_lens_order). PASS |
| frame→exam | "A frame order's member share is not worked out until no routine eye exam of the patient dated on or before the frame's date of service is still awaiting a decision." | "not … until"; state; exam plan-payment rule → decide_exam_service for participating exams. PASS (O5: an out-of-network held routine exam would satisfy the sentence's domain but no policy of this difficulty decides it) |
| lens→oon_lens | "A spectacle-lens order's member share is fixed only after no earlier-dated spectacle-lens receipt of the patient is still held without a remark." | "only after"; state; for an out-of-network held receipt the OON-lens rule ("paid to the member when the member files the claim") → file_oon_lens_claim. PASS |
| lens→exam | "The member share of a spectacle-lens order is not settled until every routine eye exam of the patient dated on or before the order carries a remark." | PASS |
| fitting→oon_contacts | "A fitting's member share is fixed only after no contact-lens receipt of the patient dated within the contact-lens frequency of the fitting is still held without a remark." | PASS (O5: an in-network held contacts service has no deciding write in this difficulty) |
No depended-on rule restates the sentence; no other cross-problem order is stated in any rule (the lens rule's pair_build reads the same-claim frame's state as a value; the order is pinned by the frame→lens edge, so no second order exists).

### override_declarations
Sentence-by-sentence against `base_policy_refs`:
- vision_evt_frequency s1 (per-kind frequencies, child lens frequency): followed by every rule. s2 (counting clause): overwritten by frame, exam, OON lens, OON contacts — NOT by the lens rule, which nevertheless restates its own whole-month counting → C3. s3 (contacts in lieu; DENIED_CONTACTS_IN_LIEU): not overwritten anywhere, not implemented by any availability test → C1. s4 (DENIED_FREQUENCY + materials discount; reversed service does not count): overwritten by the lens rule for lens orders; the reversed-service exclusion is re-implemented by claim number in all five frequency reads → C4. s5 (earlier enrollments count): not overwritten; compute ignores it → C5. s6 (fitting part of contacts benefit): followed by the fitting tie.
- vision_evt_in_network_benefits s1 (exam copay / fitting): overwritten by exam and fitting, siblings name each other. PASS. s2 (one materials copay): overwritten by frame and lens, siblings name each other. PASS. s4 (frame allowances): overwritten by frame. s6 ("A plan without a lens, frame or contacts benefit … denies that service DENIED_NOT_COVERED and the member may buy it at materials_discount_pct off retail"): not overwritten; frame and lens rules compute a covered member share on such plans → C2.
- vision_evt_oon_reimbursement s1: overwritten by OON lens and OON contacts; neither replaced_by names the sibling ("every other out-of-network service remains under the general out-of-network reimbursement rule") → C3 (XF-8 sibling member). s2 ("frequency limits and contacts-in-lieu apply exactly as in network"): contacts-in-lieu not implemented → C1; OON supplements paid on not-covered plans → C2.
- vision_evt_eligibility_timely_filing: followed (no rule weakens eligibility, filing limits or channel derivation).
- vision_evt_claim_reversal (not cited in any base_policy_refs) "restores the frequency the service had used": departed from by the claim-number reversal test → C4.

### factor_ladders
| policy | factor | label | tiers (reach) | baseline = fall-through | notes |
| --- | --- | --- | --- | --- | --- |
| frame | period_count | method | BY / no paid / months | yes | shape PASS (table below) |
| frame | allowance_channel | parameter | retail 80…/OON/private | yes | base content |
| frame | overage_rate | parameter | kid@private / retail-or-OON 0 / std | yes | |
| frame | household_bundle | parameter, cross dental | upper/other/0 | yes | multi-source (dental row + order channel) |
| frame | copay_age_band | parameter | kids / young adult 19–25 / std | yes | C9 (inverted on Premier 200) |
| frame | exam_eyewear_link | parameter | same-day same agreement / ≤12 m / 0 | yes | multi-source |
| lens | savings_program | parameter, cross savings | Plus 40 / S&S 35 / materials | yes | O3 |
| lens | visit_link, pair_build, age_points, dental_bundle | parameter | 3 each | yes | |
| lens | location_share | method | ×0.8 / ×0 (OON) / ×1 | yes | C12: multipliers; OON tier unreachable |
| exam | period_count | method | BY / no paid / months | yes | PASS |
| exam | fee_schedule | parameter | retail 88 / private 105 / billed charge | yes | C11: fall-through unreachable, baseline straw man |
| exam | patient_status, pediatric_ratio | parameter | private / chain / 1 | yes | multi-source (history + channel) |
| exam | copay_age_band | parameter | kids 0 / senior 5 / std | yes | C9 (senior 5 > Premier 0) |
| exam | household_bundle | parameter, cross dental | 5 / 3 / 0 | yes | C10 (provider payment raised by a dental enrollment) |
| OON lens | period_count | method | BY / no paid / months | yes | PASS |
| OON lens | oon_lens_amount (4), age_supplement, household_bundle, savings_member | parameter | | yes | |
| OON contacts | period_count | method | | yes | PASS |
| OON contacts | certified_reason, savings_member, household_bundle | parameter | | yes | |
| fitting | benefit_tie | parameter | MN 120 / elective specialty allowance / 0 | NO | C14 |
| fitting | fit_cost_rule | method | premium ×0.9 / capped MN(·,60) / plain | yes | C13 |
| fitting | household_bundle, new_wearer | parameter | | yes | |

Counts as declared: frame 6 (5p/1m), lens 6 (5p/1m), exam 6 (5p/1m), OON lens 5 (4p/1m), OON contacts 4 (3p/1m), fitting 4 (3p/1m). After striking C11/C10 (exam) 4 remain (3p/1m) — still in bounds; after striking C12 the lens has 0 method factors; after striking C13 the fitting has 3 factors and 0 method — both out of bounds. Every tier is stated in the rule (condition and value/method) and implemented in compute; no ladder tier lives only in compute. No factor reads another factor's binding (closure listed per policy: each factor's bindings read only F/P/K, its own LATEST/COUNT/CFIELD reads and the shared order selection), XF-1 PASS; assembly sentences are generic and fix the order of non-commuting steps (XF-2/3 PASS).

Method-shape all-pairs (XF-4/15):
| factor | pair | verdict | distinguishing input |
| --- | --- | --- | --- |
| period_count (4 policies) | BY vs months | PASS (adds data-anchored benefit-period floor) | last paid 2024-12-18, order 2026-10-03, 24-month frame: BY open, months 21 closed |
| period_count | BY vs no-paid | PASS | same-period order: BY closed, no-paid open |
| period_count | months vs no-paid | PASS | months closed when <N |
| lens location_share | ×0.8 vs ×1, ×0 vs ×1, ×0.8 vs ×0 | FAIL (constant multipliers of the same assembled percentage) | — |
| fitting fit_cost_rule | premium (×0.9) vs plain | FAIL (constant multiplier) | — |
| fitting fit_cost_rule | capped vs plain, capped vs premium | PASS (adds MN with tariff contact_fitting_standard_copay_max) | above = 80: capped 60, plain 80 |

### findings
Charter-global findings (each RED per the coordinator's XF rule; tasks affected named):

- **C1 SOURCE-POLICY RED — contacts-in-lieu dropped.** Base `vision_evt_frequency` s3 (in force, overwritten by nobody): "When contacts_in_lieu_of_glasses is true an elective contact-lens benefit uses both the lens and the frame benefit for their frequency periods, and lenses or a frame ordered while that benefit is used are denied DENIED_CONTACTS_IN_LIEU"; base OON s2 "frequency limits and contacts-in-lieu apply exactly as in network". `frame_open`, `lens_open`, `receipt_open`, `contacts_open` read only same-kind services. Probe P4 (task 0 world + a paid elective contacts service 2026-02-01): frame rule 104.00 vs base reading DENIED_CONTACTS_IN_LIEU at 20% off = 175.20. All six plans carry `contacts_in_lieu_of_glasses: true`. Tasks: no task world has a paid contacts service in a frame/lens period → no task consequence.
- **C2 SOURCE-POLICY RED — not-covered branch dropped (dropped branch / 0-1 multiplier).** Base `vision_evt_in_network_benefits` s6 (not overwritten): a plan without the benefit "denies that service DENIED_NOT_COVERED and the member may buy it at materials_discount_pct off retail". On Cascade Vision Exam Plus (lens/frame/contacts false): probe P3 frame 184.00 vs base 153.30; lens 0.00 vs base 217.00; OON lens reimbursement 20.00 (supplements only) vs base 0 (denied); OON contacts rule explicitly gives "nothing" as the amount but still adds the savings/bundle supplements. Lens pair_build likewise never yields `pair_points_full` for a DENIED_NOT_COVERED frame although the rule says "decided without the frame benefit". Tasks: both worlds are Select 150 → no task consequence.
- **C3 SOURCE-POLICY RED — undeclared lens month counting; sibling overwrites not cross-named (XF-8).** The lens rule states "a whole month being counted only when the day of the month of the order is not earlier than that of the last paid service" but overwrites only s4 of vision_evt_frequency; base s2 ("the last day of the month being used when that day does not exist") stays in force for lenses, and the four siblings' replaced_by say "every other service remains under the general frequency counting". Second answer: months-basis plan, last paid lens 2024-02-29, order 2025-02-28 → base: available (target day → 02-28); lens rule: 11 months, DENIED_FREQUENCY. Sibling members: the counting-clause overwrites of frame, exam, OON lens, OON contacts each name none of the other three; the OON-clause overwrites of OON lens and OON contacts do not name each other. Tasks: no consequence (benefit-year plan, no Feb-29 date).
- **C4 SOURCE-POLICY RED — reversal tested by claim number.** All five frequency reads: "when that service carries a reversal on its claim number the person is treated as having no paid … service in the frequency window" (`pf/pl/pe/pu/pc_reversed = COUNT(vision_claim_reversal, claim_number=…)`). Base: a reversal "references the service it reverses … and restores the frequency the service had used" (vision_evt_claim_reversal) and the measure takes the latest paid service "that ha[s] not been reversed". Lens and frame of one order share a claim number (task 0: V73-241218-2052). Probe P1 (task 0 on Select 130, months basis): no reversal → frame 175.20; a reversal of the 2024-12-18 *lens* → frame treated as never paid → 114.00. Also an earlier unreversed paid service is discarded when the latest is reversed. Tasks: no reversal rows → no consequence.
- **C5 XF-5 RED — "the person" read as "this enrollment".** Every history read is scoped to the current vision_plan_id; rules and base s5 count the person's earlier Cascade enrollments. Probe P5b: Mateo's 2024-12-18 frame booked under an earlier enrollment → compute 114.00 (available) vs rule 175.20 (21 months < 24 on a months plan). Members: frame pf_*, ex_same/ex_any; lens pl_*, vx_*; exam pe_*, st_*; OON lens pu_*; OON contacts pc_*; fitting tl_*, nw_*. Tasks: one enrollment per person → no consequence.
- **C6 XF-6/7 RED — dental bundle reads first subscriber row, not the active one.** `CFIELD('dental', 'status'|'variant_name', billing_account_id=…, enrollee_relationship='subscriber')` returns the first matching row; the rule tier is "holds an active … enrollment". Probe P2 (terminated subscriber dental row ahead of the active one): frame 129.00 vs 104.00; exam 85.01 vs 90.01. Members: frame bdl_*, lens bd_*, exam eb_*, OON lens ub_*, OON contacts cb_*, fitting fb_*. Tasks: single subscriber dental row → no consequence.
- **C7 XF-5/7 RED — tie reads without the remark filter.** `pf_claim`, `pl_claim`, `pe_claim`, `pu_claim`, `pc_claim` choose among all same-kind rows of the paid date (a later-received DENIED/held row on that date supplies the claim number the reversal test reads); fitting `tl_reason` reads any contacts row of `tl_date`. Rule: "when two such services [PAID/PAID_OON] share that date the one received most recently"; "the paid contact-lens service". Tasks: no same-date decoy → no consequence.
- **C8 XF-6 RED — negative date differences and window pick.** Exam `status_ratio`: a paid exam under the same agreement dated after the held exam gives MONTHS < 0 < 36 → "established", rule says "before the exam". Fitting `new_allowance`: a later paid fitting gives "not new", rule says "before the fitting". Fitting `tl_in_window` tests only the overall latest paid contacts. Tasks: no such rows → no consequence.
- **C9 SOURCE-FACTOR RED (realism, unreal outcome).** Frame copay_age_band: kids_materials_copay 10.00 and young_adult 15.00 against Premier 200 materials_copay 0.00; exam copay_age_band: senior_exam_copay 5.00 against Premier 200 exam_copay 0.00 — the "reduced" age-band tiers charge children/seniors more than the plan's standard copay; no carrier publishes a child or senior band above its adult copay. Tasks: Select 150 → no consequence.
- **C10 SOURCE-FACTOR RED (realism).** Exam household_bundle: "the plan adds a household bundle supplement" to `plan_paid` of a participating exam because the subscriber holds a dental PPO plan; the member's copay is unchanged, so the only effect is paying the provider above the fee schedule the same rule calls "the contracted routine-exam amounts". A participating provider's payment is set by the fee schedule, never by the patient's other insurance products. Task 0 bears it (see task_0.md).
- **C11 SOURCE-FACTOR RED (dead fall-through / straw-man baseline).** Exam fee_schedule "for any other location it is the billed charge" — the rule settles only participating exams ("an out-of-network exam receipt is outside this rule"; `fe_channel` reads only in_network rows), so the fall-through, which is also the baseline (`exam_fee: ex_charge`), is never reached: two reachable tiers, and the baseline pays a participating exam its billed charge, which the base charter itself rules out ("the plan pays the rest of the provider's contracted exam fee"). Task 0 bears it.
- **C12 SOURCE-FACTOR RED (mislabelled method; dead tier).** Lens location_share: tiers multiply one assembled percentage by 0.8 / 0 / 1 — method-shape FAIL on all pairs; the OON tier is unreachable (lens rule settles participating orders only). The lens computation has no honest method factor. Task 0 bears it.
- **C13 SOURCE-FACTOR RED (method-shape pair).** Fitting fit_cost_rule premium = plain × 0.9 (constant multiplier). Task 1 sits on the premium tier.
- **C14 SOURCE-FACTOR RED (dishonest baseline).** Fitting benefit_tie baseline `fit_allowance: P('contact_fitting_specialty_allowance')`, fall-through tier "otherwise (no tied contact-lens service) → 0.00"; the baseline is the elective tier's value under another name. Task 1 bears it.
- **C15 SOURCE-POLICY RED (check 3).** Exam tool docstring covers "one eye exam or contact-lens fitting service" — second tool for the fitting decision. Task 1 bears it.

Observations (no consequence demonstrated): O1 RND is Python round, not half-up. O2 household-bundle and savings-membership supplements/allowances on member-facing amounts (frame, lens, OON lens, OON contacts, fitting) read as company perks, not industry practice — realism risk only. O3 the lens starting discount uses the savings membership's discount_eyewear_pct at Vision Network locations, while the savings charter honors that discount only at Savings Network practices ("Outside the savings network there is no discount"). O4 exam plan_paid has no lesser-of-billed cap (fee × ratios + supplement can exceed the billed charge). O5 state-form sentences whose domain includes rows no policy of this difficulty decides (held OON routine exam; held in-network contacts). O6 fitting rule header says "at a participating location" but its selection reads any channel. O7 the channel tiers read the claim's stored `network_channel` rather than the agreement in force (base derives it); in both worlds the stored value agrees with the agreement.

## closing_checklist
Written 2026-10-18T03:30, after both task derivations were frozen and then compared with GT (this section is post-reveal; the charter-global section above is unchanged).
- Files: `0.md`, `1.md` correspond one-to-one with tasks/0.json and tasks/1.json; `_difficulty.md` alongside; revision_1 only.
- Coverage and scope: task 0 claims vision_ext_oon_lens_reimbursement, vision_ext_exam_plan_payment, vision_ext_lens_member_share, vision_ext_frame_member_share (tools file_oon_lens_claim_87fedf94, decide_exam_service_5f5caac3, decide_lens_order_308134ce, decide_frame_order_646cd942); task 1 claims vision_ext_oon_contacts_reimbursement, vision_ext_fitting_member_share (file_oon_contacts_claim_522b92fb, decide_contact_fitting_9468302b). All six policies covered, scopes (whole trees) pairwise disjoint, task tools ⇄ GT closed, uuid8s independent.
- Trees: task 0 — 3 prerequisite problems, 4 value_input edges, owner=user receipt filing, acyclic; task 1 — 1 prerequisite problem, 1 value_input edge, owner=user filing, acyclic; difficulty-wide graph acyclic.
- Unique solution: blind derivation equals GT on every write, argument, owner, order and terminal state in both tasks.
- Factors: NOT closed — task 0 lens computation has no honest method factor (C12) and the exam carries an unreal supplement (C10) and a dead fall-through/straw baseline (C11); task 1 fitting fails the method-shape test on the tier taken (C13) and has a baseline ≠ fall-through (C14).
- Seeds: task 0 F0-4, task 1 F1-3/F1-4.
- Charter: C1–C9, C15 are charter defects (C1–C9 without consequence in either world; C15 with a task-1 tool-surface consequence).
- Gates were not re-run by this auditor (the brief's snapshot is authoritative for round 1); the difficulty does not pass the source-layer audit in this revision.

VERDICT revision_1: task0=RED task1=RED charter=C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12,C13,C14,C15

## revision_2

### charter_global_frozen (revision_2)
- Frozen 2026-10-18T04:45, before any round-2 GT was read. Same auditor as revision_1; revision_1 text above is untouched.
- Inputs re-hashed and equal to the brief: `vision.extended.yaml` sha256=55a889c9e75322a6dd3c1be788d3a85c297fbb9cca60b916765f7015dbfda634; `task_tools.py` sha256=665c3b0fe7ede9027f90aa847357d526c6e68404daec3980ad943c8dae5b8bb2. Both changed since revision_1, so every charter-global section is re-derived in full (not carried forward). Base copy (lines 1–969) still byte-identical to products/vision.yaml.
- Masked/unread at freeze: raw tasks/*.json and every GT field; difficulty worklog. Read: coordinator notes (unchanged), XF_recipe.md, charter, tools, r2 masked views (task_0 2fabf88b…, task_1 c0b0eba2…, verified), check_compute.py semantics.
- Gate snapshot (brief, 2026-10-18T04:14:36): 7/7 rc=0. Entry conditions complete.
- Probes: `/tmp/audit_vision_member_services_0070/ev.py` (ROUND=2) and `probe2.py`, charter compute on copies of the r2 worlds.

### policy_conflict_scan (revision_2)
Same six policies, tools, owners and computes as revision_1. Lens factors changed (savings_program and location_share removed; option_pricing added); OON lens adds polycarbonate_supplement; exam household_bundle now scales the member copay; fitting fit_cost_rule re-tiered. Trigger rule (XF-14): unchanged tool bodies (one `ctx.update` on a vision_claims row; events with `triggers: []`) — PASS.

### rule_compute_equivalence (revision_2)
- Mechanical sweep: every compute_basis quote verbatim in its rule; bindings ⇄ bases complete; baseline sentences, prerequisite sentences and replaced_by texts all in their rules. PASS (XF-9).
- Rounding now `int(x*100+0.5)/100` (half up) in every result — O1 closed.
- Same-date tie reads now filter PAID / PAID_OON (`pf_rn/pf_ro/pf_id`, `pl_*`, `pe_*`, `pu_*`, `pc_*`, `plc_*`, `puc_*`); fitting `tl_reason` filters remark and date — C7 closed. Reversal test reads `original_vision_claim_id` of the chosen service — C4 claim-number defect closed (residual in D2). Dental reads carry `status='active'` in all six policies — C6 closed. `st_last <= ex_dos` guard; `nw_last > x_dos` matches the reworded "latest … dated on or before" rule; tie window reworded to the latest paid service — C8 closed. Enrollment-only history declared by a scoped overwrite in frame, lens, exam, OON lens, OON contacts — C5 closed (rule words now equal compute).

### action_binding_and_uuids (revision_2)
uuid8s unchanged and independent. `decide_exam_service_5f5caac3` now documents "one routine eye exam service … (contact-lens fittings are not decided with this tool)" — C15 closed. No example values, no ordering words, no tool names in docstrings. Bodies judge nothing. PASS.

### prerequisite_graph / prerequisite_sentences (revision_2)
Edges unchanged in shape: frame→lens (lens_with_copay), frame→exam (ex_same), lens→oon_lens (gate now `pl_o`), lens→exam (vx_same), fitting→oon_contacts (gate now `tl_o`). Sentences now name "at a participating location" (exam edges) and "out-of-network" (receipt edges), so each state is brought about by exactly one write of this difficulty — O5 closed. All verbatim, state form, ordering connective, acyclic, resolvers equal target tools. PASS.

### override_declarations (revision_2)
- vision_evt_frequency counting clause: overwritten by frame, lens, exam, OON lens, OON contacts; every replaced_by now names the four siblings — C3 closed. Earlier-enrollment sentence: same five, siblings named. Frequency-denial sentence: lens only (scoped). Contacts-in-lieu (s3): implemented in frame, lens, OON lens (counted from the later of same-kind and contacts service; DENIED_CONTACTS_IN_LIEU) — C1 closed (probe: frame with a paid contacts service in the period → 175.20, the base reading).
- vision_evt_in_network_benefits s6 (not covered): frame (discount at materials_discount_pct), OON lens and OON contacts (nothing) now follow base. **Lens does not** — D1.
- vision_evt_oon_reimbursement s1: overwritten by OON lens and OON contacts, siblings named. **s2 "lens options are not reimbursed when oon_lens_options_reimbursed is false" is not overwritten, yet the OON-lens polycarbonate supplement reimburses a lens option** — D4.
- vision_evt_claim_reversal / vision_evt_frequency s1: residual — D2.

### factor_ladders (revision_2)
| policy | factors (label) | notes |
| --- | --- | --- |
| frame | period_count (m), allowance_channel, overage_rate, household_bundle (dental), copay_age_band, exam_eyewear_link | D7 (bundle), D10 (young-adult tier) |
| lens | option_pricing (m), visit_link, pair_build, age_points, dental_bundle (dental) | D6, D7 |
| exam | period_count (m), fee_schedule, patient_status, pediatric_ratio, copay_age_band, household_bundle (dental) | D7, D9 (senior tier); fee_schedule tiers all reachable, baseline exam_fee_private = fall-through (C11 closed) |
| OON lens | period_count (m), oon_lens_amount, age_supplement, polycarbonate_supplement, household_bundle (dental), savings_member (savings) | D4, D7, D8, D9 |
| OON contacts | period_count (m), certified_reason, savings_member (savings), household_bundle (dental) | D5, D7, D8 |
| fitting | benefit_tie, fit_cost_rule (m), household_bundle (dental), new_wearer | D7; benefit_tie fall-through "elective → contact_fitting_specialty_allowance" = baseline (C14 closed) |

Method-shape all-pairs (XF-4/15):
| factor | pair | verdict |
| --- | --- | --- |
| period_count ×4 | BY vs months / BY vs none / months vs none | PASS (as revision_1) |
| fit_cost_rule | specialty@private (billed − allowances) vs standard (MN(billed − allowances, 60)) | PASS (adds MN with tariff) |
| fit_cost_rule | specialty@chain (billed × 0.90, no allowance) vs specialty@private | PASS (drops the allowance inputs: different input set) |
| fit_cost_rule | specialty@chain vs standard | PASS |
| option_pricing | child-with-options vs adult-with-options | **FAIL** — identical algorithm (options at plan copays, rest discounted); they differ only in the polycarbonate price (0 vs option_copay_polycarbonate_adult), a number |
| option_pricing | either "with options" tier vs "no options" | **FAIL on the reachable domain** — the "no options" tier's method (whole charge discounted) is the same algorithm at opt_part = 0, the only value it can take there |
Realism judgment of the perks the reworker flagged (coordinator: invented ladder = RED): household dental bundle — RED (D7); Smile & Sight supplements on out-of-network receipts — RED (D8); exam-and-eyewear allowance — accepted (exam-linked eyewear incentives within 12 months of an exam are standard plan design, e.g. extra savings on eyewear bought within 12 months of the last covered exam); new-wearer allowance — accepted (new-fit vs refit fitting fees are standard); pediatric exam ratios — observation (no evidence either way that commercial vision fee schedules vary the routine-exam fee by age; not demonstrated unreal). Kids' reduced copays (pediatric vision cost-sharing) accepted; lens senior discount points accepted (retail senior discounts on non-benefit eyewear exist).
Counts after striking RED factors/tiers: frame 4 (3p/1m, no cross-difficulty); lens 3p/0m — out of bounds; exam 4 (3p/1m, no cross-difficulty); OON lens 2 — out; OON contacts 1 — out; fitting 3 — out. No computation keeps a real cross-difficulty factor.

### findings (revision_2)
Status of revision_1 charter findings: C1 closed; C2 partly closed (frame, OON lens, OON contacts) — residual D1; C3 closed; C4 claim-number defect closed — residual D2; C5 closed (declared); C6 closed; C7 closed; C8 closed; C9 closed (fractions of the plan copay; Premier 0 → 0); C10 re-shaped (now a member copay share) — judged under D7; C11 closed; C12 closed (location_share removed; replacement D6); C13 closed; C14 closed; C15 closed. O1, O3 (savings start percentage removed), O4 partly (lesser-of now applied, residual D3), O5, O6 closed.

New / residual findings (each RED per the XF rule):
- **D1 SOURCE-POLICY RED (C2 residual, lens not-covered pricing).** Lens rule: "a plan whose lens_benefit_included is false denies the order DENIED_NOT_COVERED; in each case the order is bought without the lens benefit", then prices it with points and option pricing. Base in_network s6 (not overwritten; the lens frequency overwrite is scoped to orders "requested before its benefit is available again"): "the member may buy it at materials_discount_pct off retail". Probe (task 0 world on Exam Plus): lens rule 139.50 vs base 217.00. No task consequence (Select 150).
- **D2 SOURCE-POLICY RED (C4 residual).** Frame/lens/exam/OON rules: when the latest paid service "is referenced by a reversal entry … otherwise the enrollment is treated as having no paid … service in the frequency window", discarding earlier unreversed services that still used the benefit (base s1 "available once per its frequency"; vision_evt_claim_reversal restores only "the frequency the service had used"). Probe (task 0 world): contacts paid 2025-02-01 and 2026-02-01, the latter reversed → frame 104.00 (available); the same world without the reversed service → 175.20 (DENIED_CONTACTS_IN_LIEU from the 2025 contacts, 1 benefit period < 2). Divergence arises where a 24-month frame counts from 12-month contacts. No task consequence (no reversals).
- **D3 SOURCE-FACTOR RED (O4 residual, realism).** Exam: the lesser-of-billed test is applied before the ratios ("the exam fee is the billed charge when the billed charge is below the scheduled amount", then "multiplied by every ratio"). Probe: new-patient child at a retail chain billed 85.00 → plan_paid 86.75 + member copay 2.50 = 89.25 > 85.00 billed. No carrier pays more than the provider billed. No task consequence (task 0 billed 120.00 ≥ 88.00).
- **D4 SOURCE-POLICY RED + SOURCE-FACTOR RED (OON polycarbonate supplement).** (a) Undeclared override: base vision_evt_oon_reimbursement s2 "lens options are not reimbursed when oon_lens_options_reimbursed is false" (false on all six plans, not superseded); the supplement is paid because "a receipt listing polycarbonate" — reimbursing a lens option. (b) Dead tier: "child_polycarbonate_covered is false → oon_child_poly_part" is reachable only on Exam Plus, whose lens_benefit_included is false, so the result is 0.00 whatever the tier — two reachable outcomes. Task 0 consequence (see 0.md).
- **D5 SOURCE-FACTOR RED (dead tier).** OON contacts certified_reason tier "medically necessary reason under a plan that does not cover medically necessary contacts → 0.00": only Exam Plus has `contacts_medically_necessary_in_network: not_covered`; there the fall-through value oon_contacts_elective_reimbursement is also 0.00 and the result is gated to 0 by contacts_benefit_included false — the tier selects the same outcome as the fall-through on its whole reachable domain. Task 1 bears the factor (see 1.md).
- **D6 SOURCE-FACTOR RED (lens option_pricing).** Method-shape table above: the two "with options" tiers select the same method and differ by one price; the "no options" tier equals that method at opt_part = 0. One method tier written as three. Task 0 bears it.
- **D7 SOURCE-FACTOR RED (realism: household dental bundle, all six policies).** Re-judged at the coordinator's request (revision_1 recorded it as observation O2; the exam variant was C10). A frame-allowance bonus, eyewear discount points, an exam-copay share, out-of-network reimbursement supplements and a fitting allowance, each granted because the subscriber also holds a Cascade dental PPO plan on the same billing account. US dental/vision carriers price multi-line households through premium (bundled rates), never through per-claim benefit amounts that read another product's enrollment and tier (Plus/Premier/Elite vs other plans). Members: frame household_bundle, lens dental_bundle, exam household_bundle, OON lens household_bundle, OON contacts household_bundle, fitting household_bundle. Both tasks bear it.
- **D8 SOURCE-FACTOR RED (realism, cross-charter): Smile & Sight supplements on out-of-network receipts** (OON lens savings_member, OON contacts savings_member). The savings charter: "A member who also holds Cascade … vision coverage may use the savings discount only for services that coverage does not pay for … never on the member's share of a covered service"; savings discounts apply only "At a practice holding an active Cascade Savings Network Participating Provider Agreement". Raising the insured reimbursement of a covered out-of-network receipt because a discount card is held combines the card with a covered service at a non-network supplier — contrary to the owning charter and not something any carrier does. Both tasks bear it.
- **D9 SOURCE-FACTOR RED (realism: senior tiers on insured amounts).** Exam copay_age_band "three quarters of exam_copay for a patient aged 65 or more"; OON lens age_supplement "senior_oon_supplement" for 65+. Commercial vision plans do not vary insured copays or out-of-network reimbursement at age 65. Present since revision_1, not reported then (auditor miss). No task consequence (patients 16 and 39).
- **D10 SOURCE-FACTOR RED (realism: young-adult materials copay).** Frame copay_age_band "three quarters of materials_copay for a covered child aged child_age_limit_years through 25": dependent eligibility to 26 is an enrollment rule; no carrier reduces the materials copay for 19–25-year-old dependents. Present since revision_1, not reported then. No task consequence (Mateo is 16).
- Factor-floor consequence: with D4–D10 struck, lens (0 method), OON lens (2 factors), OON contacts (1), fitting (3) fall below the bounds, and neither task keeps a real cross-difficulty factor.

Observations (revision_2): R2-O1 pediatric exam ratios unproven either way. R2-O2 enrollment-only frequency (declared) departs from usual carrier practice of counting a member's services across continuous coverage; declared, so not a conflict. R2-O3 fitting tie ignores reversal of the tied contacts service (rule and compute agree). R2-O4 on a plan without a lens or contacts benefit the OON rules reimburse 0.00 but the member's tool can only record PAID_OON_REIMBURSEMENT (base would record DENIED_NOT_COVERED); no task reaches it.

## closing_checklist (revision_2)
Written after both revision_2 derivations were frozen and compared (post-reveal; the revision_2 charter section above was written before the reveal).
- Files 0.md / 1.md / _difficulty.md, revision_2 appended, revision_1 untouched.
- Coverage: all six policies across the two tasks; scopes disjoint; tools ⇄ GT closed; uuid8s independent.
- Trees: task 0 n=3 / 4 value_input / owner=user; task 1 n=1 / 1 value_input / owner=user; graph acyclic.
- Unique solution: blind = GT on every write in both tasks; task 0 carries the D4 second reading on the receipt amount (70.00 vs 85.00).
- Factors: NOT closed (D4–D10; lens 0 method; OON lens, OON contacts, fitting below 4 surviving factors; no real cross-difficulty factor in either task).
- Charter: D1, D2, D3 (no task consequence) plus the factor findings above. Gates not re-run by this auditor (brief snapshot authoritative).

VERDICT revision_2: task0=RED task1=RED charter=D1,D2,D3,D4,D5,D6,D7,D8,D9,D10

## revision_3

### charter_global_frozen (revision_3)
- Gate protocol `/tmp/erl0070_coord/reaudit_gate.txt` followed: worklog tail = `REWORK round 3 claims: D1,…,D10,F0-5,F0-6,F0-7,F1-5,F1-6` / `REWORK round 3: gates 7/7 green`; `/tmp/erl0070_coord/snapshot.sh vision_member_services 3` run at 2026-10-18T07:03:01 — check_extended / check_task_tools / replay_tasks / check_solvability / check_compute / check_grounding / check_cross_fire all rc=0 OK; views r3/task_0.json sha256=17b81bb9bc45396ba0271dfc3d5742f1fbabb581a85d67295f9143ede384ee87, r3/task_1.json sha256=ac51719f60282247b6bc236477ca1ccc089346f3b6dc4187c1f5d2f1578fa5bb; `vision.extended.yaml` sha256=507ceb2c4275838c2fa4e696e36d54ef7ab89c1010c9de93065e3de4540abed0 (changed → all charter sections re-derived); `task_tools.py` sha256=665c3b0f… (unchanged since revision_2; action_binding_and_uuids carried forward on that hash).
- Frozen 2026-10-18T07:08, before any round-3 GT was read. Base copy still byte-identical. Probes: `ev.py` (ROUND=3), `probe3.py`.

### policy_conflict_scan (revision_3)
Same six policies/tools. Struck since revision_2: every household dental bundle, every Smile & Sight read, senior and young-adult tiers. Added in all six policies: factor `eligibility_basis` (label method, cross_difficulty billing) reading the funding billing account's status, paid_through_date and aptc_monthly_amount. Added: age bands with an under-six tier (lens points, exam copay, OON lens and OON contacts pediatric supplements); `exam_continuity` supplements (OON lens, OON contacts); frame copay_band (OON → 0). option_pricing relabelled parameter. Trigger rule: unchanged tools, PASS.

### rule_compute_equivalence (revision_3)
Sweep: quotes verbatim, bindings ⇄ bases complete, baselines and prerequisite/replaced_by texts in rules — PASS. One branch without a rule sentence: E3 (frame out-of-network receipt denied for timely filing → member_paid 0.00; the rule states only the denial). Exam cap `MN(ex_billed, fee × ratios)` matches "the product is capped at the billed charge" (D3 closed). Lens not-covered branch = materials_discount_pct off retail (D1 closed).

### prerequisite_graph / sentences (revision_3)
Unchanged edges, gates (lens_with_copay, ex_same, pl_o, vx_same, tl_o), sentences and resolvers — PASS.

### override_declarations (revision_3)
- New scoped overwrite of vision_evt_claim_reversal in frame, lens, exam, OON lens, OON contacts ("a reversal of the last paid service clearing the frequency window unless another paid service of the kind shares its date") — D2 is now a declared departure (closed; realism note R3-O2).
- OON lens now overwrites vision_evt_oon_reimbursement s2 for child polycarbonate, scoped — D4a closed.
- **No policy overwrites vision_evt_eligibility_timely_filing**, yet every rule replaces its s1 ("payable only if the enrollment was active on its date_of_service (on or after coverage_effective_date and on or before any termination_date)") and s2 ("Services with a date of service while the funding billing account is in grace_period are adjudicated normally") with a paid-through/grace test — E1.

### factor_ladders (revision_3)
| policy | factors | struck / defects |
| --- | --- | --- |
| frame | eligibility_basis (m, billing), period_count (m), allowance_channel, overage_rate, copay_band, exam_eyewear_link | eligibility_basis (E2) |
| lens | eligibility_basis (m, billing), option_pricing, visit_link, pair_build, age_points | E2; age_points under-six tier (E4) |
| exam | eligibility_basis (m, billing), period_count (m), fee_schedule, patient_status, pediatric_ratio, copay_band | E2; copay_band under-six tier (E4) |
| OON lens | eligibility_basis (m, billing), period_count (m), oon_lens_amount, pediatric_supplement, polycarbonate_supplement, exam_continuity | E2, E4, E5, E6 |
| OON contacts | eligibility_basis (m, billing), period_count (m), pediatric_supplement, exam_continuity | E2, E4, E5 |
| fitting | eligibility_basis (m, billing), benefit_tie, fit_cost_rule (m), new_wearer | E2 |
option_pricing as a parameter is now honest (its tiers select the option-copay amount priced outside the discount) — D6 closed. Method-shape all-pairs: period_count ×4 and fit_cost_rule PASS as in revision_2. eligibility_basis: late (constant 0.00 / full charge) vs grace (benefit formula) vs paid_through (benefit formula when DOS ≤ paid-through, else deny) — the tiers select an eligibility outcome over one unchanged benefit formula (see E2). Factor independence: no factor reads another factor's binding (eligibility bindings fe_/le_/ee_/ue_/ce_/xe_ read only the claim and the billing row) — PASS.
Survivors after striking: frame 5 (4p/1m); lens 3p/0m — out; exam 4 (3p/1m); OON lens 2 — out; OON contacts 1 — out; fitting 3 — out. With eligibility_basis struck no computation keeps a cross-difficulty factor.

### findings (revision_3)
Status of revision_2 findings: D1 closed; D2 closed (declared overwrite; realism R3-O2); D3 closed; D4 closed in its (a) half, (b) half replaced by E6; D5 closed (certified_reason removed; MN amount is a plain binding); D6 closed (relabelled parameter, honest); D7 closed (all dental-bundle reads removed); D8 closed (all savings reads removed); D9 closed (senior tiers removed); D10 closed (young-adult tier removed).

New findings (RED per the XF rule):
- **E1 SOURCE-POLICY RED (all six policies) — undeclared replacement of base eligibility.** Rule: "eligibility on the date of service follows the billing account that funds the enrollment: when that account is in its grace period, receives no advance premium tax credit and the date of service is later than its paid-through date, coverage continues …; otherwise the service is eligible only when its date of service is on or before the account's paid-through date". Base vision_evt_eligibility_timely_filing s1/s2 stay in force (no overwrite), and the billing charter (billing_grace_and_lapse): "During grace coverage continues; on an APTC account claims with dates of service from month aptc_claims_pend_from_grace_month of the grace period onward are pended, and on other accounts claims are paid normally." Second readings (probe3, task 0 world): (a) exchange APTC account in grace month 1 → extended DENIED_NOT_ELIGIBLE, member 219.00; base/billing → adjudicated normally, 129.00; (b) Mateo's enrollment terminated 2026-08-31 with the account paid through 2026-10-31 → extended eligible, 129.00; base s1 → DENIED_NOT_ELIGIBLE, 219.00. No task consequence (both worlds are non-APTC grace with active enrollments, where the two readings agree).
- **E2 SOURCE-FACTOR RED (all six policies) — eligibility_basis: straw-man baseline, gate labelled method.** Baseline `*_mode: 'paid_through'` and baseline.rule "a service is eligible when its date of service is on or before the paid-through date … and a service dated later is denied DENIED_NOT_ELIGIBLE": applied to a non-APTC account in grace it denies exactly the claims that base s2 and the billing charter say are "adjudicated normally" / "paid normally" — a treatment no reader of the charters and no carrier would give. The factor's tiers select deny / pay over one unchanged benefit formula (an existence gate — the 0/1-multiplier form), not a way the quantity is computed; the "late" tier is base timely-filing content. Both tasks sit on the grace tier, so the factor's apparent weight (task 0 frame 219.00, lens 310.00, exam/receipt 0.00; task 1 receipt 0.00, fitting 230.00) is the distance to a straw man. It is the only method factor of the lens and the only cross-difficulty factor everywhere.
- **E3 XF-5 RED (frame) — compute branch without a rule sentence.** Frame `result: 0.0 if fe_mode == 'late'` also for an out-of-network receipt (timely_filing_days_oon): probe3 → member_paid 0.00 while the member bears the unreimbursed receipt (219.00); the rule states only "is denied DENIED_TIMELY_FILING" and base exempts the member only "for a participating provider". No task consequence.
- **E4 SOURCE-FACTOR RED (realism) — under-six tiers.** Lens age_points "under six years old … young_child_points", exam copay_band "nothing for a patient under six", OON lens pediatric_supplement "young_child_oon_supplement", OON contacts pediatric_supplement "young_child_cl_supplement": commercial vision schedules carry one pediatric band (under 19, the pediatric-vision band); an under-six split of copays, discount points and out-of-network reimbursement is not published by any carrier and appears here exactly where the struck senior tier left a two-tier ladder (a ladder filled to reach the floor). With the tier struck each of the four ladders has two tiers. OON contacts pediatric_supplement as a whole (a children's supplement on contact-lens reimbursement) has no counterpart in carrier practice either. Both tasks bear the affected factors (patients 16 and 15, on the 6–18 tier).
- **E5 SOURCE-FACTOR RED (realism) — exam_continuity supplements.** OON lens and OON contacts: "when the latest paid routine eye exam of the enrollment lies within twelve whole months before or after the receipt's date of service the receipt receives … exam_oon_recent / exam_cl_recent, … twelve to twenty-three … exam_oon_older / exam_cl_older". Out-of-network eyewear reimbursement is a fixed schedule amount per material; carriers do not raise it with exam recency, and an exam dated after the purchase cannot change what the purchase is reimbursed. Both tasks bear it (10.00 each).
- **E6 SOURCE-FACTOR RED — polycarbonate_supplement tiers 2 and 3 select the same value.** "polycarbonate for any other patient (a lens option, not reimbursed) → 0.00" and "otherwise (no polycarbonate listed) → 0.00": one tier written as two; two distinct outcomes. Task 0 bears it.
- Factor-floor consequence: lens 0 method; OON lens, OON contacts, fitting below 4; no real cross-difficulty factor in either task.

Observations (revision_3): R3-O1 pediatric exam ratios (unchanged, unproven either way). R3-O2 the declared reversal overwrite discards an earlier unreversed service that used the benefit (only reachable when a 24-month frame counts from 12-month contacts); legal, unusual. R3-O3 the realistic core of the billing read — claims during a non-APTC grace paid normally, APTC month-1 paid and months 2–3 pended, services after a lapse denied — is what the billing charter already states; the defect is in the factor wrapping it (E1/E2), not in reading the billing account.

## closing_checklist (revision_3)
Written after both revision_3 derivations were frozen and compared (post-reveal).
- Files: revision_3 appended to 0.md, 1.md, _difficulty.md; older revisions untouched.
- Coverage/scope/tools/uuid8s: unchanged, PASS. Trees: task 0 n=3 / 4 value_input / owner=user; task 1 n=1 / 1 / owner=user; acyclic.
- Unique solution: blind = GT on every write in both tasks.
- Factors: NOT closed (E2, E4, E5, E6; lens 0 method; OON lens, OON contacts, fitting below 4 survivors; no real cross-difficulty factor). Charter E1, E3 without task consequence.
- Gates: snapshot of round 3 run per the gate protocol (7/7 OK).

VERDICT revision_3: task0=RED task1=RED charter=E1,E2,E3,E4,E5,E6

## revision_4

### charter_global_frozen (revision_4)
- Gate protocol followed: worklog tail `REWORK round 4 claims: E1,E3` / `REWORK round 4: gates 7/7 green`; `snapshot.sh vision_member_services 4` at 2026-10-18T12:57:30 — 7/7 OK; views r4/task_0.json sha256=17b81bb9…ee87 and r4/task_1.json sha256=ac51719f…a5bb (identical to r3: worlds and personas unchanged); `vision.extended.yaml` sha256=383a647418fe0c3bd9fc68d474c8b843092b350f0b54158a6a68b155faa24a8b (changed → charter re-derived); `task_tools.py` 665c3b0f… unchanged (tool section carried forward on that hash).
- Frozen 2026-10-18T12:59, before any round-4 GT was read. Base copy byte-identical. Probes: ev.py (ROUND=4), probe3.py.

### what changed (revision_4)
Only the eligibility machinery: every eligibility_basis now has five tiers (late / enrollment not active / APTC grace month ≥ 2 held / grace settled as usual / otherwise settled when DOS ≤ paid-through), each policy adds a scoped overwrite of vision_evt_eligibility_timely_filing s2, and the frame states the out-of-network late case ("the member keeps the whole charge"). All other factors, ladders and parameters are as in revision_3 (re-listed by the mechanical sweep: under-six tiers, exam_continuity and polycarbonate_supplement unchanged). Sweep: quotes, bindings, baselines, prerequisite and replaced_by texts all PASS; prerequisite graph unchanged, PASS; trigger rule PASS.

### findings (revision_4)
Status of revision_3 findings (reworker claimed E1, E3 only):
- **E1 partly closed.** APTC grace month 1 now settles (probe: frame 129.00 = base/billing reading); terminated enrollment now denied (219.00 = base s1); APTC grace months ≥ 2 held, matching billing_grace_and_lapse. Residuals: G1, G2, G3 below.
- **E3 closed** (probe: out-of-network frame filed late → 219.00, and the rule now says so).
- **E2 open (not claimed).** Baseline of every eligibility_basis is still `'paid_through'` with baseline.rule "a service is eligible when its date of service is on or before the paid-through date … a service dated later is denied DENIED_NOT_ELIGIBLE" — in both task worlds (non-APTC grace) it denies the services the rule itself, base s2 and billing_grace_and_lapse settle normally; the tiers still select deny / hold / pay over one benefit formula. Still the only cross-difficulty factor everywhere and the lens's only method factor.
- **E4 open (not claimed):** under-six tiers unchanged in lens age_points, exam copay_band, OON lens and OON contacts pediatric_supplement.
- **E5 open (not claimed):** exam_continuity unchanged in OON lens and OON contacts.
- **E6 open (not claimed):** polycarbonate_supplement tiers 2 and 3 both 0.00.

New / residual (RED per the XF rule):
- **G1 SOURCE-POLICY RED (E1 residual, all six policies).** The fall-through "otherwise the service is settled when its date of service is on or before the account's paid-through date" denies a service of an active enrollment on an account that is not (yet) in grace when its DOS is past the paid-through date — e.g. a service on the premium due date itself (the account enters grace only "on the day after a premium due date"). Base s1 (not overwritten; only s2 is superseded): "A service is payable only if the enrollment was active on its date_of_service". Probe: account active, paid through 2026-08-31, frame dated 2026-09-01 → extended not eligible, 219.00; base s1 → payable (129.00 on the task-0 figures). No task consequence.
- **G2 XF-6 RED (undefined branch, all six policies).** The new "held unpaid: nothing is paid or charged now" tier (APTC grace month ≥ 2) yields `result 0.0`, but the decision tools record a final outcome and their remark enum has no pended value; the rule does not say whether a held service is written at all or with which remark. Probe: APTC account in grace month 2 → frame 0.00 with no defined remark. No task consequence.
- **G3 XF-8 RED (sibling overwrites).** The six scoped overwrites of vision_evt_eligibility_timely_filing s2 each say "only for a [frame order / spectacle-lens order / routine eye exam / out-of-network spectacle-lens receipt / out-of-network contact-lens receipt / contact-lens fitting]; every other service remains under the general eligibility rule" — none names its five siblings, so each overwrite's own text puts the siblings' services back under the base sentence the siblings retire (the defect class closed for the frequency overwrites in revision_2). No figure in either task changes, but the rendered KB carries six mutually contradicting scope statements.
- Factor floors unchanged from revision_3: lens 0 method (E2), OON lens 2 survivors, OON contacts 1, fitting 3; no real cross-difficulty factor in either task.

### correction and post-reveal notes (revision_4)
- Correction to revision_3 E1(a): its demonstration used an exchange APTC account funding a vision enrollment. Vision variants admit only the individual and group markets (`entry_gate.markets`), and billing_agg_multi_holding funds exchange enrollments only by Exchange SADP and individual enrollments only by individual-market arrangements, so no vision enrollment can sit on an APTC account; that half of E1 rested on a state the charters cannot produce. E1(b) (terminated enrollment treated as eligible) was valid and is now closed. The revision_3 text is left as written.
- Consequence for G2 (post-reveal refinement, prompted by design_rationale's own note and verified in billing.yaml/vision.yaml): the "held … second or a later grace month of an account receiving advance premium tax credit" tier is unreachable for any vision service — a dead tier in all six eligibility ladders — and its branch is undefined if reached. G2 stands as RED under both readings (XF-6 undefined branch; dead tier).
- design_rationale states that no honest billing read can bear weight on a vision amount in this blueprint and that the drawn factor counts cannot be met with real ladders; this audit records the consequence only (E2, E4–E6 open, factor floors unmet) and does not arrange a fix.

## closing_checklist (revision_4)
- revision_4 appended to all three files; older text untouched.
- Coverage/scope/tools/uuid8s/trees: unchanged, PASS. Unique solution: blind = GT in both tasks.
- Factors: NOT closed (E2, E4, E5, E6 open; lens 0 method; OON lens, OON contacts, fitting below 4; no real cross-difficulty factor). Charter: G1, G2, G3 new; E1 partly closed, E3 closed.
- Gates: round-4 snapshot 7/7 OK.

VERDICT revision_4: task0=RED task1=RED charter=E2,E4,E5,E6,G1,G2,G3

## revision_5

### charter_global_frozen (revision_5)
- Gate protocol: worklog tail `REWORK round 5 claims: G1,G2,G3,E2,E4,E5,E6` / `REWORK round 5: gates 7/7 green` (three earlier round-5 requests were answered BLOCKED with nothing written). `snapshot.sh vision_member_services 5` at 2026-10-19T17:09:07 — 7/7 OK; views r5/task_0.json sha256=043e18d1211b43e6a8101a3d0ee456748d8eaef548cc18771ee1892b2ef7329f, r5/task_1.json sha256=fbcb30b6a9b4e4cec2a54f5b023944f496c3eb5c8cf9d9e2d8a6b7620b81259c; `vision.extended.yaml` sha256=ac6adc1508d4f9dea91835ff775d4fea6cff059641f389840a6510ea3eeb2eaa; `task_tools.py` sha256=1ef0874b9f5ca78eab9e34f263ee235e6be5b0b3206220c8846c3a20e10f7778 — both changed, every section re-derived.
- Frozen 2026-10-19T17:15, before any round-5 GT was read. Base copy byte-identical. Probes: ev.py (ROUND=5), probe5.py.
- Coordinator context applied: the listed vision-benefit-manager features are treated as real industry features (implementation judged); the reworker's own additions (record-decided election outcome, OON specialty-lens and first-lens supplements, and everything else) judged strictly.

### policy_conflict_scan (revision_5)
| policy | tool (owner) | computes | prerequisites |
| --- | --- | --- | --- |
| vision_ext_exam_plan_payment | decide_exam_service_5f5caac3 (agent) | plan_paid | [] |
| vision_ext_lens_member_share | decide_lens_order_308134ce (agent) | member_paid | exam (l_exam) |
| vision_ext_frame_member_share | decide_frame_order_646cd942 (agent) | member_paid | lens (f_pair), exam (f_exam) |
| vision_ext_contacts_in_lieu_election | record_contacts_election_3e86a553 (user) | member_paid | frame (k_ppct), exam (k_epct) |
| vision_ext_oon_contacts_reimbursement | file_oon_contacts_claim_522b92fb (user) | plan_paid | [] |
| vision_ext_fitting_member_share | decide_contact_fitting_9468302b (agent) | member_paid | OON contacts (x_tie) |
The OON-lens policy and its tool are gone. Every policy now selects "the service that carries no remark yet, or … the latest received … denied as not eligible" and carries `eligibility_binder` (billing transactions read: binder payment, return). Trigger rule: tools only update vision_claims rows (triggers []), PASS. uuid8s independent (new 3e86a553). Docstrings: no example values, no ordering words.
**Overlap (H2):** the election rule selects "the enrollment's contact-lens service" of any channel and states the out-of-network outcome ("out of network the member pays the provider the whole charge"), while the OON-contacts rule settles "the enrollment's out-of-network contact-lens service" — both policies (and both user tools) settle the same out-of-network contact-lens row.

### rule_compute_equivalence (revision_5)
Mechanical sweep: quotes verbatim, bindings ⇄ bases, baseline sentences, prerequisite and replaced_by texts — PASS. Branch defects: H3, H4, H9, H10 below.

### prerequisite_graph / sentences (revision_5)
Edges: lens→exam, frame→lens, frame→exam, election→frame, election→exam, fitting→OON contacts; all state form ("… still stands denied as not eligible"), verbatim, ordering connective, acyclic, gates are real bindings. State-form resolver uniqueness fails for fitting→OON contacts (H2: the election write also lifts the out-of-network row out of DENIED_NOT_ELIGIBLE).

### override_declarations (revision_5)
Declared: exam and fitting over in_network s1; lens over in_network s3 (lens coverage); frame over in_network s4 (frame benefit); election over frequency s4 (contacts after paid glasses → DENIED_CONTACTS_IN_LIEU at the in-lieu rate); OON contacts over OON s1. **Not declared and departed from:** vision_evt_frequency s1–s3 and s5 (no exam, lens, frame or contacts frequency test anywhere — H3); vision_evt_in_network_benefits s6 / vision_evt_medically_necessary_contacts s3 (not-covered plans — H4). The binder tier follows base vision_activation_binder ("becomes active on its coverage effective date once the binder premium has been received, retroactively …") — no conflict.

### factor_ladders (revision_5)
| policy | factors (label) | judgment |
| --- | --- | --- |
| exam | eligibility_binder (m, billing), scheduled_exam_fee, new_patient_ratio, pediatric_fee_ratio, child_exam_copay, lens_evaluation_addon | new-patient ratio real (new vs established exam codes); pediatric ratio observation (unchanged); evaluation add-on approved feature but double-pays with the fitting service (H8) |
| lens | eligibility_binder (m), lens_type_copay, anti_reflective_copay, light_control_copay, child_materials_copay, exam_eyewear_lens_credit | option-copay tiers approved; exam credit accepted (same class as the revision_2 exam-and-eyewear allowance) |
| frame | eligibility_binder (m), allowance_channel, overage_rate, children_frame_credit, exam_eyewear_credit, complete_pair_credit | children's frame allowance approved; complete_pair_credit invented (H7) |
| election | eligibility_binder (m), in_lieu_basis (m), channel_in_lieu_rate, exam_in_lieu_rate, additional_pair_rate | approved features; tool/act defect H1 |
| OON contacts | eligibility_binder (m), certified_reason_amount, specialty_lens_supplement, first_lens_supplement | dead tier H5; supplements invented H6 |
| fitting | eligibility_binder (m), tied_fitting_allowance, new_wearer_allowance, fit_cost_rule (m) | PASS |
eligibility_binder: baseline `'record'` ("the enrollment's own status and dates decide") is the literal application of base eligibility s1 to the enrollment record — an honest standard method (the round-3/4 straw-man ground of E2 is gone); tiers late / binder-retro / record. Method-shape all-pairs: binder vs record PASS (the record tier adds the status/date test and the full-charge outcome); late vs either PASS (constant vs formula; neither other tier is 0 across its domain). R5-O1: its tiers still choose deny vs pay over the benefit formula (an eligibility gate); not RED on the method-shape test. in_lieu_basis: in-lieu (charge × (1 − rate)) / MN (copay) / elective (copay + MX(charge − allowance)) — all pairs PASS. fit_cost_rule: contracted-less-allowance / contracted / benefit — PASS. Factor independence: no factor reads another factor's binding — PASS.

### findings (revision_5)
Status of revision_4 findings: E2 closed (grace read and paid-through baseline removed; binder baseline honest); E4 closed (no under-six tier remains); E5 closed (exam_continuity removed); E6 closed (OON-lens policy removed); G1 closed (record tier pays an active enrollment whatever the paid-through date); G2 closed (no held tier); G3 closed (no eligibility overwrites remain).

New (RED per the XF rule):
- **H1 SOURCE-CHAIN RED (realism of the customer-owned write).** record_contacts_election_3e86a553: "The member records their own contacts-in-lieu election … the contact-lens order … receives the outcome remark that matches the election and the amount the member pays", with remark and amount "as stated to the member by the agent"; the election rule decides the outcome entirely from the records (glasses paid earlier in the period → DENIED_CONTACTS_IN_LIEU at the in-lieu rate; else MN or elective). The member chooses nothing, and the write records Cascade's adjudication — including a denial remark — on the member's own claim. A contacts-in-lieu election is a member's choice of which materials benefit to use; recording the carrier's denial outcome is not a customer act. Task 0 bears it (root).
- **H2 SOURCE-POLICY RED (two policies, two user writes on one row).** Election rule s0/s3 settles any contact-lens service including out of network ("out of network the member pays the provider the whole charge"); OON-contacts rule settles the same out-of-network row; the fitting's state-form prerequisite ("no contact-lens order … still stands denied as not eligible") is lifted by either write. The election's out-of-network remark is undefined (XF-6). Task 1 consequence (see 1.md).
- **H3 SOURCE-POLICY RED (dropped frequency, exam/lens/frame/election/OON contacts).** No rule states and no compute tests the last paid service of the kind; base vision_evt_frequency s1–s3, s5 stay in force. Probes (task-0 world on an enrollment active since 2024): lens 2026-09-08 with a paid lens 2026-02-10 in the same period → rule 210.00 vs base DENIED_FREQUENCY 336.00; frame with a paid frame 2025-10-10 (24-month, benefit-year plan) → 125.00 vs base 196.00. No task consequence (new enrollments, no history).
- **H4 SOURCE-POLICY RED (C2/D1 regression: not-covered plans).** Exam Plus: lens 0.00 vs base 294.00 (70 % of 420.00); frame 200.00 vs 171.50; election 190.00 vs 133.00; OON contacts reimburses 115.00 (supplements on an amount of 0.00) vs base not covered 0.00. No task consequence (Select 150).
- **H5 SOURCE-FACTOR RED (D5 regression, dead tier).** certified_reason_amount "plan covers no medically necessary contact lenses → 0.00" is reachable only on Exam Plus, whose oon_contacts_elective_reimbursement is also 0.00 — two tiers, one outcome. Task 1 bears the factor.
- **H6 SOURCE-FACTOR RED (realism, invented, not coordinator-approved).** specialty_lens_supplement (+90.00 / +40.00 for medically necessary contacts after a specialty / standard fitting) and first_lens_supplement (+25.00 / +10.00 for a first-time wearer) on the out-of-network contact-lens reimbursement: out-of-network contact-lens reimbursement is a fixed schedule amount (elective vs medically necessary); no carrier raises it by the kind of fitting performed or by first-time wear. Task 1 bears both.
- **H7 SOURCE-FACTOR RED (realism, invented).** Frame complete_pair_credit: the frame allowance rises by 15.00 when the same-claim lenses are paid under the benefit and by 5.00 when they were bought outside it; frame allowances do not vary with the lens adjudication of the claim (the additional-pair discount the coordinator approved is a different feature — a discount on a second pair). Task 0 bears it (110.00 vs 125.00).
- **H8 SOURCE-FACTOR RED (implementation of an approved feature: double payment).** lens_evaluation_addon pays a contact-lens evaluation add-on with the routine exam whenever contact lenses are ordered under the same agreement within 30 days, while the fitting rule pays the separately billed "contact-lens fitting and evaluation" service; no sentence excludes the add-on when a fitting is billed, so a visit with exam + fitting + contacts pays the evaluation twice. No task world has both (task 0 has no fitting, task 1 no exam).
- **H9 XF-6/7 RED (first-match / latest reads).** Exam new-patient test reads the latest paid exam under the agreement and fails when that one is dated after the exam (rule: "dated on or before … less than thirty-six months"); exam add-on reads the latest contacts order under the agreement (probe: a second order 52 days later removes the add-on, 125.63 vs 150.63); lens, frame, election and OON in-lieu tests read only the latest paid contacts / lens / frame; fitting tie reads the latest paid contacts overall (in-window order missed when a later one exists); fitting new-wearer test is restricted to the same fitting kind (rule: "no contact-lens fitting … under the same provider agreement"); OON specialty-fitting date prefers a private-practice fitting regardless of date; "the patient" reads (new-patient, new-wearer, first-lens) are enrollment-scoped. No task consequence.
- **H10 XF-5 RED (lens out of network).** Under the lens benefit an out-of-network lens order yields member_paid 0.00 (probe: 0.00 vs the member's receipt less the out-of-network progressive amount, 370.00); the rule says only "out of network the plan reimburses no lens options and no copay is taken". No task consequence.
Observations: R5-O1 eligibility_binder is a deny/pay gate (passes the method-shape test). R5-O2 both worlds hold the enrollment in `applied` 25 and 18 days after an in-time binder (system activation unposted) — the coordinator's logged world design; base describes the activation as automatic. R5-O3 pediatric fee ratio unproven either way. R5-O4 contacts after paid glasses denied in lieu is the reverse of base s3's direction; declared by the scoped overwrite of s4.

## closing_checklist (revision_5)
- revision_5 appended to all three files; older text untouched.
- Coverage: task 0 = exam, lens, frame, election; task 1 = OON contacts, fitting — all six policies, scopes disjoint; tools ⇄ GT closed; uuid8s independent.
- Trees: task 0 n=3 / 5 value_input / owner=user root (H1 RED); task 1 n=1 / 1 / owner=user (H2 RED); acyclic.
- Unique solution: blind = GT on every write; task 1 carries the H2 second write.
- Factors: task 0 in bounds after striking H7 (frame 5); task 1 OON contacts below bounds (H5, H6). Charter: H3, H4, H8, H9, H10 without task consequence.
- Gates: round-5 snapshot 7/7 OK.

VERDICT revision_5: task0=RED task1=RED charter=H1,H2,H3,H4,H5,H6,H7,H8,H9,H10

## revision_6

### charter_global_frozen (revision_6)
- Gate protocol: worklog tail `REWORK round 6 claims: H1,…,H10` / `REWORK round 6: gates 7/7 green`; `snapshot.sh vision_member_services 6` at 2026-10-19T18:21:26 — 7/7 OK; views r6/task_0.json sha256=5ddc3658eeffc17f069f26d4832e9d61e24378d9bc197ee510bfa9e0281ab04e, r6/task_1.json sha256=a775012035e788475a86a6b9e67feec655dd6f97524a303e827bc8013ce78dfc; `vision.extended.yaml` sha256=adce16f04f6d0c4e5a1f711b1d7c24082740774e10df987a74516df6951e85db; `task_tools.py` sha256=4d7fc35ddab88b6b94affe6b4d94e5a595123453707ad012a530e78f73605325 — all changed, all sections re-derived.
- Frozen 2026-10-19T18:26, before any round-6 GT was read. Base copy byte-identical. Probes: ev.py (ROUND=6), probe6.py.
- Coordinator DECISION applied: the customer-owned write is the member's combined out-of-network claim for one visit; real features for it are OON schedules by lens type and exam type, the children's frame allowance, contacts elective vs medically necessary, contacts-in-lieu and binder eligibility; everything else judged strictly.

### policy_conflict_scan (revision_6)
| policy | tool (owner) | computes | prerequisites (declared) |
| --- | --- | --- | --- |
| exam_plan_payment | decide_exam_service_5f5caac3 (agent) | plan_paid | [] |
| lens_member_share | decide_lens_order_308134ce (agent) | member_paid | exam |
| contacts_member_share | decide_contacts_order_55f7002b (agent) | member_paid | lens, OON eyeglass claim, exam |
| oon_eyeglass_claim | file_oon_eyeglass_claim_2513bc70 (user) | plan_paid | exam |
| oon_contact_lens_claim | file_oon_contact_lens_claim_04f2b50e (user) | plan_paid | [] |
| fitting_member_share | decide_contact_fitting_9468302b (agent) | member_paid | OON contact-lens claim |
In-network policies select participating-location services only; the two OON claims are split by "carries a contact-lens fitting", and each tool returns a pointer to "the other claim step" for the wrong kind of claim (routes between the two user tools; judges no prerequisite). Election and frame policies removed. Trigger rule PASS (vision_claims updates only). uuid8s independent (new 55f7002b, 2513bc70, 04f2b50e).

### rule_compute_equivalence (revision_6)
Sweep: quotes verbatim, bindings ⇄ bases, baseline sentences, prerequisite and replaced_by texts — PASS. Frequency now stated and computed in every policy (benefit-year periods / whole months, child lens frequency); not-covered plans handled in lens, contacts, fitting and both OON claims; exam evaluation add-on excludes a fitting billed in the window. Branch defects: J2, J3, J10.

### prerequisite_graph / sentences (revision_6)
State form, verbatim, acyclic. Defect J1: the lens→exam and contacts→exam conditions ("every routine eye exam service of the enrollment dated on or before … carries a remark other than DENIED_NOT_ELIGIBLE") include out-of-network exam lines, which the declared resolver decide_exam_service cannot decide (the exam rule settles participating exams only); only the member's out-of-network claim filing lifts them.

### override_declarations (revision_6)
Declared: in_network s1 (exam, fitting), s3 (lens); OON s1 (both OON claims); frequency s4 (contacts in lieu after glasses); frequency s5 (current enrollment only) in all six, each naming its five siblings — PASS for XF-8. Not declared: the reversal semantics "when that latest service was reversed the benefit counts as available" against base s4 ("a reversed service does not count") and the measure (latest unreversed paid service) — J2 (the revision_3 scoped reversal overwrite is gone).

### factor_ladders (revision_6)
| policy | factors | judgment |
| --- | --- | --- |
| exam | eligibility_binder (m, billing), scheduled_exam_fee, new_patient_ratio, pediatric_fee_ratio, child_exam_copay, lens_evaluation_addon | child copay split by location type invented (J4); pediatric ratio observation |
| lens | eligibility_binder (m), lens_type_copay, anti_reflective_copay, light_control_copay, child_materials_copay, exam_eyewear_lens_credit | child materials split by location type invented (J4) |
| contacts | eligibility_binder (m), in_lieu_basis (m), exam_in_lieu_part, additional_pair_part, new_wearer_part | new-wearer discount on contact-lens materials invented (J5) |
| OON eyeglass | eligibility_binder (m), line_frequency (m), oon_lens_schedule, children_oon_frame, oon_exam_eyewear_allowance, oon_glasses_in_lieu (m) | J6 (exam-eyewear allowance on OON reimbursement), J7 (line_frequency baseline = no frequency), J8 (lens-schedule dead tier) |
| OON contact-lens | eligibility_binder (m), oon_fitting_schedule, certified_reason_amount, oon_contacts_in_lieu (m) | J8 (two dead tiers) |
| fitting | eligibility_binder (m), tied_fitting_allowance, new_wearer_allowance, fit_cost_rule (m) | PASS |
Method-shape all-pairs: eligibility_binder (late / binder / record) PASS as revision_5; in_lieu_basis PASS; fit_cost_rule PASS; line_frequency (BY deny / months deny / available) PASS on shape; oon_glasses_in_lieu and oon_contacts_in_lieu (contacts dropped / glasses dropped / larger kept / all kept) PASS (each adds a different selection; "larger" adds a max pick). Factor independence PASS.
Survivors: exam 5, lens 5, contacts 4, OON eyeglass 4 (after J6, J7), OON contact-lens 2 with 0 parameters (after J8) — out of bounds; fitting 4. Cross-difficulty: eligibility_binder (billing binder/return rows) in every policy.

### findings (revision_6)
Status of revision_5 findings: H1 closed (election removed; the customer-owned write is now the member's out-of-network claim — R6-O1); H2 closed; H3 closed; H4 closed; H5 open (moved to the OON contact-lens claim — J8); H6 closed; H7 closed (frame policy removed); H8 closed; H9 partly open (J3); H10 closed (in-network lens rule no longer settles out-of-network lenses).

New / residual (RED per the XF rule):
- **J1 SOURCE-POLICY + SOURCE-CHAIN RED (task 0).** The lens's and contacts' exam conditions cover the out-of-network exam line, resolvable only by the member's out-of-network eyeglass filing; the declared edges name decide_exam_service, and no edge lens ← OON eyeglass claim is declared. The order is load-bearing: with the lens decided before the filing, the filing's lens line is frequency-denied (benefit period of the paid in-network lens) and the reimbursement is 105.00 instead of 150.00.
- **J2 SOURCE-POLICY RED (charter; C4/D2 regression).** Every frequency sentence: "the last paid service is the latest service of the kind … and when that latest service was reversed the benefit counts as available"; base s4 and the measure count the latest unreversed paid service and are not overwritten. Probe (duplicate paid lenses 2027-01-02, one reversed, then the 2027-01-04 order): 262.00 or 368.00 depending on row order (base: 368.00, DENIED_FREQUENCY); compute also blanks per remark, so a reversed latest PAID service falls back to an older PAID_OON one where the rule says "available".
- **J3 XF-6/7 RED (H9 residual).** In-lieu tests read only the latest paid service of the other kind: lens (latest contacts — probe: paid contacts 2027-01-02 plus later 2027-03-01 → 262.00 vs rule 368.00), contacts (latest lens / frame), OON eyeglass and OON contact-lens claims (latest lens / frame / contacts before the claim).
- **J4 SOURCE-FACTOR RED (realism, invented split).** child_exam_copay and child_materials_copay split the children's copay reduction by location type (½ at an independent practice, ¾ at a retail chain); a children's copay reduction is not varied by location type in carrier schedules, and the split restores a third tier after the senior tier was struck. Task 0 bears both (exam copay 7.50, materials copay 15.00).
- **J5 SOURCE-FACTOR RED (realism).** contacts new_wearer_part: a first-time-wearer discount on contact-lens materials bought outside the benefit; new-wearer pricing exists for fittings (kept in the fitting rule), not as a materials discount. Task 0 bears it (5 %).
- **J6 SOURCE-FACTOR RED (realism, E5 class).** oon_exam_eyewear_allowance raises the out-of-network eyeglass reimbursement when an in-network exam was paid on the same day or within twelve months; out-of-network eyewear reimbursement is a fixed schedule amount and is not on the coordinator's list. Task 0 bears it (10.00).
- **J7 SOURCE-FACTOR RED (dishonest baseline).** line_frequency baseline `g_freq: ''` — the standard method applies no frequency limit at all, while base vision_evt_oon_reimbursement s2 ("frequency limits and contacts-in-lieu apply exactly as in network") stays in force; no reader of the charter would reimburse a line without a frequency test. Task 0 bears it (200.00 vs 150.00).
- **J8 SOURCE-FACTOR RED (dead tiers; H5 regression).** OON contact-lens certified_reason_amount "a plan without a contacts benefit, or whose medically necessary contact lenses are not covered → 0.00" and oon_fitting_schedule "a plan without a contacts benefit → 0.00": reachable only on Exam Plus, where every other tier's contact-lens amount is also 0.00 and the fitting is reimbursed only with a reimbursed contact-lens line; OON eyeglass oon_lens_schedule "a plan without a lens benefit → 0.00": every lens-type amount is 0.00 on Exam Plus. Task 1 bears the first two → the OON contact-lens claim keeps eligibility_binder and oon_contacts_in_lieu only (0 parameter factors).
- **J10 XF-5 RED (OON contact-lens in-lieu comparison).** "only the larger of the contact-lens part and the glasses part" with "the fitting following the contact-lens line": the rule does not say whether the fitting counts in the contact-lens part; compute compares the contact-lens line alone. Second reading where contacts 100.00 + fitting 100.00 face glasses 150.00. No task consequence.
Observations: R6-O1 the member's filing tools record denial remarks dictated by the agent (coordinator-accepted act). R6-O2 eligibility_binder is a deny/pay gate (passes method shape). R6-O3 enrollments held `applied` after an in-time binder (coordinator world design). R6-O4 pediatric fee ratio unproven. R6-O5 task 1's in-network refit receives a second tied fitting allowance for contacts already reimbursed with an out-of-network fitting; base "a fitting … is not limited separately" admits it.

## closing_checklist (revision_6)
- revision_6 appended; older text untouched. Coverage: task 0 = exam, OON eyeglass claim, lens, contacts; task 1 = OON contact-lens claim, fitting — six policies, disjoint; tools ⇄ GT closed.
- Trees: task 0 n=3, owner=user filing, but an undeclared load-bearing edge (J1) and a false order-uniqueness assertion; task 1 n=1 PASS.
- Unique solution: blind = GT in both tasks.
- Factors: task 0 RED (J4–J7 bear weight); task 1 RED (J8, out of bounds). Charter: J2, J3, J10 without task consequence.
- Gates: round-6 snapshot 7/7 OK.

VERDICT revision_6: task0=RED task1=RED charter=J1,J2,J3,J4,J5,J6,J7,J8,J10

## revision_7

### charter_global_frozen (revision_7)
- Gate protocol: two round-7 requests were answered BLOCKED (worklog still on round 6). Now: worklog tail `REWORK round 7 claims: J1,J2,J3,J4,J5,J6,J7,J8,J10` / `REWORK round 7: gates 7/7 green`; `snapshot.sh vision_member_services 7` at 2026-10-20T03:46:56 — 7/7 OK; views r7/task_0.json sha256=9a63463c73758c904a880e35702cb0a5e87ec0e0ad33f171ce0e37c9b1609dfc, r7/task_1.json sha256=d92b4e8e751544e6ddeed2b9324b9e5aa34d3f5ad63f9d91f3a967d558a75dc2; `vision.extended.yaml` sha256=a2a541263417fb08c7941b25273340b58c21aca87356e5dfb057981e9562d893; `task_tools.py` sha256=6eb42bfe63e5ec580c3926806c5cce65d5647ef8f131f5db9b6f0275dd78f532 — all changed, re-derived in full.
- Frozen 2026-10-20T03:52, before any round-7 GT was read. Base copy byte-identical. Probes: ev.py (ROUND=7), probe7.py.
- Coordinator DECISIONs applied (per-visit / per-order settlement; approved ladders listed in the brief; 3-tier channel schedules because the agent reprocesses denied out-of-network lines); everything else judged strictly.

### policy_conflict_scan (revision_7)
| policy | tool (owner) | computes | declared prerequisites |
| --- | --- | --- | --- |
| exam_visit_payment | decide_exam_visit_80d2e33d (agent) | plan_paid | [] |
| eyeglasses_order | decide_eyeglasses_order_e7a7f40f (agent) | member_paid | exam visit, OON glasses claim |
| contacts_order | decide_contacts_order_55f7002b (agent) | member_paid | eyeglasses, OON glasses claim |
| oon_glasses_claim | file_oon_eyeglass_claim_2513bc70 (user) | plan_paid | exam visit |
| oon_contacts_claim | file_oon_contact_lens_claim_04f2b50e (user) | plan_paid | [] |
| refit_member_share | decide_contact_fitting_9468302b (agent) | member_paid | OON contacts claim |
Claims are settled whole (exam + fitting; lenses + frame; contacts + fitting; stand-alone fitting; new OON claim split by which part prevails). The six tool bodies are identical (record every open line of a claim number, book one amount on the first non-denied line); the docstrings separate them by claim kind. Trigger rule PASS. uuid8s independent (new 80d2e33d, e7a7f40f). No example values in docstrings.

### rule_compute_equivalence (revision_7)
Sweep PASS (quotes, bindings ⇄ bases, baseline sentences, prerequisite and replaced_by texts). Frequency now order-independent ("a latest service in a later benefit period blocks nothing"; months "in either direction") and reversal handled per date; in-lieu counts every paid service of the other kind in the period. Defects: K1 (reversal exclusion in compute, not in the rule, on five "latest … that stands PAID" reads), K4 (benefit period of the in-lieu test).

### prerequisite_graph / sentences (revision_7)
State form, verbatim, acyclic; new "still awaits its first decision" sentences resolve to the member's filing only (new OON lines carry an empty remark) — PASS. Order-independence of frequency removes the revision_6 hidden lens ← filing dependency (J1).

### override_declarations (revision_7)
Every policy now overwrites, scoped and sibling-named, vision_evt_frequency s2 (counting), s3 (contacts in lieu), s4 (denial and reversed services) and s5 (current enrollment); in_network s1 / s3 and OON s1 as before. PASS.

### factor_ladders (revision_7)
| policy | factors | judgment |
| --- | --- | --- |
| exam visit | eligibility_binder (m), channel_exam_fee, new_patient_ratio, pediatric_fee_ratio, fitting_type_fee, exam_copay_band | fitting_type_fee fall-through unreachable (K2); new-patient rule/compute (K1); pediatric ratio observation |
| eyeglasses | eligibility_binder (m), lens_type_copay, anti_reflective_copay, light_control_copay, materials_copay_band, exam_eyewear_lens_credit | approved / accepted |
| contacts | eligibility_binder (m), in_lieu_basis (m), additional_pair_part, tied_fitting_allowance, new_wearer_allowance, fit_cost_rule (m) | tie never sees the order's own contacts (K6) |
| OON glasses | eligibility_binder (m), oon_lens_schedule, children_oon_frame, oon_fitting_schedule, oon_glasses_in_lieu (m) | oon_fitting_schedule fall-through unreachable (K2) |
| OON contacts | eligibility_binder (m), oon_fitting_schedule, reason_channel_amount, oon_contacts_in_lieu (m) | K2; reason_channel_amount first tier unreachable (K3) |
| refit | eligibility_binder (m), tied_fitting_allowance, new_wearer_allowance, fit_cost_rule (m) | PASS |
Method-shape all-pairs: as revision_6 for eligibility_binder, in_lieu_basis, fit_cost_rule and both in-lieu factors — PASS. Factor independence PASS. Survivors: exam visit 5, eyeglasses 6, contacts 6, OON glasses 4, OON contacts 2 (0 parameter) — out of bounds, refit 4.

### findings (revision_7)
Status of revision_6 findings: J1 closed; J2 closed (reversal semantics declared, duplicates on one date handled); J3 closed in the rule (count of every paid service of the other kind in the period) — implementation defect K4; J4 closed (one child ratio); J5 closed; J6 closed; J7 closed (frequency no longer a factor); J8 open in a new form (K2, K3); J10 closed (fitting counted in the contact-lens part).

New (RED per the XF rule):
- **K1 XF-5 RED (reversal exclusion only in compute; task 0 consequence).** The new-patient sentence (exam visit): "the latest routine eye exam of the patient under the same provider agreement that stands PAID or PAID_OON_REIMBURSEMENT is not dated on or before the visit and less than thirty-six whole calendar months before it"; compute (`a_np`) blanks that exam when it is the only paid exam on its date and has been reversed. Task 0's exam 246cc5f3… stands PAID (reversed by a394edc3…) under the same agreement on the visit's date: rule → established patient, plan 169.50; compute → new patient, 195.63. Same split between rule words and compute in the eyeglasses exam credit (latest PAID/PAID_OON exam), contacts additional-pair part (latest PAID/PAID_OON frame), contacts and refit tie (latest PAID/PAID_OON contacts) and contacts/refit new-wearer (latest PAID/PAID_OON fitting) — compute applies the frequency sentence's reversal rule, the sentences do not.
- **K2 SOURCE-FACTOR RED (unreachable fall-through).** fitting_type_fee (exam visit) "otherwise → exam_fee_private" and oon_fitting_schedule (both OON claims) "otherwise → oon_exam_reimbursement": a fitting line's exam_type is by definition contact_lens_fitting_standard or contact_lens_fitting_specialty (schema enum), so the fall-through — which is the baseline — is never reached; two reachable tiers each. Task 0 bears the exam and OON-glasses members, task 1 the OON-contacts member.
- **K3 SOURCE-FACTOR RED (unreachable tier).** reason_channel_amount "certified medically necessary contact lenses on a line from a participating location → the receipt in full": the rule settles "the member's new out-of-network claim … whose lines are at providers without a Cascade agreement", so no line is from a participating location. Task 1 bears it; with K2 and K3 the OON contact-lens computation keeps eligibility_binder and oon_contacts_in_lieu only.
- **K4 SOURCE-POLICY RED (two definitions of the benefit period).** Every in-lieu sentence: "its date of service falls in the same benefit period, the twelve-month period that starts on the enrollment's benefit_period_start_mmdd … ; the period is counted in whole calendar months back from the day of the decision"; compute counts with `within_months` windows back from NOW, which align with the reset day only when the decision's day of month allows. Probe (task-0 world, reset day 12-15, a paid contacts 2026-12-10 in the previous period): eyeglasses order denied in lieu, 600.00, where the benefit-period reading gives no in-lieu. No task consequence (reset day 01-01).
- **K6 SOURCE-FACTOR RED (realism: the order's own contacts never tie its fitting).** Contacts-order tie: "the latest contact-lens service of the enrollment that stands PAID or PAID_OON_REIMBURSEMENT … within tie_window_days"; the order's own contact-lens line is decided in the same write, so a fitting on a contact-lens order whose contacts are covered receives no fitting allowance. Probe (task-0 world without glasses in the period): elective contacts covered, fitting tie 0.00 → order 180.00 instead of 120.00 with the elective tie. No task consequence (task 0's contacts are denied in lieu).
Observations: R7-O1 pediatric fee ratio unproven. R7-O2 eligibility_binder deny/pay gate. R7-O3 enrollments `applied` after an in-time binder. R7-O4 the six tools share one body; the two member tools differ only by which part prevails, so filing a contact-lens claim with the glasses tool records the same lines (tool choice scored by name only). R7-O5 task 0's decoy exam (same visit billed twice, the duplicate paid on 2026-12-05 before the binder and reversed) is a plausible billing-error record.

## closing_checklist (revision_7)
- revision_7 appended; older text untouched. Coverage: task 0 = exam visit, OON glasses claim, eyeglasses, contacts order; task 1 = OON contacts claim, refit — six policies, disjoint; tools ⇄ GT closed.
- Trees: task 0 n=3 / 5 value_input / owner=user, order-independent frequency; task 1 n=1 — PASS.
- Unique solution: task 0 carries the K1 second reading (169.50 vs 195.63); task 1 = GT.
- Factors: task 0 RED (K2 members, in bounds after striking); task 1 RED (K2, K3, out of bounds). Charter: K4, K6 without task consequence.
- Gates: round-7 snapshot 7/7 OK.

VERDICT revision_7: task0=RED task1=RED charter=K1,K2,K3,K4,K6

## revision_8

### charter_global_frozen (revision_8)
- Gate protocol: worklog tail `REWORK round 8 claims: K1,K2,K3,K4,K6` / `REWORK round 8: gates 7/7 green`; `snapshot.sh vision_member_services 8` at 2026-10-20T04:31 — 7/7 OK; views r8/task_0.json sha256=9a63463c…09dfc and r8/task_1.json sha256=d92b4e8e…5dc2 (identical to r7: worlds unchanged); `task_tools.py` 6eb42bfe… unchanged (tool section carried forward on that hash); `vision.extended.yaml` sha256=8a23ce0786944e869b7fa339b1c5d881f32cc12b3fb5d9a450a38a79c8cec494 (changed → charter re-derived).
- Frozen 2026-10-20T04:32, before any round-8 GT was read. Base copy byte-identical. Mechanical sweep (quotes, bindings, baselines, prerequisite/replaced_by texts) PASS; no `within_months` read remains; prerequisite graph and overwrites as revision_7, PASS; trigger rule PASS.

### findings (revision_8)
Status of revision_7 findings:
- **K1 closed.** Every "latest … that stands PAID or PAID_OON_REIMBURSEMENT" read (new patient, exam credit, additional pair, fitting tie, new wearer, in-lieu) now states the reversal treatment the compute applies ("when that latest one is the only such service on its date and has been reversed, there is taken to be none …; of several … a reversal of one leaves that date standing"). Task 0's decoy now makes the new-patient ratio unambiguous (195.63).
- **K2 closed as defined.** fitting_type_fee and both oon_fitting_schedule ladders now end in "no fitting line → 0.00", a reachable tier (exam visits and OON claims without a fitting). The declared baseline value (the exam fee / OON exam amount) differs from the fall-through value, but on the fall-through's own domain (no fitting line) the baseline prices nothing either, so no input separates them — R8-O1.
- **K3 closed** (reason_channel_amount removed) — **but its replacement reintroduces the dead tier (L1).**
- **K4 closed.** The in-lieu sentences now define one benefit period ("the twelve-month period that starts each year on the enrollment's benefit_period_start_mmdd") and read the latest service of each kind; compute no longer uses windows from the decision date (probe: reset day 12-15, paid contacts 2026-12-10 → not in lieu, 423.00 = rule).
- **K6 closed.** The contact-lens order's fitting ties to the order's own contacts when this decision covers them (probe: no glasses in the period → tie 60.00, order 120.00).

New / regressed (RED per the XF rule):
- **L1 SOURCE-FACTOR RED (dead tier; H5/J8 regression).** OON contacts certified_reason_amount "a plan without a contacts benefit (contacts_benefit_included false, or contacts_medically_necessary_in_network not_covered) → 0.00": only Exam Plus satisfies it, and on Exam Plus oon_contacts_medically_necessary_reimbursement and oon_contacts_elective_reimbursement are both 0.00 — the tier selects the outcome every other tier selects on its whole domain. Task 1 bears the factor; struck, the OON contact-lens computation keeps eligibility_binder, oon_fitting_schedule and oon_contacts_in_lieu (3 factors, 1 parameter) — out of bounds.
Observations: R8-O1 (above). R8-O2 the in-lieu test now reads only the latest service of each kind, so a later-period service hides an earlier same-period one when an older order is reprocessed — stated in the rule and declared by the scoped overwrite of frequency s3. R8-O3–O5 as revision_7 (pediatric ratio unproven; binder gate; enrollments held `applied`).
- **L2 SOURCE-CHAIN RED (task 0, XF-13 stale proof, post-reveal).** prerequisite_closure of task 0 still states the revision_7 load "result 180.00 instead of 262.50" for skipping the eyeglasses decision; under the K6 fix the recomputation is 120.00.

## closing_checklist (revision_8)
- revision_8 appended; older text untouched. Coverage, scopes, tools, trees and acyclicity as revision_7 — PASS.
- Unique solution: blind = GT in both tasks; K1's second reading removed.
- Factors: task 0 all factors survive, in bounds; task 1 OON contact-lens computation out of bounds (L1).
- Stale proof: task 0 closure load figure (L2).
- Gates: round-8 snapshot 7/7 OK.

VERDICT revision_8: task0=RED task1=RED charter=L1,L2

## revision_9

### charter_global_frozen (revision_9)
- Gate protocol: worklog tail `REWORK round 9 claims: L1,L2` / `REWORK round 9: gates 7/7 green`; `snapshot.sh vision_member_services 9` at 2026-10-20T05:00:31 — 7/7 OK; views r9/task_0.json and r9/task_1.json byte-identical to r7/r8 (9a63463c…, d92b4e8e…); `task_tools.py` 6eb42bfe… unchanged; `vision.extended.yaml` sha256=81cf6d83f79bc9f844954db4019ab796df8f9e8d5016e18dbf4f1fcf78ae72e9 (changed → charter re-derived; a copy kept in scratch for later rounds).
- Frozen 2026-10-20T05:02, before any round-9 GT was read. Base byte-identical; sweep PASS; graph, overwrites, trigger rule PASS; all revision_7/8 probes re-run with unchanged results (K4 423.00, K6 120.00); every task figure unchanged.

### findings (revision_9)
- **L1 closed.** The OON contact-lens claim's amount factor is now contacts_basis: "glasses counted in the claim's benefit period → 0.00 (contact-lens line denied in lieu, fitting follows) / medically necessary → oon_contacts_medically_necessary_reimbursement / elective → oon_contacts_elective_reimbursement"; plans without a contacts benefit are handled by a plain gate (`c_cv`) stated in the rule's not-covered sentence. All three tiers are reachable (the first on a contacts-only OON claim after glasses in the period) and distinct on every plan with a contacts benefit; label honest; oon_contacts_in_lieu now carries contacts-held / compare / none and reads no factor binding (the comparison lives in `result`) — XF-1 PASS. OON contact-lens computation: 4 factors (2 parameter, 2 method).
- L2: post-reveal (see closing).
- **M1 SOURCE-FACTOR RED (XF-12/17 seed realism; present since revision_7, missed by this auditor in revisions 7–8).** Task 0's decoy exam V73-261204-4409 (Marquez, 2026-12-04, PAID on 2026-12-05 and reversed 2026-12-06) carries plan_paid 85.00 / member_paid 10.00 — the adult copay on the 95.00 chain fee. Priced by the exam-visit rule the same service gives 125.63 (new patient × 1.25, pediatric × 1.10, child copay 5.00; charter compute on the row alone). The row is read for its date, remark and reversal only, but it is the paid history the rule is checked against; a payment the adjudication charter cannot produce (the reversal reason is eligibility, not pricing).
Observations: R9-O1 fitting-fee ladders' declared baseline vs the "no fitting line" tier (as R8-O1). R9-O2 the in-lieu test reads only the latest service of each kind (declared). R9-O3 pediatric ratio unproven; binder gate; enrollments held `applied`; shared tool body.
- **L2 closed (post-reveal).** Task 0's closure now states 120.00 for skipping the eyeglasses decision, equal to the recomputation.

## closing_checklist (revision_9)
- revision_9 appended; older text untouched.
- Coverage: task 0 = exam visit, OON glasses claim, eyeglasses, contacts order; task 1 = OON contacts claim, refit — six policies, scopes disjoint; tools ⇄ GT closed; uuid8s independent.
- Trees: task 0 n=3 / 5 value_input / owner=user; task 1 n=1 / 1 / owner=user; acyclic, order-independent.
- Unique solution: blind = GT in both tasks.
- Factors: every computation of both tasks 4–6 factors, ≥2 parameter, ≥1 method, cross-difficulty and multi-source present, every factor bearing weight against its baseline.
- Open: M1 (task 0 seed row). Not closed until M1 is resolved; gates re-run once on the final form (round-9 snapshot 7/7 OK).

VERDICT revision_9: task0=RED task1=PASS charter=M1

## revision_10

### charter_global_frozen (revision_10)
- Gate protocol: worklog tail `REWORK round 10 claims: M1` / `REWORK round 10: gates 7/7 green`; `snapshot.sh vision_member_services 10` at 2026-10-20T05:09:32 — 7/7 OK. Seed-only round confirmed: `vision.extended.yaml` sha256=81cf6d83f79bc9f844954db4019ab796df8f9e8d5016e18dbf4f1fcf78ae72e9 (byte-identical to the revision_9 scratch copy) and `task_tools.py` sha256=6eb42bfe63e5ec580c3926806c5cce65d5647ef8f131f5db9b6f0275dd78f532 — every charter-global section of revision_9 is carried forward on those two hashes. Views: r10/task_0.json sha256=2dfefed9c19ebf8dfdbd44a5dd21c491c2ca43e965c88eae7ed9686a149682d5 (changed: two rows, below); r10/task_1.json sha256=d92b4e8e…5dc2 (unchanged).
- Frozen 2026-10-20T05:11, before any round-10 GT was read.

### seed re-pricing (revision_10, exhaustive over both worlds)
Task 0 world diff r9 → r10: decoy exam 246cc5f3… plan_paid 85.00 → 125.63, copay/member 10.00 → 5.00; reversal a394edc3… plan_paid 85.00 → 125.63.
| row | check | result |
| --- | --- | --- |
| task 0 decoy exam V73-261204-4409 (PAID 2026-12-05) | exam-visit rule on the row alone: 95.00 × 1.25 (new) × 1.10 (age 16) = 130.625 ≤ 185.00, − copay ½ × 10.00 → 125.63 / member 5.00 | equal — **M1 closed** |
| task 0 reversal of 246cc5f3… (2026-12-06) | base reversal "carries the original plan_paid" → 125.63; reason: paid while coverage not yet in force (status applied, binder unpaid on 2026-12-05) | equal |
| task 0 denied lines (exam visit -4417 on 2026-12-08; eyeglasses -4620 on 2027-01-07; contact-lens order -4630 on 2027-01-12) | DENIED_NOT_ELIGIBLE, plan 0.00, member = retail charge (185.00, 95.00; 520.00, 230.00; 150.00, 190.00) — record tier while the enrollment stands applied | consistent |
| task 0 new OON claim -4502 lines | no remark, plan 0.00, member = receipt; received 2027-01-26 (≤ 365 days) | consistent |
| task 0 billing | invoices 29.44 (= Select 150 member_children) for 2026-12 (issued at opening 2026-11-12), 2027-01 (2026-12-12 = due − 20), 2027-02 (2027-01-12); binder 29.44 by check (Direct Bill binder methods card/check) 2026-12-28 ≤ deadline 2026-12-31, regular 29.44 same day; paid through 2027-01-31; balance 3 × 29.44 − 2 × 29.44 = 29.44 | consistent |
| task 1 denied refit -5310 (2026-10-09) | DENIED_NOT_ELIGIBLE, plan 0.00, member 225.00 | consistent |
| task 1 new OON claim -5233 lines | no remark, plan 0.00, member = receipt; received 2026-10-24 (≤ 365) | consistent |
| task 1 billing | invoices 14.72 (= member_only) for 2026-09 (at opening 2026-08-18), 2026-10 (2026-09-11), 2026-11 (2026-10-12); binder 14.72 by check 2026-10-01 = deadline day, regular 14.72 same day; paid through 2026-10-31; balance 14.72 | consistent |
No other paid or reversed vision row exists in either world. No remaining seed member.

### findings (revision_10)
- M1 closed. No new defect; nothing regressed (charter and tools byte-identical; task figures re-run unchanged: 195.63 / 140.00 / 457.00 / 262.50 and 310.00 / 67.50).
Observations carried: R9-O1–O3.

## closing_checklist (revision_10 — difficulty closed)
Written after both revision_10 derivations were frozen and compared.
- Files: `0.md`, `1.md` one-to-one with tasks/0.json and tasks/1.json, `_difficulty.md` alongside; revisions 1–10 preserved; every comparison section of revision_10 carries PASS.
- Coverage and scope: the six extended policies are all claimed — task 0: vision_ext_exam_visit_payment, vision_ext_oon_glasses_claim, vision_ext_eyeglasses_order, vision_ext_contacts_order; task 1: vision_ext_oon_contacts_claim, vision_ext_refit_member_share — scopes (whole trees) pairwise disjoint; task tools ⇄ GT closed; uuid8s (80d2e33d, e7a7f40f, 55f7002b, 9468302b, 2513bc70, 04f2b50e) independently generated and frozen.
- Problem trees: task 0 — 3 prerequisite problems (exam visit, OON glasses claim, eyeglasses), 5 value_input edges ≥ 2, owner=user filing, acyclic, every edge load-bearing, frequency order-independent; task 1 — 1 prerequisite problem (OON contact-lens claim), 1 value_input edge, owner=user filing. The difficulty-wide prerequisite graph is a DAG.
- Factors: every computation declares a self-sufficient baseline (baseline.rule sentences all in the rule; definite fall-back figures 0.00 / 0.00 / 750.00 / 340.00 and 0.00 / 225.00, all ≠ gold) and 4–6 factors with ≥ 2 parameter and ≥ 1 method; ladders ≥ 3 reachable, distinct tiers stated in the rule; method tiers pass the all-pairs shape test; factor independence holds; each task has a cross-difficulty factor (eligibility_binder on seeded billing binder/return rows) and a multi-source factor; every factor bears weight on its world against its baseline; near-misses present (regular vs binder payment; reversed duplicate exam; out-of-network fitting outside the new-wearer test).
- Seeds: every paid/reversed vision row and every billing row of both worlds reproduces its charter (revision_10 seed re-pricing).
- Gates re-run on the final form: round-10 snapshot (2026-10-20T05:09:32) check_extended / check_task_tools / replay_tasks / check_solvability / check_compute / check_grounding / check_cross_fire — 7/7 OK.
- Open observations (no RED): R9-O1 fitting-fee ladders' declared baseline vs "no fitting line" tier (indistinguishable on every input); R9-O2 in-lieu reads the latest service of each kind (declared); R9-O3 pediatric fee ratio unproven, eligibility_binder a deny/pay gate, enrollments held `applied` after an in-time binder (coordinator world design), the six tools share one body.

The difficulty passes the source-layer audit: policy self-consistency PASS, problem tree PASS, factors PASS, unique solution PASS in both tasks.

VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN

## revision_11

### charter_global_frozen (revision_11)
- Gate protocol: worklog tail `REWORK round 11 claims: R1,R2,R3,R4,R5,R6,R7` / `REWORK round 11: gates 7/7 green`; `snapshot.sh vision_member_services 11` at 2026-10-20T05:25:22 — 7/7 OK; views r11 byte-identical to r10 (2dfefed9…, d92b4e8e…); `vision.extended.yaml` sha256=6be5efb71a3635d79566d157e3337080444f6b18f2ccc318c2833e84546252f8 and `task_tools.py` sha256=b3555bf3d59826069ca43c5e3f778257685ed848b1a74383121ba3056d3aff56 — both changed, charter and tool sections re-derived (copies kept in scratch). Rework input read: `audits/render_source/vision_member_services/render_r1.md` (7 renderer pre-scan findings).
- Frozen 2026-10-20T05:28, before any round-11 GT was read. Base byte-identical; factors and baselines unchanged since revision_9 (mechanical diff); sweep PASS (quotes, bindings, baselines, prerequisite and replaced_by texts); every parameter the compute reads is named in its rule or in the base sentence it inherits; trigger rule PASS; all revision_7–10 probes re-run unchanged (K4 423.00, K6 120.00); every task figure unchanged.
- Tools: the exam-visit tool now records only the exam line and, on a claim without contact lenses, its fitting; the fitting tool only a stand-alone fitting (scope routing, no prerequisite judged); docstrings carry no example values or ordering words; uuid8s unchanged.

### render-source items (revision_11) — each probed with a concrete case (`probe11.py`)
| item | renderer finding | now | probe | should this audit have caught it? |
| --- | --- | --- | --- | --- |
| R1 (XF-2) | contacts and refit assembly sentences named the tied / new-wearer allowances, the cost rule and an in-lieu rate the baseline lacks | contacts s14: "every discount part that applies … every fitting allowance that applies is added into one combined fitting allowance and the fitting line's share is taken as the fitting sentences state"; refit s10: "Every allowance that applies … as the sentences for its kind and location state" — generic | text check | **Yes** — XF-2 was on my list every round; I passed it on the mere presence of an ordering sentence without reading which quantities it named. |
| R2 (XF-1) | the additional-pair part was added to a rate that existed only inside in_lieu_basis | s9 defines the outside-benefit discount rate as a plain quantity (materials_discount_pct) for every outside-benefit purchase (no benefit, frequency, in lieu); s10 adds the additional-pair part to it; `k_ppct` reads no factor binding and compute applies it on all three outside paths | contacts blocked by frequency, OON frame running → 190.00 × 0.75 + fitting 60.00 = 202.50 (rule = compute) | **Yes** — my XF-1 check closed over bindings only, not over the rule's own gating sentence. |
| R3 | OON claims zeroed a fitting whose contacts got nothing; the rule said only "not limited separately" | OON glasses s11 / OON contacts s10: "A fitting line follows its claim's contact-lens line: when the contact-lens line receives no reimbursement (… frequency or missing, its amount 0.00, or … in lieu), the fitting line receives none either and carries the contact-lens line's remark" | OON claim with contacts held earlier in the period → glasses in lieu, contacts blocked, fitting 0.00 → 0.00 (rule = compute) | **Yes** — a compute branch without a rule sentence (XF-5). |
| R4 | exam-visit OON fitting priced at oon_exam_reimbursement with no rule sentence | s11 "Out of network the visit's fitting line, whatever its kind, is reimbursed at the lesser of its receipt and oon_exam_reimbursement"; s12 states it in the assembly | OON exam visit (exam 185 + standard fitting 95) reprocessed → 50.00 + 50.00 = 100.00 | **Yes** (XF-5). |
| R5 | claim-scope exclusions without compute; an exam line on a contacts claim belonged to no policy | exam visit = the claim's exam line (+ its fitting only when no contacts); eyeglasses = lens/frame lines; contacts order = contacts + fitting; refit = a fitting on a claim with neither exam nor contacts (else "settles nothing"); selection compute and tool filters match | exam visit on a claim also carrying contacts → exam line alone, 125.63; tool records only the exam line | **Yes** — a scope/compute mismatch I never probed. |
| R6 | refit's OON case lived inside the not-covered sentence and compute order contradicted it | s4 not covered → nothing reimbursed OON; s5 covered plan OON → lesser of receipt and oon_exam_reimbursement; compute checks the benefit first | Exam Plus OON stand-alone fitting 225.00 → member 225.00 (rule = compute) | **Yes** (XF-5 branch order). |
| R7 (XF-6/7) | rule "a binder payment" vs compute "latest binder" | every eligibility sentence: "the latest binder payment the funding billing account received (its latest payment with payment purpose binder) was not returned, is for at least … and was received on or before the binder deadline" | in-time binder 2026-12-28 + later binder 2026-12-29 returned → record tier → exam visit 0.00 (rule = compute) | **Yes** — a LATEST read I listed under XF-6/7 but did not probe with a second record. |
All seven items closed. No new defect found; nothing regressed.

### findings (revision_11)
- R1–R7 closed. Auditor note: all seven were catchable from the charter alone and were missed in revisions 7–10 because the sweeps were mechanical (quote presence) and the probes targeted the previously reported classes; this round's probes cover each class with a second-record or branch case.
Observations carried: R9-O1–O3.

## closing_checklist (revision_11 — difficulty closed)
- revision_11 appended to all three files; revisions 1–10 untouched; both comparison sections carry PASS.
- Coverage, scopes, tools ⇄ GT, uuid8s, trees (task 0 n=3 / 5 value_input / owner=user; task 1 n=1 / 1 / owner=user), DAG: as revision_10 — PASS; the R5 scope sentences keep each claim line in exactly one policy.
- Factors: unchanged since revision_9 and all pass (4–6 per computation, ≥ 2 parameter, ≥ 1 method, reachable distinct tiers, honest baselines, cross-difficulty and multi-source present, every factor bearing weight).
- Rule == compute: the seven render-source items are closed and probed; no new member found in the sweep.
- Seeds: unchanged since revision_10 — PASS.
- Gates re-run on the final form: round-11 snapshot 2026-10-20T05:25:22 — 7/7 OK.
- Open observations (no RED): R9-O1–O3.

VERDICT revision_11: task0=PASS task1=PASS charter=CLEAN

## revision_12

### charter_global_frozen (revision_12)
- Gate protocol: worklog tail `REWORK round 12 claims: R2-1,R2-2` / `REWORK round 12: gates 7/7 green`; `snapshot.sh vision_member_services 12` at 2026-10-20T05:35:27 — 7/7 OK; views r12 byte-identical to r10/r11; `task_tools.py` b3555bf3… unchanged (tool section carried forward); `vision.extended.yaml` sha256=3bff9ec767dbe5e90590ed689476ccf89fa96895a09ed6af611dcd6d60a2f866 (changed). Rework input read: `audits/render_source/vision_member_services/render_r2.md`.
- Frozen 2026-10-20T05:37, before any round-12 GT was read. Mechanical diff against the revision_11 copy: no compute, factor, ladder, baseline value, overwrite or prerequisite changed; changes are baseline.rule sentences, compute_basis attributions and one refit sentence split (listed below). Sweep PASS; every task figure re-run unchanged.

### render-source items (revision_12)
| item | change | probe | result |
| --- | --- | --- | --- |
| R2-1 | OON glasses and OON contact-lens baseline.rule now carry "A fitting line follows its claim's contact-lens line: when the contact-lens line receives no reimbursement (its benefit blocked by frequency or missing, its amount 0.00, or the line left out in lieu), the fitting line receives none either …"; compute_basis attributes it to `result` (no longer to g_lieu / c_lieu) | task-1 world, prior paid contacts 2026-09-05 (contacts blocked), every factor at baseline except eligibility: contacts-only claim → 0.00; claim with glasses → lenses 35.00 + frame 70.00, contacts 0.00, fitting 0.00 = 105.00 (both claim rules); unblocked control → 105.00 + 50.00 + 105.00 = 260.00 | baseline.rule = baseline compute — **closed** |
| R2-2 | contacts-order baseline.rule now carries "Contact lenses bought outside the benefit at a participating location (on a plan without the benefit, blocked by frequency, or left out in lieu) are bought at their retail charge less the outside-benefit discount rate, which is materials_discount_pct percent", attributed to `result` | baseline computation of an outside-benefit order now reaches a figure (190.00 × 0.80 at baseline) | **closed** |
| reworker sweep | every result behaviour stated in baseline.rule and attributed to result; every quantity baseline.rule uses defined there | scratch sweep: every compute_basis sentence of every non-factor binding is in baseline.rule except (a) the filing-limit bindings (a_lim, b_lim, k_lim, x_lim) and (b) the contacts order's latest lens / frame selections (k_yl…, k_yf…) — each used only by factor bindings (eligibility_binder's late tier; in_lieu_basis and the tie's own-contacts test), never by the baseline computation; the exam visit's OON-fitting sentence is now in baseline.rule and attributed to result | **holds** |
Should this audit have caught R2-1/R2-2? R2-2 yes (a baseline.rule quantity without its definition — the "baseline self-sufficient" test); R2-1 was created by the round-11 fix, which revision_11 checked against the full rule but not against baseline.rule — a miss.

### findings (revision_12)
- R2-1, R2-2 closed. No new defect; nothing regressed.
Observations: R12-O1 the tie factor's own-contacts test reads the same record fact as in_lieu_basis (plain selections, no factor binding read); single-factor substitution of in_lieu_basis therefore mixes the two (task 0's 180.00 sensitivity figure). R9-O1–O3 carried.

## closing_checklist (revision_12 — difficulty closed)
- revision_12 appended; older text untouched; both comparisons PASS.
- Coverage, scopes, tools ⇄ GT, uuid8s, trees, DAG, factors, seeds: unchanged since revision_11 — PASS.
- Baseline self-sufficiency: every quantity a baseline.rule uses is defined in it and every result behaviour it relies on is stated in it (R2-1, R2-2 closed; sweep above).
- Gates re-run on the final form: round-12 snapshot 2026-10-20T05:35:27 — 7/7 OK.
- Open observations (no RED): R9-O1–O3, R12-O1.

VERDICT revision_12: task0=PASS task1=PASS charter=CLEAN

## revision_13

### charter_global_frozen (revision_13)
- Gate protocol: worklog tail `REWORK round 13 claims: KB-TRACE-1` / `REWORK round 13: gates 7/7 green`; `snapshot.sh vision_member_services 13` at 2026-10-20T05:59:55 — 7/7 OK; views r13 byte-identical to r10–r12; `vision.extended.yaml` 3bff9ec7… byte-identical to the revision_12 copy (rule, compute, factors, baselines unchanged — charter sections carried forward on that hash); `task_tools.py` sha256=2e073251237d931071b3960af1b993685c220d4d0b69ad68d38af77395c4c831 (changed: the tool-contract change under audit).
- Frozen 2026-10-20T06:00, before any round-13 GT was read.

### tool contracts (revision_13)
The composed `denied_lines` argument is replaced in all six tools by one optional remark argument per line kind the tool records: exam visit (exam_remark, fitting_remark); eyeglasses (lenses_remark, frame_remark); contact-lens order (fitting_remark, contact_lenses_remark); stand-alone fitting (fitting_remark); both member OON claims (exam_remark, fitting_remark, contact_lenses_remark, lenses_remark, frame_remark).
- Schema: every remark argument is "Enum class" listing the allowed codes with their meaning (DENIED_FREQUENCY, DENIED_CONTACTS_IN_LIEU, DENIED_NOT_COVERED, DENIED_NOT_ELIGIBLE, DENIED_TIMELY_FILING) and "an empty text when the claim carries no such line or the line is paid or reimbursed" — format and allowed values only; no example values, no claim numbers, no amounts, no ordering words, no other tool named. PASS (XF-10).
- Bodies: each tool builds its denial map from its own arguments (keys exactly the line kinds it lists), keeps its revision_11 line-scope filter (exam visit: exam + fitting only without contacts; eyeglasses: lenses/frame; contacts order: contacts/fitting; stand-alone fitting: fitting on a claim with neither exam nor contacts; member claims: every open line), and writes every recorded line with `ctx.update` in its own body; no prerequisite is judged. PASS.
- Each argument is now a single enumerated value with a verbatim source in the charter (the remark codes named in the rules), which closes the post-publication traceability finding (composed text with no verbatim source).
- Action binding and uuid8s unchanged. Trigger rule PASS.

### findings (revision_13)
- KB-TRACE-1 closed as a contract change; rule, compute and worlds unchanged (hash-verified). Gold-argument check post-reveal below.

## closing_checklist (revision_13 — difficulty closed)
- revision_13 appended; older text untouched; both comparisons PASS (gold arguments equal the blind derivation under the new contracts, each remark argument single-valued and derivable from a rule sentence).
- Charter, worlds, trees, factors, seeds: unchanged since revision_12 (hash-verified) — PASS.
- Tool contracts: enumerated per-line remark arguments, schema lists allowed codes only, no answer leaked, bodies write their own lines, uuid8s unchanged — PASS.
- Gates re-run on the final form: round-13 snapshot 2026-10-20T05:59:55 — 7/7 OK.
- Open observations (no RED): R9-O1–O3, R12-O1.

VERDICT revision_13: task0=PASS task1=PASS charter=CLEAN

## revision_14

### charter_global_frozen (revision_14)
- Gate protocol: worklog tail `REWORK round 14 claims: S1,S2` / `REWORK round 14: gates 7/7 green`; `snapshot.sh vision_member_services 14` at 2026-10-20T06:26:42 — 7/7 OK; views r14/task_0.json sha256=b43cd6d4558f6549432858b39b890e0da73d0a426bf028339c3f8a20d91ca372, r14/task_1.json sha256=26a95a2c013180c64d05019d7b0f233596a8755ea3b130cdc81424cc27506ff4; `vision.extended.yaml` sha256=ba150cf0f5416673deeae5e02b5e5122f90e7d65dc010f4a0c869ca42c53cde7; `task_tools.py` sha256=649138cb8694eda2afe3f898372246a7bf33f9b27f451484cadb3aceb925ca94. Rework input read: the S1 and S2 entries of `audits/policy_kb/vision_member_services/`.
- Frozen 2026-10-20T06:28, before any round-14 GT was read. Mechanical diff against the revision_12/13 copies: only the two OON claim rules changed (side-test sentence in rule and baseline, `g_own` / `c_own` bindings, the result gated on them, the "records nothing" sentence); both member tools now refuse the other side's claims; worlds changed only in three `credentialing_decision_date` values. Factors, ladders, baselines, overwrites and prerequisites unchanged; sweep PASS; every task figure re-run unchanged.

### S1 — side test of a member's new OON claim (probe14.py)
New sentence in both rules (and both baseline.rules): "which rule settles it is fixed by its receipts alone, whatever either rule's amounts: when the retail charges of its spectacle-lens and frame lines together are at least the retail charges of its contact-lens and contact-lens fitting lines together, it is settled on its glasses part under the glasses claim rule, and otherwise … under the contact-lens claim rule"; each rule "records nothing" (0.00) for the other side; compute `g_own` (lenses + frame ≥ contacts + fittings) and `c_own` (strictly greater) are exact complements.
| probe | glasses rule | contact-lens rule | tools |
| --- | --- | --- | --- |
| V73-261211-4502 (receipts 590.00 vs 220.00), after the exam visit | 140.00 | 0.00 | contacts tool first → "Not settled on its contact-lens part …", then glasses tool records 140.00; glasses tool first → records, then contacts tool finds no open line |
| same claim after the eyeglasses decision (other order) | 140.00 | 0.00 | — |
| decoy: contacts receipt raised to 700.00 (760.00 > 590.00) | 0.00 | 135.00 | — |
| tie decoy: 590.00 = 590.00 | 140.00 | 0.00 | — |
| task 1 V73-260912-5233 (300.00 vs 790.00) | 0.00 | 310.00 | glasses tool → "Not settled on its glasses part …" |
Exactly one rule claims every claim; both tools refuse the other's claims (routing on the claim's receipts, no prerequisite judged). **S1 closed.**
Should this audit have caught S1? **Yes.** From revision_7 on I evaluated both claim rules on the same claim (task 1: both returned 310.00) and noted that the two tools share one body (R7-O4), but never tested the side tests against each other with the two rules' different frame amounts.

### S2 — provider credentialing dates
World diff: 1abff9cf decision 2017-10-24 → 2026-11-01 (due 2029-11-01); ac3ca85f 2016-03-22 → 2025-05-01 (due 2028-05-01); aa5feab4 2015-04-20 → 2025-05-01 (due 2028-05-01). Each due date = decision + 36 months (provider charter: "recredential_due_date = last decision date plus this value", Vision Network cycle 36); each decision date precedes the frozen time and the agreement's services; license and malpractice dates unchanged and later than the frozen times. No vision value reads these fields. **S2 closed.**

### findings (revision_14)
- S1, S2 closed; nothing regressed.
- **N1 SOURCE-FACTOR RED (implementation of the approved children's frame allowance; charter, no task consequence).** The children's OON frame amount (children_oon_frame, oon_child_frame_reimbursement 90.00) exists only in the glasses-claim rule; the contact-lens-claim rule prices the glasses part of a child's claim with oon_frame_reimbursement ("oon_frame_reimbursement for the frame", `c_famt`) in its in-lieu comparison and when every line is reimbursed. Now that the side is fixed by receipts, the same child's frame receives 90.00 or 70.00 depending on whether the claim's contact-lens receipts exceed its glasses receipts. Probe (decoy above, Ivy 16): routed to the contact-lens rule, glasses part 50.00 + 70.00 = 120.00 < contact-lens part 135.00 → 135.00 with glasses denied in lieu; with the children's frame amount the glasses part is 140.00 and wins. A carrier's children's frame allowance does not depend on the claim's receipt mix. Present since revision_7 (masked until S1 by both rules claiming the claim); not reported before.
Observations carried: R9-O1–O3, R12-O1.

## closing_checklist (revision_14)
- revision_14 appended; older text untouched; both task comparisons PASS.
- S1 (one rule per OON claim, tools refuse the other side) and S2 (credentialing due dates) closed and probed; worlds, trees, factors, seeds otherwise unchanged; round-14 gates 7/7 OK.
- Not closed at charter level: N1 (children's OON frame amount absent from the contact-lens-claim rule) — no task consequence.
- Open observations (no RED): R9-O1–O3, R12-O1.

VERDICT revision_14: task0=PASS task1=PASS charter=N1

## revision_15

### charter_global_frozen (revision_15)
- Gate protocol: worklog tail `REWORK round 15 claims: N1` / `REWORK round 15: gates 7/7 green`; `snapshot.sh vision_member_services 15` at 2026-10-20T06:31:30 — 7/7 OK; views r15 byte-identical to r14; `task_tools.py` 649138cb… unchanged; `vision.extended.yaml` sha256=5cfe619416ed9f73c784f2f2a797c5a82111d4441e1227fe8ed868685f1681fc (changed).
- Frozen 2026-10-20T06:32, before any round-15 GT was read. Mechanical diff against the revision_14 copy: only vision_ext_oon_contacts_claim changed — its line-amount sentence now names "the frame amount for the frame", a new frame-amount sentence ("nothing on a plan whose frame_benefit_included is false, the children's out-of-network frame amount oon_child_frame_reimbursement for a patient under child_age_limit_years …, and oon_frame_reimbursement for everyone else") in rule and baseline.rule, `c_famt` implementing it, param oon_child_frame_reimbursement 90.00 added, and the scoped OON overwrite now listing "fitting, contact-lens and frame amounts". Factors, ladders, baselines of factors, prerequisites unchanged; sweep PASS; task figures re-run unchanged.

### N1 and the shared amounts of the two OON claim rules (probe15.py)
| amount | glasses-claim rule | contact-lens-claim rule |
| --- | --- | --- |
| routine exam | lesser of receipt and oon_exam_reimbursement, frequency-gated | same |
| lenses | by lens type (progressive / trifocal / bifocal / single vision), 0.00 without a lens benefit | same |
| frame | 0.00 without a frame benefit, 90.00 under 19, oon_frame_reimbursement otherwise | same (N1 fix) |
| contact lenses | 0.00 without a contacts benefit, MN 210.00 / elective amount | same (gated by the same `cv` test) |
| fitting | specialty 100.00 / standard 30.00 / none 0.00, follows the contact-lens line | same |
| in lieu | glasses held → contacts and fitting out; contacts held → glasses out; both on the claim → larger part kept (glasses on a tie) | same |
Probes on the same claim content (Ivy's V73-261211-4502 after the exam visit): contacts receipt 160.00 → glasses rule 140.00 / contact-lens rule 0.00; contacts receipt 700.00 (the revision_14 N1 decoy) → glasses rule 0.00 / contact-lens rule **140.00** (glasses part 50.00 + 90.00 = 140.00 beats 135.00; it was 135.00 under revision_14). Every line amount equal in both rules (lens 50.00, frame 90.00, contacts 105.00, fitting 30.00). Adult variant: 135.00 by whichever rule owns the claim (frame 70.00 in both). Exam Plus: 0.00 by both. **N1 closed**; no remaining amount differs between the two rules.

### findings (revision_15)
- N1 closed; nothing regressed; no new defect.
Observations carried: R9-O1–O3, R12-O1.

## closing_checklist (revision_15 — difficulty closed)
- revision_15 appended; older text untouched; both comparisons PASS.
- N1 closed: the two member-claim rules now price every shared line identically, so a claim's reimbursement does not depend on which side its receipts send it to (probes above).
- Coverage, scopes, tools ⇄ GT, uuid8s, trees, DAG, factors, baselines, seeds: as revision_14 — PASS.
- Gates re-run on the final form: round-15 snapshot 2026-10-20T06:31:30 — 7/7 OK.
- Open observations (no RED): R9-O1–O3, R12-O1.

VERDICT revision_15: task0=PASS task1=PASS charter=CLEAN

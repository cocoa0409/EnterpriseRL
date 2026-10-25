# Policy-task audit — insurance_claim_services / charter-global

## revision_1

## charter_global_frozen

- Freeze time: 2026-10-23 21:12 UTC. Auditor: independent policy auditor (erl-task-policy-audit), round 1. I did not write any of the audited artifacts.
- Hashes (sha256, re-computed by me, they match the coordinator snapshot `.audit_views/policy/insurance_claim_services/snapshot_r1.txt`):
  - `tasks/insurance_claim_services/claims.extended.yaml` = 2075cd957b08a78b0653ffadd06598ece656ae662be99c6ef95081d794086816
  - `tasks/insurance_claim_services/task_tools.py` = ecfa993f0d95234d52ae54257c22b5549cf74aa678c68a46ea097e352ae80d92
  - `blueprint/products/claims.yaml` = b97120199e6877f15e4dd470cd5cd79c8d4bb86813f0d422a3bafe1e1b1742eb (and water/mold/rebuild product hashes as in the snapshot)
  - masked views 0.json = 2ac31cc9…d9d1, 1.json = 323d4dc3…7dee7 (match the brief)
- Read: blueprint.yaml, db_schema.json, share_tools.py (tool list), products/claims.yaml (base), the water/mold/rebuild product charters (tier parameters and the rules that make their seeded rows producible), claims.extended.yaml in full, task_tools.py in full, audits/render_source/XF_recipe.md, audits/render_source/identifier_bands.md, the gate snapshot, and the two masked views.
- Not read before this section was frozen: tasks/insurance_claim_services/tasks/*.json, worklog.md, plan.md, any evaluation_criteria / computations / charter_scope / required_documents / design_rationale / solvability_contract / prerequisite_closure field, and any earlier audit. Every search was scoped to explicit file paths, and no search was run recursively over the tasks directory.
- This section uses only the charter, the schema and the tool contracts. It contains nothing derived from a revealed GT.

### entry conditions (Step 0)
Present: all 7 instantiation gates green (check_extended, check_task_tools, replay --check, check_solvability, check_compute, check_grounding, check_cross_fire), with their actual output lines. check_traceability is deferred to post-render by the coordinator. Masked views and their hashes are present. **Entry conditions met.**

Base copy: lines 1–1743 of claims.extended.yaml are byte-identical to blueprint/products/claims.yaml. I checked this with a line-by-line diff.

### policy_conflict_scan

Extended policies (abbreviations used in this audit):

| abbr | id | target_tool (owner) | computes | prerequisite |
|---|---|---|---|---|
| RMS | claims_ext_regulated_material_supplement | submit_regulated_material_supplement_a5be6b72 (user) | requested_amount | [] |
| CRS | claims_ext_code_reconciliation_supplement | submit_code_reconciliation_supplement_37cdbc2e (user) | requested_amount | RMS (value_input code_requested), CWW (value_input denied_back), IDR (state_gate) |
| CWW | claims_ext_code_waiver_writeoff | post_code_waiver_writeoff_45243a0f (agent) | amount | [] |
| IDR | claims_ext_insured_depreciation_release | submit_depreciation_release_d117c1f9 (user) | requested_amount | CWW (value_input rl_written) |
| MRS | claims_ext_mold_reconciliation_supplement | submit_mold_reconciliation_supplement_c8ac8fa6 (user) | requested_amount | MOW (value_input mold_denied_back) |
| MOW | claims_ext_mold_overapproval_writeoff | post_mold_overapproval_writeoff_0ae79d4b (agent) | amount | [] |

- Every policy is scoped to a Homeowner Direct Pay Claim Support file, with an exact record test: exactly one water job plus one contract (RMS, CRS, IDR), exactly one water job plus exactly one supplement approval (CWW), or exactly two mold jobs, one closed and one awaiting clearance (MRS, MOW).
- Overlapping subjects:
  - RMS and CRS both write a claims_supplement_submit with reason code_upgrade. Their objects are disjoint: RMS names the water job, CRS names the reconstruction contract.
  - CWW and MOW both write a claims_receivable_writeoff with reason carrier_denied_line. Their objects are disjoint: a code-upgrade approval naming the water job, versus a mold approval naming the closed mold job.
  - The scopes stay disjoint as stated.
- Conflicts on the same quantity that this scan found (each is a numbered RED below):
  - RMS↔CWW and MRS↔MOW treat the same credited lines, and the same after-hours premium, in opposite ways (CG-16).
  - The three sibling supplement overwrites each retire the base recording clause and defer the rest to "their own rules" (CG-8).
  - CWW and MOW use carrier_denied_line with a meaning the base never gave it (CG-7).
- Time anchors:
  - Supplement window: approved_date, calendar days from the day after, last day inclusive. Restated identically in RMS, CRS and MRS.
  - Depreciation window: earliest acv received_date. Restated in IDR.
  - No conflict.
- Cross-category read boundaries:
  - RMS, CRS, CWW and IDR read water / rebuild rows.
  - MRS and MOW read mold rows.
  - Every XSUM/XCOUNT runs over all of the customer's holdings, and every scope sentence fixes the holding count exactly. B7 is satisfied.
- Task scopes, as I derived them from the trees before any reveal:
  - task 0 = {CRS root, RMS, CWW, IDR}
  - task 1 = {MRS root, MOW}
  - The two are pairwise disjoint and together cover all six extended policies.

### rule_compute_equivalence (check 2)

Mechanical sweep (scratch script, path-scoped to the two files):
- Every `compute_basis` quote is verbatim in its own rule, except **MOW `mo_err`**. Its basis reads "when the closed job carries billing_error credits and no duplicate_line credit, …" while the rule reads "when it carries billing_error credits and no duplicate_line credit, …" (→ CG-10).
- Every `baseline.rule` sentence and every overwrite `replaced_by` is verbatim in its rule.

Sentence-by-sentence sweep in both directions. Every tier named in `factors[].ladder` is a rule sentence and a branch of its `decides` binding, and every compute branch is a stated tier, in all six policies. These rule/compute departures remain (→ CG-9):
1. CWW `ap_written = SUM(claims_approvals.amount, event_type=claims_receivable_writeoff)` sums **every write-off on the file**. The rule holds the figure to "the approval line's amount less earlier write-offs **of it**". The two diverge as soon as a write-off exists against any other line, for example a program_price_adjustment or depreciation_forfeited on the initial approval.
2. MOW `mo_written` has the same defect against the same rule sentence.
3. IDR `rl_code_lines` subtracts **every** billing_error and duplicate_line credit on the water job. The rule says "the water job's lead-safe setup, asbestos sampling, containment setup and HEPA vacuuming, **each net of** the billing_error and duplicate_line credits". water_payments.source_charge_id ties each credit to its line, so a credit against, say, an air-mover line is subtracted by compute but not by the rule.
4. IDR `rl_sup_withheld` and `rl_sup_approved` filter coverage_part='dwelling'. The rule's code-holdback sentence reads "the depreciation withheld on the file's supplement approvals" and its overpayment sentence reads "the supplement approvals less their depreciation withheld", with no coverage filter. A contents supplement approval carrying withheld depreciation separates the two.

### action_binding_and_uuids (check 3)

- `(target_tool, computes)` is unique for each of the six policies, and the six tool names are distinct.
- uuid8s: a5be6b72, 37cdbc2e, c8ac8fa6, d117c1f9, 45243a0f, 0ae79d4b. They share no common prefix or tail and form no sequence, so they read as independently generated.
- Every write tool calls ctx.create/update in its own body (D4). There are no forbidden tokens (D5 sweep clean) and no example values (D1). No composed arguments (D3).
- No tool body checks a policy condition or a prerequisite.
- Docstrings name no other tool and state no position relative to other actions. The words found are "then shows on the claim file as awaiting…" and "carrier receivable after posting". Both describe the tool's own effect, so I record them as an observation (O-4).
- **D2 (→ CG-15):** every docstring states "a positive number with 2 decimal places", and the supplement tools add "an integer of at least 1". No body enforces positivity, the integer bound or the sign. `_Money.cents` rounds only, and `int(supplement_number)` accepts 0 or a negative number.

### prerequisite_graph (check 7)

- Every policy has `prerequisite` filled in: RMS [], CWW [], MOW []; CRS has 3 edges, IDR 1, MRS 1.
- Every `problem` is an extended policy id in this file. None points at a base policy or at itself.
- Graph: RMS→CRS, CWW→CRS, IDR→CRS, CWW→IDR, MOW→MRS. It is acyclic, and the two trees are disjoint.
- Every `policy_source` is verbatim in its own blocked rule (mechanical check). All edges are `form: state`, so no `fallback_reason` is needed.
- `resolved_by` equals the depended-on policy's `target_tool` on all 5 edges.
- `gate` bindings exist in the blocked compute: CRS `code_requested`, `denied_back`; IDR `rl_written`; MRS `mold_denied_back`.
- Each `resolved_by` changes its gate's value as `effect` claims:
  - RMS adds to code_requested.
  - CWW adds to denied_back and rl_written.
  - MOW adds to mold_denied_back.
- The CRS←IDR edge is `state_gate` with `gate: claims_requests.event_type`. Extended policies carry no eligibility list, so this gate names a column, not an eligibility id. I record this as observation O-3. It is not a defect, because the rule sentence carries the gate.
- No authoring-viewpoint phrasing ("in this task", "at the opening") appears in any `prerequisite` text.
- **condition vs sentence (→ CG-13):** on CWW→CRS and CWW→IDR, `condition` is weaker than the sentence, so the field has quietly weakened the edge.
  - The condition asks for one write-off row "for the water job's adjustment credits".
  - The sentence asks for a write-off "for every adjustment credit the water job posted against a line that approval paid for" (CRS), and that "every adjustment credit … against a line paid by the code-upgrade approval stands as a carrier-denied write-off" (IDR).

### prerequisite_sentences (check 6)

| edge | sentence (verbatim, blocked rule) | connective | waited-on state record-visible? | single write that brings it about | verdict |
|---|---|---|---|---|---|
| RMS→CRS | "The ordinance-or-law reconciliation is fixed only after the file carries a code-upgrade supplement naming the water job as its related job that is still awaiting the carrier's decision." | only after | yes: claims_requests code_upgrade, related_job_id = water job, no claims_approvals.claim_request_id referencing it | RMS (only policy writing a code_upgrade supplement naming the water job) | PASS |
| CWW→CRS | "The ordinance-or-law reconciliation is not fixed until the file carries a carrier-denied write-off against the code-upgrade approval for every adjustment credit the water job posted against a line that approval paid for." | not until | **no**: no record ties an approval to the charge lines it paid for (claims_approvals has no line reference; the supplement request carries one amount and one related job) | CWW | **RED CG-13** |
| IDR→CRS | "The ordinance-or-law reconciliation is submitted only after the file carries a depreciation release request naming the reconstruction contract as its completed job." | only after | yes | IDR (only depreciation-release writer) | PASS |
| CWW→IDR | "The insured's depreciation release is not computed before every adjustment credit the water job posted against a line paid by the code-upgrade approval stands as a carrier-denied write-off on the file." | not … before | **no** (same) | CWW | **RED CG-13** |
| MOW→MRS | "The mold reconciliation figure is fixed only after the file carries a carrier-denied write-off against the earlier mold approval for the approved amount the closed mold job never billed." | only after | yes: write-off whose source_approval_id is the mold supplement approval | MOW | PASS |

Derivations, from the sentence plus the records plus the depended-on rule to the resolving action:
- **RMS→CRS.** The reader searches for the rule that prices a code_upgrade supplement naming the water job and finds RMS only. Single reading.
- **IDR→CRS.** The reader searches for the rule that records a depreciation release request naming the contract and finds IDR only. Single reading.
- **MOW→MRS.** The reader searches for the rule that writes off the closed job's unbilled mold approval and finds MOW only. Single reading.
- **CWW→CRS and CWW→IDR.** The reader is pointed at CWW, but there are two defensible readings.
  - (a) One aggregate write-off, as CWW's rule prices it.
  - (b) Write-offs only for credits "against a line that approval paid for". This excludes the goodwill credit, which has no source_charge_id, and, when the paid-for lines cannot be identified, cannot be evaluated at all.
  - The phrase "for every adjustment credit" also reads as one write-off per credit.
- No blocked rule restates a dependency in a second wording or names a tool, a policy id or a snake_case token. ("code-upgrade" is prose, and it is hyphenated.)
- No depended-on rule restates the sentence.
- No rule states a cross-problem order that grounds no declared edge.
- Value dependency with no stated order: RMS's `ol_room` reads `denied_back`, which is written by CWW, but RMS declares no edge on CWW. Where RMS's room binds, a CWW-first order and an RMS-first order give two RMS values. Both are prerequisites of CRS, so the parallel-edge test applies per task (see task files). No consequence follows on task 0's world (room 22 850.00 / 23 296.20, not binding).

### override_declarations (check 1, finding half)

Sweep of each extended policy against every sentence of each `base_policy_refs` entry:

- **RMS and CRS vs claims_evt_supplement.**
  - Followed: approved status, window, pending maximum, minimum, allowed reason, numbering, follow-up/escalation.
  - Declared overwrite 1 (recording on HDP) and overwrite 2 (code_upgrade limit).
  - The base clause "when that remainder is zero the supplement is not submitted…" is compatible.
  - vs claims_carrier_decision and claims_agg_multi_holding: no conflict.
- **MRS vs claims_evt_supplement.** Same as RMS/CRS, with overwrite 2 on the mold limit.
- **IDR vs claims_evt_depreciation_release.**
  - Followed: status, completion, window.
  - Declared: the amount sentence. The replaced_by restates the base amount for every other release (C2 PASS).
  - vs claims_payment_allocation: no conflict.
- **CWW and MOW vs claims_evt_writeoff.**
  - Followed: status, approval-line reference, desk cap, appraisal referral.
  - Declared: "the same amount stays owed by the customer on the job". The replaced_by restates the clause for other write-offs and names the sibling (C2 PASS). The grammar is ambiguous on whether the sibling also "stays owed" (observation O-6).
  - **Undeclared (→ CG-7):** the base defines "carrier_denied_line records a line the carrier declined after approval". CWW posts carrier_denied_line for "the approved amount for water job lines that the water job has since credited". MOW posts it for "the approved amount that the closed mold job … never billed". In neither case did the carrier decline anything, and neither policy declares an overwrite of the defining sentence.
- **Overwrite replaced_by defects (→ CG-8):**
  - (i) RMS ov1, CRS ov1 and MRS ov1 each retire "On tiers where the company does not submit supplements, the company prepares the supplement and records it on the day it is delivered to the insured or public adjuster." They restate it only for PA files. For every other HDP supplement they say "is prepared and recorded as their own rules state", and the own rule of a base HDP supplement (e.g. hidden_damage) is exactly the retired clause (C3).
  - (ii) RMS ov2 and CRS ov2 retire "A code_upgrade supplement may request no more than the ordinance or law limit less the code upgrade amounts already approved on the file,". They then say "every other code_upgrade supplement … stays limited as its own rule states". The limit "less the code upgrade amounts already approved" is not restated for any other code_upgrade supplement (C2/C3), and neither overwrite names its sibling, which retires the same clause (C2).
  - (iii) MRS ov2 retires the mold half and says "every other mold_remediation supplement stays limited as the base rule states", which defers to the clause it retires (C3).

### factor_ladders (structure only; per-task weight lives in 0.md / 1.md)

How to read the tables:
- T1/T2/T3 are the tiers in ladder order; T3 is the fall-through.
- "≡" means one tier's formula, evaluated on another tier's domain, equals that tier's formula identically. Under XF A7 a "nothing" tier fails where another tier is also 0 across its whole domain.
- "producible" means a world the owning charter can produce. Inputs used for producibility:
  - water: lead-safe setup billable only pre-1978, asbestos sampling only pre-1981 (water_regulated_materials).
  - rebuild: plan drawings billed once per contract at plan_drawing_fee (rebuild_permits_and_fees).
  - water/mold: "Goodwill credits on one job may not exceed the tier's goodwill credit cap in total".

**Declared counts.**

| policy | declared | parameter / method | cross_difficulty |
|---|---|---|---|
| RMS | 6 | 4 / 2 | rebuild, water×5 |
| CRS | 6 | 4 / 2 | rebuild×5, water |
| CWW | 6 | 5 / 1 | water×5, null |
| IDR | 6 | 3 / 3 | rebuild, water×2, null×3 |
| MRS | 5 | 3 / 2 | mold×5 |
| MOW | 4 | 2 / 2 | mold×3, null |

- Bindings are pairwise disjoint within each policy.
- No `decides` is `result`.
- Every fall-through equals its `baseline` binding.

#### RMS — all-pairs tier table / factor-reads
| factor (label) | T1 | T2 | T3 | pair test | reads (owner) | verdict |
|---|---|---|---|---|---|---|
| lead_setup_counting (method) | MX(0, wj_lead−rb_lead) | 0 | wj_lead | distinct; **T2 unreachable**: its condition "water job billed a lead-safe setup and built in or after 1978" is barred by water_regulated_materials | rb_lead (own), wj_lead/wj_built/wj_rrp_cutoff (plain) | RED CG-3 |
| rrp_cleanup_lines (method) | cont+hepa | hepa (cont=0) | 0 | **T1≡T2** on T2's domain (cont+hepa with cont=0) | own + wj_built (plain) | RED CG-2 |
| abatement_disposal_line (param) | haul | dumpster (haul=0) | 0 | distinct (data-selected line) | own + wj_asb (plain) | PASS |
| regulated_ppe_line (param) | PPE billed | 1 tech-day × rate | 0 | distinct | own + wj_asb, wj_lead (plain) | PASS |
| setup_day_labor (param) | tech+sup | tech (sup=0) | 0 (tech=0) | **T1≡T2**; **T2≡T3** on T3's domain | own | RED CG-2 |
| regulated_op_rate (param) | O+P | O only | 0 | distinct numbers; **"overhead alone" keyed on the count of regulated codes billed** is no carrier or contractor O&P practice (O&P is the 10/10 pair decided by the trade count, as base claims_estimate_submission states it) | rm_codes (own) | RED CG-4 |
Survivors: abatement_disposal_line and regulated_ppe_line, both parameter. That is 2 factors, below 4, with no method → **CG-6**.

#### CRS
| factor | T1 | T2 | T3 | pair test | reads | verdict |
|---|---|---|---|---|---|---|
| expediting_counting (param) | all expediting | all less building's (no drawings) | 0 | distinct; **unreal condition**: whether plan drawings were billed is no lever on whether the building permit's expediting fee is claimable | own + rb_types, rb_drawings (plain) | RED CG-4 |
| drawing_line_counting (param) | drawings billed | tier plan_drawing_fee (no building permit) | 0 (no drawings) | **T1≡T2 in every producible world** (drawings are billed once at plan_drawing_fee); **T1≡T3** on T3's domain → one live outcome; T2's schedule-fee substitution keyed on the building permit is unreal | own + rb_drawings | RED CG-2, CG-4 |
| letter_line_counting (param) | letters billed | 1 × letter fee (no drawings) | 0 (no letters) | **T1≡T3** on T3's domain; T2 keyed on drawings is unreal | own + rb_drawings | RED CG-2, CG-4 |
| property_setup_counting (method) | MX(rb, wj) | rb (wj=0) | 0 | **T1≡T2** (MX(rb,0)=rb) | own | RED CG-2 |
| mitigation_sampling_lines (method) | asb+haul | asb (no flood cut) | 0 (built ≥1981) | T1/T2 distinct (adds an input); **T2≡T3 in producible worlds** (no asbestos sampling is billable on a ≥1981 building) | own | RED CG-2 |
| reconciliation_op_rate (param) | O+P | O only | 0 | "overhead alone" keyed on the permit-type count is unreal | own | RED CG-4 |
Survivors: 0 → **CG-6**.

#### CWW
| factor | T1 | T2 | T3 | pair test | reads | verdict |
|---|---|---|---|---|---|---|
| duplicate_credit_counting (param) | dup (closed) | MN(dup, balance) (open) | 0 (no dup) | **T1≡T3** on T3's domain; capping a duplicate-line credit at the job balance while the job is open has no basis in a write-off of a carrier approval | own + wj_status, wj_balance (plain) | RED CG-2, CG-4 |
| goodwill_credit_counting (param) | goodwill (closed) | MN(goodwill, cap) (open) | 0 | **T1≡T2 in every producible world** (water goodwill ≤ cap in total); **T1≡T3** → one live outcome; writing off a carrier approval because the contractor gave goodwill is unreal, and goodwill has no line at all (it contradicts the policy's own subject, CG-17) | own + wj_goodwill, wj_status | RED CG-2, CG-4 |
| credited_op_rate (param) | O+P | O only | 0 | O&P keyed on the number of credits ≥2 is unreal | own | RED CG-4 |
| refund_offset_rule (param) | refunds (balance 0) | MX(0, refunds−balance) | 0 | **T1≡T2** on T1's domain (balance 0); **T1≡T3** → one formula; subtracting customer refunds from a carrier write-off is unreal | own + wj_balance | RED CG-2, CG-4 |
| late_fee_relief_rule (param) | all late fees (goodwill present) | late fees above minimum | 0 | **T1≡T3** on T3's domain; an invented "relief" ladder (XF E1 names relief ladders explicitly) | own + wj_goodwill | RED CG-2, CG-4 |
| carrier_cut_rule (method) | scale ap/req (ap ≥ reinspection threshold) | subtract req−ap | as is | distinct; **reads cw_lines = f(cw_duplicate, cw_goodwill, cw_op_rate, cw_refund_offset, cw_late_relief)**, i.e. five factor outputs; choosing pro-rata or flat by the reinspection threshold is unreal | cw_lines (plain built from factor outputs) | RED CG-5, CG-4 |
Survivors: 0 → **CG-6**.

#### IDR
| factor | T1 | T2 | T3 | pair test | reads | verdict |
|---|---|---|---|---|---|---|
| incurred_cost_shortfall (method) | approval − final invoices | approval − (contract ± COs) − water invoice | 0 | T1/T2 distinct; **T3, the fall-through and baseline, is unreachable inside the policy's own scope**: IDR requires the named contract "in substantially_complete, final_invoiced or closed status", so every customer who reaches this write is on T1 or T2 | own + rl_initial, rb_status | RED CG-3 |
| deductible_carry_rule (param) | whole deductible | deductible − gap | 0 | distinct; a real HDP practice (deductible not absorbed by the ACV payment is taken from the holdback) | own + rl_initial | PASS |
| code_holdback_cut_rule (method) | withheld − code lines (final/closed) | whole withheld (substantially complete) | 0 | distinct (adds an input / conditional pick) | own + rl_sup_withheld, rb_status | PASS |
| pending_release_rule (method) | prior requested (no release payment) | MX(0, prior−released) | 0 (no prior) | **T1≡T2** (released = 0 whenever no release payment); **T1≡T3** → a single formula | own + rl_n_release_pay, rl_released | RED CG-2 |
| goodwill_release_offset (param) | goodwill (closed) | MN(goodwill, cap) (open) | 0 | **T1≡T2** in every producible world; **T1≡T3** | own | RED CG-2 |
| supplement_overpayment_rule (param) | excess (no release payment) | MX(0, excess−released) | 0 | **T1≡T2**, **T1≡T3** → single formula | own + rl_sup_withheld, rl_n_release_pay, rl_released | RED CG-2 |
Survivors: deductible_carry_rule (param) and code_holdback_cut_rule (method). That is 2, below 4, with only 1 parameter → **CG-6**.

#### MRS
| factor | T1 | T2 | T3 | pair test | reads | verdict |
|---|---|---|---|---|---|---|
| containment_equipment_days (param) | scrubber+dehu | scrubber (no dehu) | 0 | **T1≡T2**; T2≡T3 on T3's domain | own | RED CG-2 |
| clearance_fee_counting (param) | fees + open tier test fee (assessor tier) | fees | 0 (no fees) | **T2≡T3** on T3's domain | own | RED CG-2 |
| minimum_charge_counting (method) | min lines (charges ≥ minimum) | min lines + shortfall | 0 | **T1≡T3** on T3's domain (min lines = 0) | own + ml_min_lines | RED CG-2 |
| mold_regulated_lines (method) | lead+asb (pre-1978 and lead billed) | asb (1978–1980) | 0 | distinct; **unreal**: a pre-1978 building's billed asbestos sampling counts for nothing when no lead-safe setup was billed, while a 1979 building's counts | own + ml_lead, ml_asb | RED CG-4 |
| mold_op_rate (param) | O+P (containment billed) | O only | 0 | "overhead alone" keyed on containment is unreal | own | RED CG-4 |
Survivors: 0 → **CG-6**.

#### MOW
| factor | T1 | T2 | T3 | pair test | reads | verdict |
|---|---|---|---|---|---|---|
| closed_job_credit_counting (param) | err+dup | err (no dup) | 0 (no err) | **T1≡T2**; T2≡T3 on T3's domain; duplicate-line credits counted only when a billing_error credit also exists is an unreal condition | own + mo_err (plain) | RED CG-2, CG-4 |
| closed_job_goodwill_counting (param) | goodwill (billing_error present) | MN(goodwill, cap) | 0 | **T1≡T2** in every producible world (mold goodwill ≤ cap in total); T1≡T3; the presence of a billing_error credit deciding the goodwill treatment is unreal | own + mo_err | RED CG-2, CG-4 |
| after_hours_premium_rule (method) | premium on tech+sup | premium on tech (no sup) | 0 (no tech) | **T1≡T2**; T2≡T3 on T3's domain; a supervisor-only after-hours premium uncounted is an unreal condition | own | RED CG-2, CG-4 |
| mold_cut_rule (method) | scale | subtract | as is | **reads mo_unbilled = f(mw_credits, mw_goodwill, mw_premium)**; threshold-keyed choice is unreal | mo_unbilled (plain from factor outputs) | RED CG-5, CG-4 |
Survivors: 0 → **CG-6**.

- **Rule statement of ladders:** every tier, its condition and its value or method is stated in its own rule. No tier lives only in compute.
- **Assembly (XF A2, → CG-11):** in every policy the combination sentence names factor quantities instead of combining generically:
  - RMS: "raised by the regulated-material overhead and profit rate"
  - CRS: "raised by the reconciliation overhead and profit rate"
  - CWW: "raised by the credited-line overhead and profit rate; the refund offset and the late-fee relief are then subtracted …; the carrier's cut is applied"
  - IDR: "the incurred-cost shortfall, the deductible carry, the code holdback cut, the pending release, the goodwill release offset and the supplement overpayment are each subtracted"
  - MRS: "raised by the mold overhead and profit rate"
  - MOW: "less the adjustment credits counted below, less the goodwill counted below and less the after-hours premium …, after which the carrier's cut is applied"
- **Order (XF A5, → CG-12):** RMS's combination sentence fixes "sum → raised → held to the room → rounded", and a separate sentence subtracts prior requests "From the raised sum". Where subtraction sits relative to the hold is not fixed in the combination sentence, and min(raised − prior, room) ≠ min(raised, room) − prior whenever the room binds. CRS, CWW, IDR, MRS and MOW fix their order.
- **Baseline self-sufficiency:** every baseline.rule gives a definite number from the records with no factor applied. But each baseline sentence also **denies** the factors in the same rule (→ CG-1).

### XF recipe sweep summary (every point, every policy)

| XF point | result |
|---|---|
| A1 | RED CG-5: CWW carrier_cut_rule, MOW mold_cut_rule. Every other factor reads only its own bindings plus plain or baseline bindings (tables above) |
| A2 | RED CG-11, 6/6 policies |
| A3 | PASS: each factor's defining sentences are its own ladder; shared selections (wj_built, rb_drawings, rl_initial, mo_err, wj_goodwill …) are plain bindings |
| A4 | PASS: no "as another policy figures it", no gate spanning several factors |
| A5 | RED CG-12 (RMS) |
| A6 | per task, see 0.md / 1.md; T2 fails structurally wherever CG-2/CG-3 make a tier dead |
| A7 | RED CG-2, 19 members |
| A8 | PASS: tier text equals compute, including inclusive and exclusive boundaries |
| A9 | PASS |
| A10 | PASS: no factor id is a substring of any tool name (mechanical) |
| B1 | RED CG-9 |
| B2/B3 | PASS within the exact-count scopes; lead-safe setup is billed once per job, so the XLATEST setup date has no tie |
| B4 | n/a |
| B5 | PASS: RND(x+1e-9) on non-negative values; tool bodies use a Decimal half-up helper |
| B6 | RED CG-10 (MOW mo_err) |
| B7 | PASS: exact holding-count scopes |
| C1 | RED CG-7 |
| C2/C3 | RED CG-8 |
| D1 | PASS |
| D2 | RED CG-15 |
| D3–D8 | PASS |
| E1 | RED CG-4, CG-16, CG-17 |
| E2/E3 | per task (task 0 carries a seeded claims row no rule produces, see 0.md) |
| E4 | n/a |
| E5 | per task: PASS in both |
| E6/E7 | RED CG-14 |
| E8/E9 | PASS: account charter not in either world; no service agreement is held |
| F1 | PASS: the insured submits their own supplement / release from the portal on a tier where the company does not submit |

### findings (charter-global; each lists the tasks it bears on)

**CG-1 SOURCE-POLICY RED — the baseline sentences in every rule deny the factors stated in the same rule.**
- Symptom. Each rule states its baseline as an unconditional fact that contradicts its own factor sentences:
  - RMS: "…each at the amount billed, and nothing else; no overhead and profit is added". The same rule also says "the containment setup and the HEPA vacuuming billed on the job are both counted" and "The regulated-material overhead and profit rate is the tier's overhead percentage plus its profit percentage when …".
  - CRS: "every permit fee … and no other line; no overhead and profit is added". It also counts expediting, drawing, letter, setup and sampling lines plus an O&P rate.
  - CWW: "adds no overhead and profit, subtracts nothing, makes no adjustment for the carrier's cut". It also has an O&P rate, a refund offset, a late-fee relief and a carrier's cut.
  - IDR: "the release figure is the dwelling holdback, rounded to the cent, half up." It also subtracts six quantities "from the dwelling holdback".
  - MRS: "…and nothing else; no overhead and profit is added". It also counts equipment, clearance, minimum and regulated lines plus an O&P rate.
  - MOW: "with no credit, goodwill or premium taken off and no adjustment for the carrier's cut". The same rule takes off credits, goodwill and premium and applies a cut.
- Root cause. The baseline is written as an exclusive statement rather than a default silent about variation.
- Consequence. Two readings of one rule in one situation:
  - task 0, CRS: 0.00 (the literal baseline: 508.00 − 3 040.98 + 446.20 < 0) vs 725.62 (the ladders);
  - task 1, MRS: 0.00 vs 3 101.52;
  - task 0, CWW: 31.00 vs 446.20;
  - task 1, MOW: 111.63 vs 221.48;
  - task 0, IDR: 7 273.80 vs 3 527.39;
  - task 0, RMS: 0.00 vs 1 390.98.
- Bears on: task 0, task 1.

**CG-2 SOURCE-FACTOR RED — tiers that select the same value or method (XF A7).** 19 members:
- RMS: rrp_cleanup_lines, setup_day_labor.
- CRS: drawing_line_counting, letter_line_counting, property_setup_counting, mitigation_sampling_lines.
- CWW: duplicate_credit_counting, goodwill_credit_counting, refund_offset_rule, late_fee_relief_rule.
- IDR: pending_release_rule, goodwill_release_offset, supplement_overpayment_rule.
- MRS: containment_equipment_days, clearance_fee_counting, minimum_charge_counting.
- MOW: closed_job_credit_counting, closed_job_goodwill_counting, after_hours_premium_rule.

The pair that coincides for each member is in the factor_ladders tables. Root cause: "otherwise" and "when X is absent" tiers restate another tier's formula with one input at zero. "Up to the cap" tiers restate the amount, because the owning charters already cap goodwill per job in total. The drawing schedule-fee tier restates the billed line, because the rebuild charter bills drawings at that fee. Consequence: each such ladder has two live tiers or fewer. Bears on: task 0 (RMS, CRS, CWW, IDR members) and task 1 (MRS, MOW members).

**CG-3 SOURCE-FACTOR RED — tiers no producible or in-scope customer can reach.**
- RMS lead_setup_counting T2 is barred by water_regulated_materials: "Lead-safe setup is billable only when the building was built before the RRP year-built cutoff…".
- IDR incurred_cost_shortfall T3 (the fall-through and baseline) is excluded by IDR's own scope sentence "The job named in the request must be complete: a rebuild contract in substantially_complete, final_invoiced or closed status."
- Consequence: lead_setup_counting has 2 live tiers. incurred_cost_shortfall's baseline is a treatment no in-scope customer ever receives, so it is a straw man.
- Bears on: task 0.

**CG-4 SOURCE-FACTOR RED — unreal ladders (XF E1).**
- Members:
  - the four "overhead alone" O&P tiers: RMS regulated_op_rate, CRS reconciliation_op_rate, CWW credited_op_rate, MRS mold_op_rate;
  - CRS expediting_counting, plus the T2 schedule-fee substitutions in drawing_line_counting and letter_line_counting;
  - CWW duplicate_credit_counting (balance cap), goodwill_credit_counting, refund_offset_rule, late_fee_relief_rule, carrier_cut_rule;
  - MRS mold_regulated_lines;
  - MOW closed_job_credit_counting, closed_job_goodwill_counting, after_hours_premium_rule (its conditions), mold_cut_rule.
- The reason for each member is in the factor_ladders tables. In short: the conditions are not levers that any carrier, contractor or claim program weighs for that quantity (count of codes or credits deciding profit, drawings deciding expediting, billing_error presence deciding goodwill treatment, the reinspection threshold deciding pro-rata vs flat cut), and several outcomes are treatments no business publishes (refunds and late fees subtracted from a carrier write-off; goodwill written off against a carrier approval).
- Bears on: task 0, task 1.

**CG-5 SOURCE-FACTOR RED — a factor reads other factors' outputs (XF A1).**
- CWW carrier_cut_rule decides cw_after_cut from cw_lines = MX(0,(wj_credit_err + cw_duplicate + cw_goodwill)·(1 + cw_op_rate/100) − cw_refund_offset − cw_late_relief).
- MOW mold_cut_rule decides mw_after_cut from mo_unbilled = MX(0, mo_ap_amount − (mo_billed − mw_credits − mw_goodwill − mw_premium)).
- Consequence: the cut's effect depends on which other factors were found. Task 0: with the dup factor at baseline the cut takes CWW from 22.20 to 0.00, and with all factors applied from 496.20 to 446.20.
- Bears on: task 0 (CWW), task 1 (MOW).

**CG-6 SOURCE-FACTOR RED — factor counts after striking.**
- Surviving factors per policy:

  | policy | survivors |
  |---|---|
  | RMS | 2 (no method) |
  | CRS | 0 |
  | CWW | 0 |
  | IDR | 2 (1 parameter) |
  | MRS | 0 |
  | MOW | 0 |

- Every policy falls below the 4-factor, 2-parameter, 1-method floor.
- Bears on: task 0, task 1.

**CG-7 SOURCE-POLICY RED — undeclared override of the meaning of carrier_denied_line.**
- Base claims_evt_writeoff: "carrier_denied_line records a line the carrier declined after approval".
- CWW: "the carrier_denied_line write-off … of the approved amount for water job lines that the water job has since credited". The tool docstring says "for an approved amount the company will not collect because the water job has credited the lines it paid for".
- MOW: "the carrier_denied_line write-off … of the approved amount that the closed mold job the approval paid for never billed".
- No carrier decline exists in either world (no record of one), and neither policy's overwrite names the defining sentence.
- Consequence: under the base sentence neither write-off is a carrier_denied_line. A reader applying the base would post nothing (task 0: CWW 0.00 vs 446.20; task 1: MOW 0.00 vs 221.48). The CRS, IDR and MRS gates then never open.
- Bears on: task 0, task 1.

**CG-8 SOURCE-POLICY RED — overwrites that retire base clauses and defer the remainder to the retired clause (C2/C3).**
- Members: RMS ov1, RMS ov2, CRS ov1, CRS ov2, MRS ov1, MRS ov2. RMS ov2 and CRS ov2 additionally fail to name their sibling.
- Quotes are in override_declarations.
- Consequence: a non-extended HDP supplement (e.g. hidden_damage) has no recording rule left, and a non-extended code_upgrade or mold supplement has no limit left.
- Neither task's scored write is such a supplement, so this is a charter defect with no task consequence.

**CG-9 SOURCE-POLICY RED — rule ≠ compute in producible worlds (B1).** Four members are listed under rule_compute_equivalence. Neither task's world separates the rule from compute:
- no other write-off exists before CWW or MOW;
- task 0's credits sit on code lines (hepa, containment);
- only dwelling approvals are seeded.

So this is charter-only.

**CG-10 SOURCE-POLICY RED — compute_basis quote not verbatim (B6).** MOW `mo_err`, as shown under rule_compute_equivalence.

**CG-11 SOURCE-POLICY RED (XF A2) — assembly sentences name factor quantities.** All 6 policies.

**CG-12 SOURCE-POLICY RED (XF A5) — RMS's order of the subtraction relative to the room hold is not fixed by its combination sentence.** No consequence on task 0, because the room does not bind.

**CG-13 SOURCE-POLICY RED — two prerequisite sentences name a state that is not record-visible and admit a second reading; `condition` is weaker than the sentence.**
- Edges: CWW→CRS and CWW→IDR, as shown under prerequisite_sentences.
- Task 0 consequence: reading (b) excludes the goodwill credit, which is not against any line. It gives CWW 386.20 instead of 446.20, then IDR 3 587.39 instead of 3 527.39 and CRS 665.62 instead of 725.62.
- Bears on: task 0.

**CG-14 SOURCE-POLICY RED — waits that their resolvers cannot always satisfy (XF E6/E7).**
- Edges CWW→CRS and CWW→IDR are engaged whenever the water job carries adjustment credits, but CWW can compute 0.00 for such a world. Example: task 0's world with no duplicate_line credit gives 0.00, after the cut, and a write-off is "a positive number". CWW can also compute an amount above the desk write-off cap (HDP 500.00), "not posted by the desk". In either case CRS and IDR wait forever.
- Edge MOW→MRS: MOW computes 0.00 on task 1's world without the after-hours premium.
- Edge RMS→CRS: RMS can compute an amount below the 250.00 supplement minimum, or 0.00. Its baseline alone gives 0.00 on task 0's world. RMS then "is submitted only for an amount at least the tier's supplement minimum", so the waited-on pending supplement never appears.
- No sentence carves out the 0.00 or over-cap case.
- Both task worlds sit inside the satisfiable region (RMS 1 390.98, CWW 446.20, MOW 221.48), so this is a charter-only defect.

**CG-15 SOURCE-POLICY RED (XF D2) — docstring constraints not enforced by the bodies.** All 6 tools. No consequence on the gold path.

**CG-16 SOURCE-POLICY RED — sibling policies treat the same amounts in opposite ways.**
- RMS counts "the containment setup and the HEPA vacuuming billed on the job … each at the amount billed". This includes lines the water job has credited as duplicate_line or billing_error. CWW treats exactly those credited lines as an approved amount "the company will not collect" and writes it off.
- MRS counts "every remediation scope line billed on the file's mold jobs … at the amount billed", which includes the closed job's after-hours labor at premium rate and its credited lines. MOW states that after-hours labor "is the customer's own choice and not covered scope" and removes credits and premium from "covered billing".
- Consequence: the carrier is asked to approve amounts the sibling rule declares uncollectable or not covered:
  - task 0: RMS includes 395.00 + 31.00 of credited lines, × 1.2 = 511.20;
  - task 1: MRS includes the premium 229.18 and the credits 100.67, × 1.2 = 395.82.
- Bears on: task 0, task 1.

**CG-17 SOURCE-POLICY RED — subject sentences that the formula does not keep.**
- CRS subject: "claims … every building-department and regulated-material cost of the loss not yet claimed". Its formula:
  - counts only permits, expediting, drawings, letters, the property lead-safe setup and the water job's sampling and haul;
  - subtracts every code_upgrade request on the file, including RMS's request for cleanup, PPE and labor lines that CRS does not count;
  - adds back write-offs of credited water lines that it also does not count.
- CWW subject: "the approved amount for water job lines that the water job has since credited". Its formula counts a goodwill credit, which has no line, raises the figure by an O&P rate, and subtracts refunds and late fees.
- Task 0 consequence, CRS: the permit, expediting, drawing, letter and contract lead-safe lines (2 128.00 × 1.2 = 2 553.60) were never claimed by any request. The supplement #1 and RMS requests both name the water job. The formula nevertheless yields 725.62.
- Bears on: task 0.

### observations (no demonstrated consequence)
- **O-1.** RMS adds back every carrier_denied_line write-off on the file to its ordinance or law room, with no scope sentence restricting them to code-upgrade approvals (CRS and MRS have one). Not binding on task 0.
- **O-2.** RMS↔CWW are parallel prerequisites of CRS, and RMS's room reads CWW's output with no declared order. Not binding on task 0.
- **O-3.** The IDR→CRS state_gate field names a column (`claims_requests.event_type`) rather than an eligibility id.
- **O-4.** The docstring words "then" and "after" describe each tool's own effect only.
- **O-5.** RMS, CRS and MRS hand the insured a supplement on HDP via the portal (F1 PASS). The base's "company prepares and records on delivery" survives only for PA files (CG-8).
- **O-6.** The CWW and MOW replaced_by clauses "follows its own rule, and on such a tier the same amount stays owed" are ambiguous as to whether the sibling write-off also stays owed.

## closing_checklist

Not written in revision_1. Step 4 runs only once all M tasks PASS all four relationships, and both tasks are RED (see 0.md, 1.md).

Post-reveal note (this is the only post-reveal text in this file; the sections above were frozen before any GT read): both tasks' gold values, baselines and factor sensitivities equal my blind recomputation figure for figure. The REDs come from the charter's structure, realism and wording, and from one seeded row (task 0, T0-1), not from an arithmetic disagreement.

VERDICT revision_1: task0=RED task1=RED charter=CG-1,CG-2,CG-3,CG-4,CG-5,CG-6,CG-7,CG-8,CG-9,CG-10,CG-11,CG-12,CG-13,CG-14,CG-15,CG-16,CG-17

## revision_2

### charter_global_frozen (r2)

- Freeze: 2026-10-24, before any read of tasks/*.json for round 2. Auditor: the same independent auditor as round 1.
- Entry check: the last worklog line reads `REWORK round 2: gates 7/7 green`. I ran `/tmp/erl0079_coord/snapshot.sh insurance_claim_services 2` myself (execute only).
- Gate snapshot: `.audit_views/policy/insurance_claim_services/snapshot_r2.txt`. All 7 gates report OK; check_traceability is deferred.
- Hashes:
  - claims.extended.yaml = b2d358c4…6ed7
  - task_tools.py = 4119fca6…c448
  - views 0.json = ad06e016…b369, 1.json = 3c6edd95…fad8
  - product charters unchanged
- **Both shared hashes changed, so every charter-global section is re-derived in full.** Nothing is carried forward by reference.
- Base copy (lines 1–1743) is still byte-identical to blueprint/products/claims.yaml.
- Read for this round:
  - the full extended charter, task_tools.py, the two masked views, the water/mold/rebuild charters;
  - only the `## REWORK round 2` section of worklog.md (lines 128–156), as the coordinator instructed.
- **contamination_disclosure (r2):** that worklog section lists every scored value ("T0 write-off 498.62, regulated-scope supplement 2326.95, reassessment supplement 1172.85, release 2273.53; T1 protocol supplement 2457.15, final mold supplement 810.69"). I read it before deriving.
  - My recomputation reproduces all six figures, but it is **not blind**. It confirms arithmetic only and is not independent evidence that the policy entails these values.
  - No finding below rests on those figures. Each rests on charter text, the seed, or my own recomputation of alternative readings.

### extended policies (r2)

| abbr | id | tool (owner) | prerequisite |
|---|---|---|---|
| RSS | claims_ext_regulated_scope_supplement | submit_regulated_scope_supplement_ec41bed4 (agent) | [] |
| CAT | claims_ext_category_reassessment_supplement | submit_category_reassessment_supplement_86febceb (agent) | RSS (value_input sc_reg_pending, action) |
| CLW | claims_ext_credited_line_writeoff | post_credited_line_writeoff_e2edbc44 (agent) | [] |
| IDR | claims_ext_insured_depreciation_release | submit_depreciation_release_d117c1f9 (user) | CLW (rl_written), CAT (rl_pend_price), RSS (rl_pend_scope), all value_input, action |
| MPS | claims_ext_mold_protocol_supplement | submit_mold_protocol_supplement_d9a0c26a (agent) | [] |
| MRS | claims_ext_mold_reconciliation_supplement | submit_mold_reconciliation_7e4d140d (user) | MPS (value_input mr_pending, action) |

- Scopes, derived before reveal:
  - task 0 = {IDR root, CLW, CAT, RSS};
  - task 1 = {MRS root, MPS}.
  - They are disjoint and cover all six policies.
- The graph is acyclic.
- Every `policy_source` is verbatim in its blocked rule, every `fallback_reason` is present on its action-form edge, and every `resolved_by` equals the depended-on target tool.
- Each fallback is justified: the depended-on write leaves no record when its figure is below the supplement minimum, is 0.00, or exceeds the desk cap.
- Mechanical sweeps:
  - every compute_basis quote is verbatim (CG-10 closed);
  - baseline and replaced_by sentences are in their rules;
  - no factor id is a substring of a tool name;
  - no forbidden token appears.
  - uuid8s ec41bed4, 86febceb, d9a0c26a, 7e4d140d, e2edbc44 are new and independent; d117c1f9 is kept with its unchanged tool.

### round-1 items: closure check (each against the r2 charter)

| id | r2 status | evidence |
|---|---|---|
| CG-1 | **RED (1 member remains)** | CAT: the rule prices each family "from the water charter's rates for the tier the recorded category and the job's affected area select", then its baseline sentence says "Each line family is priced at the rates of the tier the job was dispatched at". Two statements about which tier prices a family give 0.00 vs 1 172.85 on task 0. Other baselines are worded as standard or default values ("Its standard surface treatment…", "The standard method counts…", or a definition its own fall-through tier restates) and deny no factor: closed for RSS, CLW, IDR, MPS, MRS. |
| CG-2 | CLOSED | All-pairs check over the 33 new factors: no tier coincides with another tier on its domain in a producible world. The closest case, IDR water_cost_measure T2 (final invoice) vs T3 (posted charges less late fees and card surcharges), separates when a pre-invoice credit-card payment is surcharged (water_evt_customer_payment allows payment on any not-closed job). |
| CG-3 | CLOSED | IDR contract T3 = substantially_complete is inside scope; CLW Carrier Program tier is inside scope; MRS/MPS HVAC tiers are reachable. |
| CG-4 | **RED (1 member)** | MRS final_after_hours_labor T2: "for growth in the HVAC system, no after-hours labor, because system work is scheduled with the system shut down". Labor actually performed and billed is dropped entirely, including its business-rate portion. The attic tier drops only the premium; no carrier or contractor treats billed HVAC labor as worth nothing. All other r2 ladders are grounded in charter rates or cutoffs, or in record dates (estimate vs invoice, change order dates), and I accept them. |
| CG-5 | **RED (1 member)** | IDR advance_recoupment_rule reads `rl_adv_gap = (rl_init_amt − rl_init_wh − deductible) − rl_acv`. `rl_init_wh` and `rl_acv` are bindings of deductible_carry_rule (its bindings list: rl_init_wh, rl_acv, rl_gap, rl_ded_amt, rl_deductible). Factor-reads table: every other factor reads only its own or plain bindings. |
| CG-6 | **RED** | After striking (CG-18, CG-4, CG-5): RSS 6 (5 parameter / 1 method) ✓; CAT 4, 0 method ✗; CLW 4, 0 method ✗; IDR 5 (2 / 3) ✓; MPS 2, 0 method ✗; MRS 3, 0 method ✗. |
| CG-7 | **RED (residual)** | The overwrite is now declared. Its replacement meaning says carrier_denied_line "records the carrier's decline, at its review of the final invoices". No record shows that review or decline: task 0 holds no carrier letter, no approval change, nothing dated. Base claims_carrier_decision, which is in CLW's own base_policy_refs and is not overwritten, says "The carrier's decision on the submitted estimate is recorded exactly as the carrier's approval letter states it". Posting CLW therefore records a third-party decision the world never received (a fabricated external event, check 5). |
| CG-8 | CLOSED | CLW, MRS and IDR replaced_by each restate the retired clause for every other write and name their scope. RSS, CAT and MPS follow the base PA/HDP recording clause and need no overwrite. |
| CG-9 | **RED (1 new member)** | MPS `mp_approved` and MRS `mr_approved` sum supplement approvals only. The rule says "the mold amounts already approved on the file", which base measure claims_msr_mold_approved defines as including "the mold portion of the initial approval when the loss_type is mold". Neither scope excludes loss_type mold, so rule ≠ compute on a mold-loss file. The r1 members (write-offs "of it", "each net of", coverage filters) are closed. |
| CG-10 | CLOSED | Mechanical sweep. |
| CG-11 | CLOSED | Every combination sentence is generic ("each … settled below"). CLW's "each converted to the carrier's pricing for its class of lines as settled below" is borderline but refers to the ladders generically (observation). |
| CG-12 | CLOSED | RSS has no room; the other orders are fixed. |
| CG-13 | CLOSED | Action-form sentences with valid fallbacks; conditions are record-visible. |
| CG-14 | CLOSED | Carve-outs: "where it reaches the supplement minimum"; "where it comes to more than nothing and within the desk write-off cap". |
| CG-15 | CLOSED | Bodies reject non-positive amounts and non-integer or <1 sequence numbers. The fix introduced D4 (CG-19). |
| CG-16 | **RED (4 members)** | See below. |
| CG-17 | **RED (1 member)** | MRS, see below. RSS's subject is folded into CG-16(a). CLW's and CAT's subjects now match their formulas. |

### findings (r2, charter-global; every member listed)

**CG-16 SOURCE-POLICY RED — sibling policies assert contradictory facts about the same lines or the same concept.**
- **(a) Was the water job's regulated work carried by the initial approval?** Three policies answer differently.
  - RSS subject: "the regulated-material work billed on the water mitigation job that the carrier's initial approval did not carry". It claims lead-safe setup, asbestos, containment, HEPA, disposal, PPE, labor and baseboard.
  - CLW billing_error T1: "an estimate built from the invoice carried the over-billed quantities". CLW water_line_pricing T2: "submitted on or after the water job was opened, so that it carried the water job's lines".
  - CAT regulated T2: "HEPA cleaning stands in the approved mitigation scope".
  - Task 0 consequence: estimate 2026-05-11 ≥ water invoiced_date 2026-05-10, so CLW's premise holds. Under that premise RSS has nothing un-carried to claim. RSS not owed gives CAT 1 122.85 and IDR 3 548.58, versus 2 326.95 / 1 172.85 / 2 273.53 when the omission premise is taken.
- **(b) The credited quantity.** CAT prices "the extraction square feet billed" (860 on line b78ab196). Billing_error credit 399b7c29 (31.20 = 40 sq ft × 0.78) declares 40 of those sq ft over-billed, and CLW writes that credit off as not incurred. Task 0: CAT includes 40 × 0.16 = 6.40 on credited quantity (1 166.45 net of it).
- **(c) What counts as incurred.**
  - CLW: "the carrier's replacement-cost settlement pays only the price actually incurred for work billed, kept and performed".
  - IDR: "The incurred cost is … plus the amounts requested on price_variance supplements awaiting the carrier's decision, because the scope a reassessed water category requires is part of the cost of the loss though the job was not repriced". This is scope never billed to anyone.
  - Task 0: without the unbilled reassessment scope in incurred cost, IDR is 1 100.68 instead of 2 273.53.
- **(d) The attic job's lead-safe setup.**
  - MRS attic tier: "the asbestos sampling lines billed on the job only, because … an unfinished attic carries no painted surface whose disturbance calls for lead-safe work". MPS's attic regulated tier rests on the same premise.
  - The seed bills lead-safe setup 84da335d (345.00) on that attic job. The mold charter makes it billable "only for housing built before the RRP year-built cutoff where painted surfaces are disturbed".
  - Either the row is unproducible or the tier's premise is false in this world. Task 1: MRS 1 155.69 with the line vs 810.69 without it.

**CG-17 SOURCE-POLICY RED — MRS subject vs formula.**
- Subject: "the mold_remediation supplement that claims the scope actually billed on the mold job awaiting clearance beyond what that job's protocol supplement asked".
- The formula's enumerated families omit billed PPE (23399f11, c712a181: 211.20), business-hours technician labor (e979360c: 707.20) and, on the attic tier, the lead-safe setup (345.00). No sentence excludes PPE or business-hours labor.
- Task 1: the subject reading gives 2 074.09 vs 810.69.

**CG-18 SOURCE-FACTOR RED (new; XF A7 method shape / mislabelled effect).** Factors labelled `method` whose tiers differ only by a rate, multiplier or constant, or by which same-field aggregate is summed:
- CAT reassessed_carpet_treatment: carpet qty × black removal rate vs carpet qty × gray pad rate.
- CAT reassessed_air_scrubber: mover days × 78.60 vs mover days × 70.74.
- CLW water_line_pricing_basis: ×(1 − discount) / ×(1 + O + P) / ×1.
- CLW contract_scope_pricing_basis: the same multipliers.
- MPS protocol_air_treatment, T2 vs T3: cap × scrubber rate vs cap × dehumidifier rate.
- MPS protocol_regulated_fee: constants 770 / 425 / 0.
- MRS final_air_lines: sums of amount over containment, scrubber and dehumidifier lines (one input under A7).

Seven members.

**CG-19 SOURCE-POLICY RED (new, regression of the CG-15 fix; XF D4).** submit_regulated_scope_supplement_ec41bed4, submit_category_reassessment_supplement_86febceb, submit_mold_protocol_supplement_d9a0c26a and submit_mold_reconciliation_7e4d140d each `return _Money.supplement(...)`. `ctx.create("claims_requests", …)` runs inside the helper `_Money.supplement`, not in the tool's own body. Four members. (IDR and CLW write in their own bodies.)

**CG-20 SOURCE-POLICY RED (new; XF B3 same-day ties).**
- CLW billing_error_inclusion, duplicate_line_inclusion and goodwill_inclusion T2 take "the … credit against the job's latest equipment-day line (the equipment-day line with the latest service date)". Compute is `XLATEST('water','water_charges','water_charge_id', date_field='service_date', event_type='water_equipment_day_charge')`.
- A water job bills several equipment-day lines per day (task 0 has air_mover cd2ccb36 and lgr_dehumidifier 9b613b6b, both on 2026-05-09), so the latest date normally has two or more lines. Neither the rule nor the ladder states a tie rule, and the credit taken depends on which row XLATEST returns.
- Three members. No consequence on task 0, which takes T1.

**CG-21 SOURCE-FACTOR RED (new) — no multi-source factor among task 1's computations.**
- Every MPS and MRS tier is decided by fields of one record (the job awaiting clearance: growth_location, property_type, year_built) plus that job's tier parameters.
- No tier other than a fall-through is a conjunction or disjunction of conditions over distinct records.
- Task 0 has one: CLW removed_scope_inclusion, with the rebuild change order credit date against the claims estimate date.

### observations (r2)
- RSS `rs_setup_date` and `rs_hepa_date` take the latest containment or HEPA date. The rule speaks of "the service date of the job's containment setup line" (singular) and does not say which date is used when there are several such lines.
- In CLW's water_line_pricing T2, the conjunct "submitted on or after the water job was opened" holds of nearly every file reaching this write. The tier still differs from T3 through the trade count.
- On task 1, MPS (2 457.15) plus MRS (810.69) request 3 267.84 against a mold room of 2 457.15. This is literal compliance with base ("less the mold amounts already approved"), and I note it only.

### closing_checklist (r2)

Not written: both tasks remain RED.

Post-reveal note: GT equals my recomputation on every scored, baseline and sensitivity figure in both tasks. This agreement is not blind (worklog disclosure). The r2 REDs are structural, realism or wording defects plus one tool regression (CG-19).

**r1 items closed in r2:** CG-2, CG-3, CG-8, CG-10, CG-11, CG-12, CG-13, CG-14, CG-15, T0-1, T0-2, T0-3.

**Still open, with new members:** CG-1, CG-4, CG-5, CG-6, CG-7, CG-9, CG-16, CG-17.

**New:** CG-18, CG-19 (regression), CG-20, CG-21.

VERDICT revision_2: task0=RED task1=RED charter=CG-1,CG-4,CG-5,CG-6,CG-7,CG-9,CG-16,CG-17,CG-18,CG-19,CG-20,CG-21

## revision_3

### charter_global_frozen (r3)

- Freeze: 2026-10-25, before any r3 read of tasks/*.json.
- Entry check: the last worklog line reads `REWORK round 3: gates 7/7 green`. I ran `/tmp/erl0079_coord/snapshot.sh insurance_claim_services 3` myself (execute only).
- Gate snapshot: `.audit_views/policy/insurance_claim_services/snapshot_r3.txt`. All 7 gates are OK; check_traceability is deferred.
- Hashes:
  - claims.extended.yaml = df06d0c8…eaaa
  - task_tools.py = fa915bb8…4e59
  - views 0.json = 62f8fc7d…f4b, 1.json = cfe31149…c9d
  - product charters unchanged
- **Both shared hashes changed, so every charter-global section is re-derived.** The base copy is still byte-identical.
- Read for this round:
  - the full extended charter, task_tools.py, both masked views;
  - only the `## REWORK round 3` section of worklog.md (lines 182–198);
  - audits/render_source/realism_bar.md.
- **No contamination this round:** the REWORK section carries item ids and claims only, with no figures, consistent with RULE-4.
- realism_bar.md applied: no factor is tagged R6, and none was graded R6-WAIVED.

### structure (r3)

- Six policies, the same ids and tools as r2.
- Edges:
  - IDR ← CLW (rl_written), IDR ← CAT (rl_pend_price), IDR ← RSS (rl_pend_scope);
  - MRS ← MPS (mr_pending);
  - all value_input, action form, with valid fallbacks.
- **The r2 edge CAT ← RSS has been removed.** RSS and CAT are now unordered siblings under IDR (see T0-R3-1 in 0.md).
- Scopes: task 0 = {IDR, CLW, CAT, RSS}; task 1 = {MRS, MPS}. Disjoint and complete. The graph is acyclic.
- Mechanical sweeps clean: compute_basis verbatim, policy_source and replaced_by in rule, no A10 hit, no D5 token.
- Every write tool calls ctx.create (and ctx.update) in its own body.

### r2 items: closure check (r3)

| id | r3 status | evidence |
|---|---|---|
| CG-1 | CLOSED | CAT baseline is now "starts from nothing: a line family adds a difference only as settled below". No baseline sentence denies a factor or names a tier. |
| CG-4 | CLOSED | MRS HVAC tier now keeps the supervisor labor and drops only technician time that the per-vent and per-unit cleaning fees price. This is plausible (R1/R3), with no X4. |
| CG-5 | CLOSED | IDR advance reads its own `a_init_wh` and `a_acv`. A1 table: every factor reads only its own or plain bindings. |
| CG-6 | **RED** | After the A7 re-check (CG-18 below): RSS 6 parameter / **0 method**; MPS 3 parameter / **0 method** (surface fails); MRS 4 parameter / **0 method** (labor fails). CAT 4/2 ✓, CLW 5/1 ✓, IDR 3/3 ✓. |
| CG-7 | CLOSED | The CLW overwrite now records the approved value of work the jobs credited, conceded or removed after the approved estimate carried it, keyed on credit and change-order rows. No carrier act is asserted, so RULE-3 is met; the tool docstring is aligned. |
| CG-9 | CLOSED | MPS and MRS scopes require loss_type ≠ mold, so the supplement-approval sum equals the mold amounts approved. |
| CG-16 | CLOSED | (a) RSS: "the estimate behind the carrier's initial approval leaves out [regulated work] because regulated-material work is claimed by its own supplement". CAT no longer asserts approved scope. (b) RSS and CAT scopes exclude credits on lines they read. (c) IDR treats pending supplements as expected approvals against billed cost, consistent with CLW's billed-work premise. (d) The attic job bills no lead-safe setup. Observation O-r3-1 keeps a residual wording point. |
| CG-17 | CLOSED | The MRS core now includes PPE, clearance test and minimum charge, and labor includes business-hours labor. On task 1 every billed line family of job B is counted. |
| CG-18 | **RED (3 members remain; all three were already present in r2 and missed by my r2 table)** | XF A7: "aggregates of the same field count as one input whatever their window/filter; constant multipliers are ignored; a pair of tiers FAILS if it is the same combination of the same windowed sums". (1) RSS rrp_cleanup_scope (method): T1 HEPA billed vs T2 containment + HEPA billed, both sums of water_charges.amount, so the pair fails. (2) MPS protocol_surface_method (method): T1 area × soda rate vs T3 area × (brush + encapsulation rate), constant multipliers on the same input, so the pair fails. (3) MRS final_labor_basis (method): T2 supervisor labor vs T3 technician + supervisor labor, same-field sums, so the pair fails. Methods that pass every pair: CAT reassessed_ppe (labor-line count input), CAT reassessed_antimicrobial (area input plus floor), CLW removed_scope_inclusion (additive charges plus markup division plus floor), IDR contract_cost_measure / water_cost_measure / code_holdback_cut_rule. The r2-named members (CAT carpet and scrubber, CLW pricing pair, MPS air and regulated, MRS air) are relabelled parameter: closed. |
| CG-19 | CLOSED | Writes are in each tool's own body. |
| CG-20 | **RED (1 member remains)** | CLW duplicate_line_inclusion T2 takes "the duplicate_line credits equal to the amount of an equipment-day line dated on the job's last equipment day, because a duplicated equipment day repeats a line of the same type, day and quantity". water_equipment_day_charge has grain "one row per equipment type per calendar day" and water_evt_equipment_days says "One line is booked per equipment type per calendar day". The duplicated equipment line the tier is written for cannot be booked, so T2 can only fire on a duplicate_line credit whose amount happens to equal an equipment-day line (for example a duplicated 228.00 labor line). The tier's stated case is unreachable and its live case is a decoy match the rule's reason disowns. The billing_error and goodwill T2 lookups are closed under the same grain. |
| CG-21 | CLOSED | MPS and MRS regulated ladders combine the claims file's ordinance_law_limit with the mold job's fields (two records). |

### new findings (r3)

**CG-22 SOURCE-POLICY RED (realism X4, double count; present since r2 and missed in my r2 pass).**
- RSS certified_renovator_labor T2 (commercial) takes "the technician and supervisor labor billed on that date" (the latest containment setup date).
- RSS cleaning_verification_labor T2 (commercial) takes "the technician and supervisor labor billed on that date" (the latest HEPA date).
- When both dates are the same day, which is producible (a one-day containment and HEPA wet-cleanup), the same labor lines are claimed twice in one supplement.
- No sentence prevents it. The housing tiers split by role (supervisor vs technician) and do not double count.
- No consequence on task 0 (single-family).

### observations (r3)
- **O-r3-1.** CLW still says the invoice-built estimate "carried the invoiced mitigation lines". RSS says that estimate leaves out regulated work. They reconcile only if "mitigation lines" is read as excluding the regulated lines. No task value moves.
- **O-r3-2.** The MPS/MRS rationale that on a file with an ordinance-or-law limit the mold job's regulated work "is claimed as a code_upgrade supplement under that limit" is a company routing schedule (R1/R5). I accept it: plausible, keyed on a recorded limit.
- **O-r3-3.** On task 1, the MPS and MRS requests together (4 186.24) exceed the mold room (2 457.15). Each is literally within the base limit; noted again.

### closing_checklist (r3)

Not written: both tasks remain RED.

Post-reveal note: GT equals my blind recomputation on every figure in both tasks. Task 0's GT `order_uniqueness` concedes the RSS/CAT numbering rests on authoring order (T0-R3-1).

**r2 items closed in r3:** CG-1, CG-4, CG-5, CG-7, CG-9, CG-16, CG-17, CG-19, CG-21.

**Still open:**
- CG-6 and CG-18: three members, all present in r2 and missed by my r2 table.
- CG-20: one member.

**New:**
- CG-22 (present in r2, missed).
- Task-level T0-R3-1 (a regression) and T1-R3-1 (present in r2, missed).

VERDICT revision_3: task0=RED task1=RED charter=CG-6,CG-18,CG-20,CG-22

## revision_4

### charter_global_frozen (r4)

- Freeze: 2026-10-25, before any r4 read of tasks/*.json.
- Entry check: the last worklog line reads `REWORK round 4: gates 7/7 green`. I ran `/tmp/erl0079_coord/snapshot.sh insurance_claim_services 4` myself.
- Gate snapshot: `.audit_views/policy/insurance_claim_services/snapshot_r4.txt`. All 7 gates are OK.
- Hashes:
  - claims.extended.yaml = af60992f…a9b3 (changed → policy sections re-derived);
  - task_tools.py = fa915bb8…4e59 (**unchanged** since r3 → `action_binding_and_uuids` and the D-point results of r3 carry forward by reference);
  - view 0.json = 62f8fc7d…f4b (unchanged since r3);
  - view 1.json = 43b6e59d…9d84 (changed).
- The base copy is still byte-identical.
- Read: the full extended charter, both views, only the `## REWORK round 4` section of worklog.md (lines 224–231, no figures, so no contamination), and realism_bar.md.
- Mechanical sweeps clean (compute_basis, policy_source, replaced_by, A10).
- Edges: IDR ← {CLW, CAT, RSS}; **CAT ← RSS restored** (value_input sc_reg_pending, action form, valid fallback); MRS ← MPS. The graph is acyclic.

### r3 items: closure check (r4)

| id | r4 status | evidence |
|---|---|---|
| CG-18 | CLOSED | All-pairs re-check of every method factor. RSS regulated_ppe_line: T1 PPE billed vs T2 the tier's PPE tariff rate (adds a tariff input) vs T3 0 (T1 is not zero across T3's domain: billable tier, no asbestos sampling, no lead) → pass. MPS protocol_air_treatment: T1 containment fee + (scrubber + dehumidifier) × MN(cap, DAYS(containment, clearance request)); T2 scrubber × MN(cap, DAYS(start, request)); T3 dehumidifier × cap; data-selected windows and a min → pass. MRS final_labor_basis: T1 after-hours ÷ multiplier (operation), T2 labor − HVAC cleaning lines with a floor (adds input and operation), T3 labor → pass. RSS rrp_cleanup_scope, MPS surface and MRS-side relabels to parameter are honest. CAT ppe and antimicrobial, CLW removed_scope, and IDR's three methods pass as in r3. The day count is stated: "the containment date counted, the request date not" (B4). |
| CG-6 | **RED (1 member)** | Counts: RSS 5p/1m, CAT 4p/2m, CLW 5p/1m, IDR 3p/3m, MPS 3p/1m. MRS has 4p/1m declared, but its only method, final_labor_basis, is struck for realism (CG-4 below), leaving **0 method**. |
| CG-20 | CLOSED (R6-WAIVED, observation) | CLW duplicate_line_inclusion T2 now takes "the duplicate_line credits equal to the water job tier's moisture mapping fee". The water charter bills moisture mapping "at most once per job", so a second line is a reachable double-keyed duplicate. It is tagged R6 in REWORK round 4 and meets all six conditions: (1) keyed on a recorded fee and credit amounts; (2) plausible; (3) no conflict with an in-force base clause; (4) not X1–X4; (5) XF-clean; (6) the only R6 factor. **R6-WAIVED.** |
| CG-22 | CLOSED | RSS commercial verification labor is 0 when the HEPA date equals the containment setup date. No other line is claimed by two families (swept: the housing tiers split by role, and tear-out, disposal, PPE and cleanup read disjoint charge codes). |

### reopened (r4)

**CG-4 SOURCE-FACTOR RED (realism, XF E1 / realism_bar X4; reopened by the r4 MRS labor rewrite).**
- MRS final_labor_basis T2 (HVAC) now takes "the technician and supervisor labor billed less the duct, air handler and coil cleaning lines billed, never below zero, because the per-vent and per-unit cleaning fees price the crew's cleaning time".
- It subtracts the full dollar amount of the cleaning fees, which also price materials and equipment, from all labor, supervisor labor included. r3's own rationale held that supervisor labor is not priced into those fees.
- HVAC tier figures: air handler 425.00 + coil 285.00 = 710.00 before any vent. Ten vents at 38.50 bring the fees to 1 095.00. An HVAC crew of 8 technician hours (734.00) and 2 supervisor hours (219.00) bills 953.00, so the claimed labor is 0.
- This is exactly realism_bar X4: "performed labor treated as worth nothing", and "larger scope priced lower", since every additional vent cleaned lowers the labor claimed dollar for dollar.
- No consequence on task 1, where the job awaiting clearance is attic growth, but the factor is struck, which drives CG-6.

### observations (r4)
- O-r3-1 (CLW "invoiced mitigation lines" vs RSS "leaves out regulated work") is unchanged.
- O-r3-2 and O-r3-3 are unchanged.
- **R6-WAIVED:** CLW duplicate_line_inclusion T2.

### closing_checklist (r4)

Not written: task 1 remains RED. Task 0 PASSes all four relationships.

Post-reveal note: GT equals my blind recomputation on every figure in both tasks.

**r3 items closed in r4:** CG-18, CG-20 (R6-WAIVED), CG-22, T0-R3-1, T1-R3-1.

**Still open or reopened:**
- CG-4 (reopened): MRS HVAC labor nets the cleaning-fee dollars out of all labor.
- CG-6: MRS is left with 0 method factors as a result.

VERDICT revision_4: task0=PASS task1=RED charter=CG-4,CG-6

## revision_5

### charter_global_frozen (r5)

- Freeze: 2026-10-25, before any r5 read of tasks/*.json.
- Entry check: the last worklog line reads `REWORK round 5: gates 7/7 green`. I ran `/tmp/erl0079_coord/snapshot.sh insurance_claim_services 5` myself.
- Gate snapshot: `.audit_views/policy/insurance_claim_services/snapshot_r5.txt`. All 7 gates are OK.
- Hashes:
  - claims.extended.yaml = 31489ad6…12c0 (changed);
  - task_tools.py = fa915bb8…4e59 (unchanged since r3; tool conclusions carry forward);
  - view 0.json = 62f8fc7d…f4b (unchanged);
  - view 1.json = 56c6e30c…f9e3 (changed).
- The base copy is still byte-identical.
- Read: the full extended charter (r5 copy kept at /tmp/erl0079_pta_ics/claims.extended.r5.yaml for later diffs), both views, only the `## REWORK round 5` section of worklog.md (no figures, so no contamination), and realism_bar.md.
- Unchanged-policy check: the r4 compute expressions of RSS, CAT, CLW, IDR and MPS that carried the r4 closures are present verbatim. Spot-checked: `rs_hepa_date != rs_v_setup`, `sc_reg_pending > 0`, `amount=d_mm_fee`, `MN(mp_cap, DAYS(mp_cdate, mp_rdate))`, `a_init_wh`, `rl_pending: rl_pend_price + rl_pend_scope`, and the RSS PPE tariff tier.
- Sweeps clean: compute_basis verbatim, policy_source and replaced_by in rule, no A10 hit. Edges unchanged; the graph is acyclic.

### r4 items: closure check (r5)

| id | r5 status | evidence |
|---|---|---|
| CG-4 | CLOSED | MRS final_labor_basis now differs only in how the after-hours premium is taken. T1 (attic or crawlspace) takes the after-hours part at the business rate. T2 (HVAC) takes it as billed. T3 (living area or basement) follows the standard method: business rate on a single-family house or condominium unit (`mr_ah_cut`), as billed on a multifamily unit or commercial property. No cleaning line enters labor. Labor is never below the business-rate value of the hours billed and rises with every hour billed, so realism_bar X4 no longer applies. These are keyed property-type and location schedules (R1). |
| CG-6 | CLOSED | MRS method all-pairs test. T1 tech + sup − ah + ah ÷ multiplier (a division). T2 tech + sup. T3 tech + sup − `mr_ah_cut`, a conditional pick on property type. T1/T2 differ by an operation, T2/T3 by an input plus a conditional pick, T1/T3 by a conditional pick. All pass XF A7. A1 holds: the factor binds only `mr_loc_lb` and `mr_labor` and reads plain bindings. MRS 4p/1m. Counts for all six policies: RSS 5/1, CAT 4/2, CLW 5/1, IDR 3/3, MPS 3/1, MRS 4/1. |

### new defects / regressions (r5)

None found.
- The MRS baseline sentence states its property-type default without denying the location tiers (CG-1 class clean).
- Rule = compute for `mr_ah_cut`.
- No other policy changed.

### observations (r5)
- O-r3-1, O-r3-2 and O-r3-3 are unchanged.
- R6-WAIVED: CLW duplicate_line_inclusion T2, unchanged from r4.

## closing_checklist (r5)

Written after both tasks PASS in revision_5.

- **Files:** the per-task audit files 0.md and 1.md map one-to-one to tasks/0.json and 1.json, with _difficulty.md alongside them. Revisions r1–r5 are preserved in order; old text is untouched and each revision is appended. Every comparison section in r5 carries a PASS.
- **Coverage:** all six extended policies are covered. Scopes are pairwise disjoint and complete: task 0 = {IDR, CLW, CAT, RSS}; task 1 = {MRS, MPS}. Each scope spans its whole tree.
- **Tools:** each task tool is closed to its policy, with an independently generated uuid8 that stays frozen (ec41bed4, 86febceb, d9a0c26a, 7e4d140d, d117c1f9, e2edbc44).
- **Trees:**
  - task 0: 3 prerequisite problems, 3 value_input edges into the root plus RSS → CAT; the customer's write is IDR (owner=user).
  - task 1: 1 prerequisite problem, 1 value_input edge; the customer's write is MRS (owner=user).
  - No cycle; the difficulty-wide graph is a DAG.
- **Factors:**
  - Every computation declares a self-sufficient baseline and 4–6 factors with at least 2 parameter and 1 method that pass XF A7 (RSS 5/1, CAT 4/2, CLW 5/1, IDR 3/3, MPS 3/1, MRS 4/1).
  - Each task carries at least 1 multi-source factor (task 0 CLW removed_scope; task 1 the regulated ladders) and at least 1 cross-difficulty factor (water/rebuild; mold).
  - Every factor bears weight on its task's world, and each whole baseline gives a definite number different from gold.
  - One tier is R6-WAIVED (CLW duplicate_line_inclusion T2).
- **Gates:** re-run once on the final form via snapshot_r5.txt, 7/7 OK. check_traceability stays deferred to after render, per the coordinator.
- **Open observations, not REDs:**
  - O-r3-1: CLW "invoiced mitigation lines" vs RSS "leaves out regulated work".
  - O-r3-2: ordinance-or-law routing of mold regulated work.
  - O-r3-3: MPS + MRS together exceed the mold room.

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

### charter_global_frozen (r6)

- Freeze: 2026-10-25, before any r6 read of tasks/*.json.
- Entry check: the last worklog line reads `REWORK round 6: gates 7/7 green`. I ran `/tmp/erl0079_coord/snapshot.sh insurance_claim_services 6` myself.
- Gate snapshot: `.audit_views/policy/insurance_claim_services/snapshot_r6.txt`. All 7 gates are OK.
- Hashes:
  - claims.extended.yaml = c4a016b1…dc00 (changed);
  - task_tools.py = fa915bb8…4e59 (unchanged);
  - views 0.json = 62f8fc7d…f4b and 1.json = 56c6e30c…f9e3 (both unchanged since r5).
- The base copy is still byte-identical.
- Read: audits/render_source/insurance_claim_services/render_r1.md (permitted by the coordinator), only the `## REWORK round 6` section of worklog.md (no figures), realism_bar.md, and the charter.
- **Structural diff r5 → r6** (my kept copies /tmp/erl0079_pta_ics/claims.extended.r5.yaml and .r6.yaml), exhaustive:
  - scope sentences of RSS, CAT, CLW, MPS and MRS;
  - one IDR compute expression (`rl_sup_released`);
  - no factor, ladder, baseline, compute_basis, edge or other compute changed.
- Sweeps clean.
- **Relation to my earlier revisions:** the renderer's findings 1a, 1b, 2 and the A6-T2 note were all present in the charter I passed in r5.
  - 1a: I noted a missing contract-count test for CLW in r2 scratch notes but never reported it.
  - 1b, 2 and A6-T2: I missed them.
  - I record these as misses of my r2–r5 audits.

### renderer findings: closure check (r6)

| item | r6 status | evidence |
|---|---|---|
| 1a (B7, CLW rebuild reads) | CLOSED | The CLW scope now reads "…and at most one reconstruction contract, which, when held, is linked to the file". The customer-wide `XSUM`/`XLATEST` reads of rebuild_payments and rebuild_charges are therefore this file's contract, and with no contract `r_co_last` is '' (removed scope 0) and `cp_signed` is '' (multiplier 1). |
| 1b (B7, water reads) | CLOSED | RSS, CAT and CLW scopes now read "holds exactly one water mitigation job, and that job is linked to the file". Class sweep of every customer-wide read: IDR has "exactly one water mitigation job and exactly one reconstruction contract, both linked to the file" (covers its water and rebuild XSUMs). MPS and MRS have "exactly two mold jobs, both linked to the file", and their mold reads are keyed by `mold_job_id` or `status`. No fire, contents or account read exists. |
| 2 (B1, IDR supplement_depreciation_paid) | CLOSED | Compute is now `rl_sup_wh2 if rl_sup_paid >= rl_sup_amt else …`. With no supplement approval, amount 0 and withheld 0 give 0.00, as the rule reads. With approvals present, behaviour is unchanged. Class sweep: I compared every ladder's compute guards with its rule text and found no other compute-only condition. |
| A6-T2 note (CLW water_line_pricing_basis, contract_scope_pricing_basis) | **RED (CG-23; R6 waiver not available)** | See below. |

### findings (r6)

**CG-23 SOURCE-FACTOR RED (XF A6, test T2; missed in my r2–r5 passes).**
- Members:
  - CLW water_line_pricing_basis: `cw_wmult` multiplies `cw_water_credits`.
  - CLW contract_scope_pricing_basis: `cw_cmult` multiplies `cw_removed`.
- With every other factor at its baseline, all four credit families are 0, so `cw_priced` = 0 × multiplier and neither factor can move `result` in any world. A6 T2 requires "some producible world exists where that factor moves `result` with every other factor at baseline". A6 itself names the shape: "never split one charge into two factors that multiply (count x price) — the other is 0 at baseline".
- The reworker tags both R6. realism_bar.md R6 requires **all** of six conditions, and condition (5) is "XF-clean (A1-A10, B, C, D)". These factors fail A6 by construction, as the REWORK note itself concedes ("T2 cannot hold by construction"), so they are not R6-WAIVABLE. Conditions (1)–(4) hold: recorded keys, plausible conversions the claims charter states, no base conflict, not X1–X4.
- Exhaustive A6-T2 sweep of all 33 factors: every other factor contributes additively, or as a measure or deduction against a baseline quantity that is non-zero in some producible world, so these two are the only members.
  - RSS: additive families.
  - CAT: additive differences.
  - CLW inclusions and removed scope: additive at multiplier 1.
  - IDR: deductions and cost measures.
  - MPS and MRS: additive families under the room.
- If both were struck, CLW would keep 4 factors (3p/1m), which still meets the 4–6 floor. The drawn count of 6 is a gate and draw matter outside this audit.
- Bears on task 0.

### observations (r6)
- CLW duplicate_line_inclusion T2 remains R6-WAIVED (meets all six conditions, A6-clean).
- O-r3-1, O-r3-2 and O-r3-3 are unchanged.
- The RSS scope sentence now runs "…and that job is linked to the file and on which no billing_error…". It is a run-on clause but has a single reading.

### closing_checklist (r6)

The r5 checklist is suspended: task 0 is RED on CG-23. Task 1 still meets every item of the r5 checklist.

Post-reveal note: GT is unchanged and equals my figures in both tasks.

**Renderer items closed:** 1a, 1b, 2.

**Open:** CG-23 (A6-T2 note, 2 members, not R6-waivable).

VERDICT revision_6: task0=RED task1=PASS charter=CG-23

## revision_7

### charter_global_frozen (r7)

- Freeze: 2026-10-25, before any r7 read of tasks/*.json.
- Entry check: the last worklog line reads `REWORK round 7: gates 7/7 green`. I ran `/tmp/erl0079_coord/snapshot.sh insurance_claim_services 7` myself.
- Gate snapshot: `.audit_views/policy/insurance_claim_services/snapshot_r7.txt`. All 7 gates are OK.
- Hashes:
  - claims.extended.yaml = 8f8e4d5e…739c (changed);
  - task_tools.py = fa915bb8…4e59 (unchanged);
  - view 0.json = 3c13ffb8…ea80 (changed);
  - view 1.json = 56c6e30c…f9e3 (unchanged).
- The base copy is still byte-identical.
- Read:
  - the charter (kept at /tmp/erl0079_pta_ics/claims.extended.r7.yaml);
  - both views;
  - only the `## REWORK round 7` section of worklog.md (no figures);
  - realism_bar.md and render_r1.md.
- The coordinator's CG-23 ruling is applied: the drawn count is gate-enforced; no T2 waiver is granted for factors acting only through other factors' outputs; the accepted route is that the standard method defines the credit families at a stated default, inclusion factors narrow or widen them, and pricing factors act on that baseline quantity.
- **Structural diff r6 → r7:** only claims_ext_credited_line_writeoff changed (rule, compute_basis, compute, baseline, factors). The other five policies are identical. Sweeps are clean (compute_basis verbatim, edges in rule, no A10 hit).

### closure check (r7)

| id | r7 status | evidence |
|---|---|---|
| CG-23 | CLOSED (per the coordinator's route) | CLW's baseline is now "The standard method takes every credit recorded on the water job, that is its billing_error, duplicate_line and goodwill credits, and every change order credit posted on the reconstruction contract, at their recorded amounts and the company's own prices…". Each inclusion factor's fall-through is the standard family (`cw_err`, `d_all`, `g_all`, `r_co`; these are plain bindings outside the factors' binding lists, so A1 holds), and its other tiers narrow the family. The pricing factors multiply families the baseline already makes non-zero whenever credits exist, so A6 T2 holds. On task 0, with the other factors at baseline, the water multiplier alone gives 501.85 and the contract multiplier alone 490.47, against a whole-baseline of 451.05. A6 T2 also holds for the four inclusion factors. Ladder text = compute on every boundary: "on or before the drying complete date" is `<=`, "before the invoiced_date" is `<`, the change-order credit "on or before the estimate submission date" is `<=`, and an additive charge "on or after it" is `>=`. With no change-order credit, removed scope is 0. A7: removed_scope_inclusion T1 0 vs T3 `r_co` (non-zero on T1's domain); T2 adds the charges and markup with a floor; all pairs pass. The combination sentence is generic and ordered ("families the standard method takes, each as narrowed below and each converted … then approval … held … rounded"). The baseline sentence is labelled "The standard method" and denies no factor (CG-1 class clean). |
| render 1a / 1b / 2 | STAY CLOSED | The r6 scope sentences and the `rl_sup_released` guard are unchanged in r7 (the five other policies are identical; CLW's scope sentence is unchanged). |
| R6 | — | Only CLW duplicate_line_inclusion T2 is R6-tagged. It still meets all six conditions, including (5), XF-clean: A6 T1 and T2 hold, since the factor's own family moves the result. **R6-WAIVED.** |

### new defects / regressions (r7)

None found in the charter. Task-0 seed checks are in 0.md.

### observations (r7)
- O-r3-1, O-r3-2 and O-r3-3 are unchanged.
- The rebuild owner_upgrade change order's "upgrade deposit share … due before the upgrade is ordered" has no separate payment row. This is unchanged since r1, and no factor reads it.

## closing_checklist (r7)

Written after both tasks PASS in revision_7. The r5 checklist, suspended in r6, is restated on the final form.

- **Files:** 0.md and 1.md map one-to-one to the tasks, with _difficulty.md alongside them. Revisions r1–r7 are preserved and appended in order. Both r7 comparisons PASS.
- **Coverage:** all six extended policies are covered. Scopes are disjoint and complete (task 0 = {IDR, CLW, CAT, RSS}; task 1 = {MRS, MPS}). Tools are closed to their policies, with independently generated frozen uuid8s.
- **Trees:**
  - task 0: IDR ← {CLW, CAT, RSS}, CAT ← RSS; 3 prerequisite problems, 3 value_input edges into the root; the customer's write is IDR (owner=user).
  - task 1: MRS ← MPS; the customer's write is MRS (owner=user).
  - The graph is a DAG.
- **Factors:**
  - Every computation has a self-sufficient, standard-labelled baseline and 4–6 factors (RSS 5p/1m, CAT 4p/2m, CLW 5p/1m, IDR 3p/3m, MPS 3p/1m, MRS 4p/1m).
  - Every method passes XF A7, and every factor passes A6 T1 and T2.
  - Multi-source and cross-difficulty factors are present in each task.
  - Each whole baseline is a definite number different from gold (task 0: CLW 451.05, RSS 770.00, CAT 0.00, IDR 3797.38; task 1: MPS 1129.44, MRS 0.00).
  - R6-WAIVED: CLW duplicate_line_inclusion T2 only.
- **Renderer findings:** 1a, 1b and 2 stay closed; the A6-T2 note is closed as CG-23.
- **Gates:** 7/7 OK on the final form (snapshot_r7.txt). check_traceability stays deferred to after render.
- **Observations only:** O-r3-1, O-r3-2, O-r3-3, and the owner_upgrade deposit-share row.

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN

## revision_8

### charter_global_frozen (r8)

- Freeze: 2026-10-25, before any r8 read of tasks/*.json.
- Entry check: the last worklog line reads `REWORK round 8: gates 7/7 green`. I ran `/tmp/erl0079_coord/snapshot.sh insurance_claim_services 8` myself.
- Gate snapshot: `.audit_views/policy/insurance_claim_services/snapshot_r8.txt`. All 7 gates are OK.
- Hashes:
  - claims.extended.yaml = c798ee32…a0cc (changed);
  - task_tools.py = fa915bb8…4e59 (unchanged);
  - both views unchanged since r7 (0.json 3c13ffb8…ea80, 1.json 56c6e30c…f9e3).
- The base copy is still byte-identical.
- Read: render_r1.md and render_r2.md, only the `## REWORK round 8` section of worklog.md (no figures), realism_bar.md, and the charter (kept at /tmp/erl0079_pta_ics/claims.extended.r8.yaml).
- **Structural diff r7 → r8:** only claims_ext_insured_depreciation_release changed. Its rule changed in two sentences ("dwelling scope_omission and price_variance supplements"; "the file's dwelling supplement approvals" twice), along with compute (`rl_pend_scope` and `rl_pend_price` now filter coverage_part='dwelling'), compute_basis and baseline. The other five policies are identical.
- **Relation to my earlier revisions:** the code-holdback coverage mismatch is the same item I recorded in r1 under CG-9 (`rl_sup_withheld` dwelling filter vs "the file's supplement approvals"). In r2 I marked the r1 CG-9 members closed without re-checking this sentence. That was wrong, and the item stayed open from r2 to r7.

### closure check (r8)

| item | r8 status | evidence |
|---|---|---|
| render_r2 code_holdback_cut_rule (B1, coverage part) | CLOSED | The rule now reads "when the depreciation withheld on the file's dwelling supplement approvals is above … the whole depreciation withheld on the dwelling supplement approvals", matching `rl_sup_wh` (approval_type supplement, coverage dwelling). The compute_basis quotes are verbatim. |
| class: filters in compute absent from the rule, and the reverse | CLOSED | My own exhaustive sweep of all 198 data reads across the six computes (scratch listing /tmp/erl0079_pta_ics/reads_r8.txt) compared each filter with the rule wording: coverage_part, approval_type, event_type, payment_type, supplement_reason, adjustment_reason, charge_code, rate_window, status, source/related ids, dates. Results are listed below. |
| render_r1 1a / 1b / 2; CG-23 | STAY CLOSED | These policies' scope, compute and baseline are unchanged in r8 (diff). The coordinator's CG-23 ruling remains satisfied. |

**Class sweep results:**
- **IDR:**
  - every dwelling-filtered read is named "dwelling" in the rule: withheld, release payments, approvals, initial approval and its withheld, ACV, advances, supplement approvals and withheld, supplement payments, and now pending scope_omission and price_variance;
  - unfiltered reads are unfiltered in the rule: "every write-off posted on the file's approvals"; "change order charges posted on the contract"; "draw payments and insurance postings"; the credit reasons; "every charge … other than late fees and card surcharges";
  - "awaiting the carrier's decision" on the pending sums rests on the stated scope test ("no price_variance or scope_omission supplement has yet been decided").
- **CLW:** initial approval "initial dwelling approval" ✓; write-offs keyed to that line ✓; credit reasons named ✓; equipment day and last day ✓; change-order credits and charges ✓ (every booked change-order charge is additive, since a deductive change order is booked as a credit, so "additive change order charges" = all charges).
- **CAT:** charge codes and quantities named ✓; the pending scope_omission read rests on its scope test; no coverage filter on either side.
- **RSS:** charge codes and the "latest" containment and HEPA dates named ✓.
- **MPS / MRS:** every read keyed to "the job awaiting clearance" (status filter) or its tier ✓; after-hours labor `rate_window` named ✓. The supplement-approval sum ("mold amounts already approved") and the pending mold requests rest on the stated scope tests (every supplement approval decides a mold_remediation supplement; loss_type not mold; none decides one naming the job awaiting clearance).
- **No remaining member.**

### new defects / regressions (r8)

None. No scored value moves on either world: task 0 carries only dwelling requests and approvals, and task 1 is untouched.

### observations (r8)
- O-r3-1, O-r3-2 and O-r3-3 are unchanged, as is the owner_upgrade deposit-share row.
- R6-WAIVED: CLW duplicate_line_inclusion T2 only.

## closing_checklist (r8)

The r7 checklist is restated on the final form. Every item still holds:
- files one-to-one, revisions r1–r8 appended;
- scopes disjoint and complete; tools closed;
- trees with customer writes;
- factor floors, A6, A7 and baselines as r7;
- render_r1 and render_r2 items closed, and the filter class swept empty.

Gates: 7/7 OK on snapshot_r8.txt. check_traceability stays deferred to after render.

VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN

## revision_9

### charter_global_frozen (r9)

- Freeze: 2026-10-25, before any r9 read of tasks/*.json.
- Entry check: the last worklog line reads `REWORK round 9: gates 7/7 green`. I ran `/tmp/erl0079_coord/snapshot.sh insurance_claim_services 9` myself.
- Gate snapshot: `.audit_views/policy/insurance_claim_services/snapshot_r9.txt`. All 7 gates are OK.
- Hashes:
  - claims.extended.yaml = d6311572…6ed9 (changed);
  - task_tools.py = fa915bb8…4e59 (unchanged);
  - view 0.json = d76106bc…e4cf (changed);
  - view 1.json = 1257da1a…b9e6 (changed).
- The base copy is still byte-identical.
- Read:
  - audits/policy_kb/insurance_claim_services/_difficulty.md (SRC-1..SRC-4);
  - the published docs/water/ and docs/mold/ for the policies that price the seeded rows (hub, baseline and every factor document);
  - render_r1.md and render_r2.md;
  - only the `## REWORK round 9` section of worklog.md (no figures);
  - realism_bar.md.
- I read no sibling tasks directory; the docs' meta "source" paths were not followed.
- **Structural diff r8 → r9** (kept copies .r8/.r9): wording only, with no compute change:
  - RSS cleaning_verification_labor sentence (SRC-4);
  - CAT "rate billed" → "the dispatch tier's rate" in four ladders (rule, compute_basis and ladder text);
  - MRS regulated sentence drops "as the protocol supplement prices it" (SRC-4).
- CLW, IDR and MPS are unchanged. Sweeps clean.

### SRC items: closure check (r9)

| item | r9 status | evidence (my own re-pricing from the published docs) |
|---|---|---|
| **SRC-1** (task 0 water rows) | CLOSED | All three rows priced under the published water extended pricing for water job cb1a3090 (Gray Water - Standard Loss, recorded category_3, class_2, single-family, 1974, opened on the loss date). **Final HEPA** (water_ext_final_hepa_vacuum): floor = pad 520 + affected 860 (carpet detach-and-reset with pad) = 1 380; cut-cavity wall = flood cut 140 lf × 4 (Category 3) = 560; plate = baseboard 140 × 0.5 (Class 2) = 70; contents 0; regulated pass factor 2 (pre-1978, lead-safe line); residue factor none (opened on the loss date); (1 380 + 560 + 70) × 2 = **4 020 sq ft** × 0.31 = **1 246.20**, dated the drying complete date 2026-05-09 ✓. **Tear-out antimicrobial** (water_ext_tearout_antimicrobial): treated floor 860 + 520 = 1 380; class-based wall area 140 × 2 = 280; coverage factor none; **1 660 sq ft**; rate 0.36 × 1.3 wet-wipe (pre-1978, lead line) = 0.468 → **0.47**; **780.20**, dated the latest flood cut 2026-05-05 ✓. **Tear-out debris haul-off** (water_ext_tearout_debris): flooring 520 ÷ 600 + drywall 140 ÷ 100 (Class 2) + trim ⌈140 ÷ 150⌉ = 1 (pre-1978, rounded up on its own) = 3.27 → **4 loads**; per-load rate 214 × 1.25 sanitation (Category 3 with pad and flood cut); no haul-window multiplier (the flood cut is not on the opened date); no access multiplier (single-family) → **267.50**; **1 070.00**, dated 2026-05-05 ✓. Every other water line is at the tier's unit rate × quantity, as the published hub keeps them: service call 219; moisture mapping 145; thermal 95; extraction 0.78; asbestos 425; lead 345; containment 395; flood cut 2.85; baseboard 1.12; pad 0.48; carpet detach 0.71; tech 78.50; sup 96.40; PPE 28.75; equipment 28.50 / 95.40 over 5 days within the cap; monitoring 84 with the set day waived. Ledger: final 10 435.85 = sum of 36 lines; credits 329.40 + check 10 106.45 → balance 0. The published water drying deposit applies to self-pay only; the insured's share is a customer-run payment, and the job was paid in full by the insured's check, so no row is missing. Claims carrier payments are insured_only, which the PA tier allows. Rebuild has no published docs, so it is checked against the base charter as in r7 ✓. |
| **SRC-2** (task 1 mold rows) | CLOSED | **Job 78c1f5e2** (Attic, 96 sq ft, 1972, multifamily, no linked water job, HDP file with no PA and no referral, opened 2026-09-21, scheduled 2026-10-08, signed 2026-09-29). **Work-plan visit** (mold_ext_workplan_line): base 2 h, and no factor applies (no water job; no PA or referral; lead time 17 days); 2 × 106.90 = **213.80**, dated the opened date ✓. **Pre-removal asbestos sampling** (mold_ext_presample_line): tier fee 425 (no linked water job, so no reuse) + insulation set 165 (attic); no other factor (no PA, no water job, lead time 17 days, no crew credit); **590.00**, dated the opened date ✓. **Haul-off** (mold_ext_disposal_line): insulation only, 96 ÷ 160 → 1 load × tier fee 238 (no water job) + one-trip 75 (the latest insulation removal 2026-10-09 is not the containment date); no wet charge; **313.00**, dated 2026-10-09 ✓. **Signing deposit** (mold_ext_signing_deposit): 900 − coverage credit 7 000 (approved file, mold sublimit 7 000) floored to 0, + insured-route raise 200 (no PA; HDP takes no direct payment) + lead dust-wipe 135 (no water job, pre-1978) + charges booked by signing (590.00 + 213.80); notice 9 days, so no raise; = **1 138.80** on 2026-09-29 ✓. Balance due 4 685.74 − 1 138.80 = **3 546.94** ✓. **Job 13b3e213** (Limited, 26 sq ft, living area): work plan 2 × 102.80 = **205.60** (2026-06-30) ✓; sampling 425 (age 54 < 75, no other factor), dated 2026-06-30 ✓; haul-off: drywall 64 and insulation 32 as separate streams ⌈64 ÷ 160⌉ + ⌈32 ÷ 120⌉ = 2 × 214 = **428.00**, no trip charge (removal on the containment date 2026-07-13) ✓. Signing deposit 2026-07-06 = 0 (400 less the coverage credit; the file's estimate was submitted 2026-07-06, so the 50% credit of 3 500 applies under the producible same-day order estimate-then-signing) + 200 + 135 + 630.60 = **965.60** ✓. Final 4 827.97 = sum of charges; payments 965.60 + 3 721.70 + credits 140.67 → 0 ✓. |
| **SRC-3** (task-0 read-objective prose) | checked at reveal (below) | — |
| **SRC-4** (factor text naming another factor or policy) | CLOSED | The RSS verification sentence now states its own record test ("a HEPA vacuuming date that is also the service date of the job's latest containment setup line takes none"). The MRS sentence no longer names the protocol supplement. Sweep: no ladder or rule sentence names another factor's quantity or another policy, apart from the declared prerequisite sentences and the sibling naming the overwrites require. |
| rate-wording class | CLOSED | CAT's four "rate billed" phrases now read "the dispatch tier's rate", which matches the CPARAM reads (they would now diverge on the 0.47 wet-wipe antimicrobial line). Sweep: no other "rate billed" or "billed rate" phrase in any rule. |
| render_r1 / render_r2 items, CG-23 | STAY CLOSED | Those compute expressions are unchanged (diff). |

### new defects / regressions (r9)

None.

### observations (r9)
- MPS prices regulated work at the tier's asbestos sampling fee (425.00) while the published mold sampling line on the same job is 590.00. MPS is a protocol-based figure from tier rates by its own rule, so this is not a defect.
- The work-plan visit is booked as a supervisor_labor line, so MRS's labor family counts it. That is consistent with "the technician and supervisor labor billed on that job".
- O-r3-1, O-r3-2 and O-r3-3 are unchanged.
- R6-WAIVED: CLW duplicate_line_inclusion T2 only.

## closing_checklist (r9)

The r7/r8 checklist holds on the r9 form:
- files one-to-one, revisions r1–r9 appended;
- scopes disjoint and complete; tools closed;
- trees, customer writes and DAG unchanged;
- factor floors (RSS 5/1, CAT 4/2, CLW 5/1, IDR 3/3, MPS 3/1, MRS 4/1), A6, A7, and baselines definite and different from gold;
- KB-surfaced SRC-1..SRC-4 closed;
- every other-product row the gold reads re-priced against the published water and mold docs, and the rebuild rows against the base charter (no rebuild docs published).

Gates: 7/7 OK on snapshot_r9.txt.

VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN

## revision_10

### charter_global_frozen (r10)

- Freeze: 2026-10-25, before any r10 read of tasks/*.json.
- Entry check: the last worklog line reads `REWORK round 10: gates 7/7 green`. I ran `/tmp/erl0079_coord/snapshot.sh insurance_claim_services 10` myself.
- Gate snapshot: `.audit_views/policy/insurance_claim_services/snapshot_r10.txt`. All 7 gates are OK.
- **Hashes:** claims.extended.yaml = d63115724bc1eaed… and task_tools.py = fa915bb8a0e6cb1a…, **both unchanged since r9**, as the coordinator required. View 0.json = b72e4c5e…d9ff (changed); view 1.json = 1257da1a…b9e6 (unchanged).
- **On those hash grounds every charter-global section of revision_9, and the r1–r9 conclusions it carries, stands by reference.** Nothing in the charter or the tools can have moved.
- Read:
  - only the `## REWORK round 10` section of worklog.md (no figures);
  - the KB items SRC-5 and SRC-6 in audits/policy_kb/insurance_claim_services/_difficulty.md (revision_3);
  - the published docs/rebuild/ (deductive change-order policy: hub, baseline and all factor documents; final-draw policy; draw request, draw payment and permit-fee policies; Texas retention factor);
  - realism_bar.md, including RULE-6 and RULE-7.

### SRC items: closure check (r10)

| item | r10 status | evidence (my own re-pricing from docs/rebuild) |
|---|---|---|
| **SRC-5** (deductive change-order credit, task 0) | CLOSED | CO 1 (deductive, carpet_install 180 sq ft, credit posted 2026-08-05) was the only proposal awaiting signature (CO 2 was created 2026-08-06), so the deductive credit rules apply. Change-order part 0 (no signed non-deductive carpet_install change order); contract part 180 × 1.42 (tier rate) = 255.60. Cleaning and treatment returns apply only to drywall or insulation removals; no O&P is returned (change-order part 0). Construction started 2026-06-10, on or before the signing date, so the field-remeasure deduction of 95.00 applies. Credit = **160.60**, and both rebuild_payments 5ac775ab and change order 98e3a87f carry 160.60 ✓. |
| **SRC-6** (permit expediting once per permit type) | CLOSED | Building and electrical permit fees → two expediting lines at the Standard 145.00 (93f1dad6 building, eeb101fc electrical, both 2026-06-02) ✓. |
| draws, payments, final invoice | CLOSED (re-priced consistently) | Draw 3 = 30% of the current sum on 2026-08-12 (31 850 + 151.20 − 160.60 = 31 840.60) = **9 552.18** ✓. The final draw is customer-funded (carrier payments insured_only, so the funding route is customer) = remainder 31 840.60 − 3 185 − 9 555 − 9 552.18 = **9 548.42**. On a customer-funded final draw no pass-through line is added and no hold or Texas final retainage applies ✓. Final invoice = 31 850 + 412 + 145 + 96 + 145 + 450 + 395 + 151.20 = **33 644.20** ✓. Pass-through balance 33 644.20 − 31 840.60 − 160.60 = **1 643.00**, paid 2026-10-08 before the 2026-10-10 due date ✓. Every draw was paid by check on or before its due date, and the balance closes at 0. |
| other rows (exhaustive) | unchanged and consistent | Rebuild contract sum, permit fees at cost, plan drawing 450, lead-safe 395, CO 2 151.20 ((3.95 − 3.25) × 180 × 1.2, at least the minimum), draws 1–2. Water rows are byte-identical to r9 (sum 10 435.85, credits 329.40, payment 10 106.45; r9 re-pricing stands). Task 1 view unchanged (r9 re-pricing stands). No contents rows exist in either world. Own-category history is unchanged. |

### new defects / regressions (r10)

None. The charter and tools are byte-identical; only task-0 seeds and proof text changed.

### observations (r10)
- The published Texas owner-retention text says the owner "holds back itself from its own payments of the customer-funded draws". The seed shows customer-funded draws paid in full before the retention period ended. I read this as the owner's statutory right, which this owner did not exercise, not as a booking the company makes; the KB audit read it the same way. It is not a RED.
- O-r3-1, O-r3-2 and O-r3-3 are unchanged.
- R6-WAIVED: CLW duplicate_line_inclusion T2 only.

## closing_checklist (r10)

The r9 checklist holds on the r10 form: the charter and tools are byte-identical; KB-surfaced SRC-5 and SRC-6 are closed; every other-product row the gold reads is re-priced against the published rebuild, water and mold docs.

Gates: 7/7 OK on snapshot_r10.txt.

VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN

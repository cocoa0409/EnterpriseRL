# Policy-task audit — cni_contract_care / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (round 1), not the author of the artifacts.
- Freeze time: 2026-10-04T16:25Z (wall clock). Written before any task's GT was revealed; nothing in this section derives from a revealed GT field.
- Frozen inputs (sha256, recomputed by the auditor and equal to `.audit_views/policy_task/cni_contract_care/HASHES.txt`):
  - `tasks/cni_contract_care/cni.extended.yaml` 9887dd903e885780ad5f710888fd50b4d4b87ff9882b84a37d57786862edd9c9
  - `tasks/cni_contract_care/task_tools.py` 661a0e129e6c887ecab1a12bb1f2de7ad3bf49015a81c7096543e977f6329e67
- Fields permitted: blueprint (`blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/cni.yaml`, plus targeted greps of `products/bizgas.yaml` and `products/bizpower.yaml` for cross-difficulty consistency), the full extended charter, the full task tool module, the DSL evaluator semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (MONTHS/DAYS/within_months only), and the masked views `task_0.view.json` / `task_1.view.json` (task_index, frozen_time, user_scenario, initial_state).
- Fields masked and unread at freeze: every other key of `tasks/0.json` and `tasks/1.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), both worklogs, any other audit.
- Entry conditions (Step 0): gate snapshot supplied by the orchestrator — check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cache_diff INFO; check_cross_fire SCOPE OK; check_traceability deferred (KB not rendered). Masked views and hashes present. Entry conditions met; the deferred traceability gate is noted, not a defect of this audit.

### policy_conflict_scan

Base section of the extended charter is verbatim equal to `blueprint/products/cni.yaml` (all ten top-level keys compared structurally: equal).

Extended policies (7) and their write surfaces:

| id | subject | target_tool (owner) | computes | trigger | prerequisite |
| --- | --- | --- | --- | --- | --- |
| P1 cni_ext_termination_security | cni_deposit_post | post_termination_security_b7051944 (user) | amount_usd | state_due | P2 (value_input), P3 (state_gate) |
| P2 cni_ext_noticed_termination_damages | cni_etf_charge | bill_noticed_termination_damages_6fb56a64 (agent) | amount_usd | state_due | [] |
| P3 cni_ext_preflow_termination_damages | cni_etf_charge | bill_preflow_termination_damages_230b7c5e (agent) | amount_usd | state_due | [] |
| P4 cni_ext_anniversary_security_review | cni_deposit_post | remit_review_deposit_f4180914 (user) | amount_usd | state_due | P6 (value_input), P7 (value_input), P5 (state_gate) |
| P5 cni_ext_contract_exit_damages | cni_etf_charge | bill_contract_exit_damages_2ce88247 (agent) | amount_usd | state_due | [] |
| P6 cni_ext_passthrough_block_rebill | cni_adjustment | credit_block_line_fffec1b8 (agent) | amount_usd | on_request | [] |
| P7 cni_ext_passthrough_index_rebill | cni_adjustment | credit_index_line_725777e6 (agent) | amount_usd | on_request | [] |

Overlap scan:
- Subjects overlap three ways (P1/P4 on cni_deposit_post; P2/P3/P5 on cni_etf_charge; P6/P7 on cni_adjustment) but the eligible holding states are pairwise disjoint: P1 termination_pending from written notice; P4 active with anniversary within 30 days; P2 termination_pending from written notice; P3 closed / terminated_before_flow; P5 closed / final_billed or switched_to_other_supplier before contract_end_date; P6 the pass-through cycle's block_energy_charge line; P7 the pass-through cycle's index_energy_charge line. No situation is claimed by two extended policies.
- Time anchors: all "twelve months before the handling date" windows are evaluated by posted_date against frozen_time; DSL semantics `0 <= MONTHS(posted, NOW) < 12`. No anchor conflicts between policies.
- Cross-category read boundaries: P1/P2 read bizgas (same premise), P3 reads bizpower (same premise), P4 reads bizpower (all of the business's small-business agreements). Each read is stated in its rule.
- Terminal states: P1/P4 add a cni_deposits post row; P2/P3/P5 add an early_termination_fee line; P6/P7 add a rebill_credit line. None changes a contract status; no two writes target the same dedup key in one world.
- Base/extended conflicts: see `override_declarations` (two undeclared overrides found).
- Scope exclusivity / completeness: the prerequisite graph has exactly two connected components, {P1,P2,P3} and {P4,P5,P6,P7}; with M=2 the only partition that keeps each tree whole is one component per task, which covers all 7 extended policies once. Whether `charter_scope` in each task actually says this is checked only after reveal (task files).

### rule_compute_equivalence

Swept every compute binding against `compute_basis` and back against the rule, policy by policy.

- P1: every binding has a verbatim basis; the rule sentences on grade share, notice lead, monthly-rate ladder, exposure ladder, tenure coverage, gas relief, requirement/held/rounding are each implemented. Sweep back: no rule sentence lacks compute. The 3-month tier is implemented as `(cyc12 >= 3 and cyc3 > 0)`; the rule says "three to eleven cycles give the net charges posted in the latest three months divided by the cycles posted in those three months" and is silent on a window with 3-11 cycles in twelve months but zero in the latest three, where compute falls to `lst_net` (the fall-through tier). Observation O-1: compute decides a case the rule leaves undefined (no task world reaches it).
- P2: equivalence holds. `months_std` = `0 - MONTHS(end, term)` reproduces "plus one when the day of month of contract_end_date is later"; `months_whole`/`term_left` = MONTHS(term, end). Load factor uses kwh12 ("the twelve months' kWh"), as the rule says.
- P3: equivalence holds; `deposits_posted` counts posts on the contract; `confirmed` reads utility_confirmation_date.
- P4: equivalence holds; `term_left` = MONTHS(NOW, contract_end_date); `idx_share` denominators are window supply kWh as stated.
- P5: equivalence holds; `days_w` sums billing_days of the counted cycle lines exactly as "the billing_days of the counted cycles"; `final_posted` counts supply lines whose billing_period_end equals close_date.
- P6/P7: equivalence holds; pass-through cycle = billing_period_start equal to the latest regulatory_pass_through effective_date; carrying period and rate implemented as stated.
- Rounding: every rule says "rounded half up"; the evaluator's `RND` is Python `round` on binary floats. Observation O-2: on an exact half-cent tie the evaluator and the rule can differ. No tie arises in either task world on the auditor's recomputation (all final raw values checked; none ends in an exact half cent except values already exact at the cent).

Factor ladders vs rule prose: every tier named in `factors[].ladder` is a rule sentence and a branch of its `decides` binding, and every branch is a stated tier (checked for all 34 factors). No tier lives only in compute.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one extended policy (7 distinct tools, each computes amount_usd once).
- Docstrings: no tool names another tool or policy; the words "then/before" occur only inside a tool's own effect ("the line then appears among the contract's bill lines") or a business description ("terminated before Beacon Ridge supply ever started"), never as cross-tool sequencing. No docstring adds a confirmation, review or wait.
- Function bodies: every tool performs one `ctx.create` with the passed values; none reads a status, a prior line, a prerequisite, or validates an amount (task_tools.py lines 11-284). The tool layer judges no prerequisite.
- uuid8 tails: b7051944, 6fb56a64, 230b7c5e, f4180914, 2ce88247, fffec1b8, 725777e6 — pairwise distinct, no shared prefix, no sequence or adjacency pattern. PASS.
- Observation O-3: `post_termination_security_b7051944` hard-writes `deposit_months=0`; base `cni_security_deposit` says "deposit_months and credit_grade_basis on the deposit record the grade and months used." Termination security is not sized in months, so 0 is a defensible record; no scored consequence.

### prerequisite_graph

- `prerequisite` is filled on all 7 policies ([] on P2, P3, P5, P6, P7).
- Edges: P1→P2, P1→P3, P4→P6, P4→P7, P4→P5. Every `problem` names an extended policy of this file, none a base policy, none itself. Acyclic (two depth-1 stars).
- Every `policy_source` is verbatim in its own policy's rule (P1 rule sentences 3 and 4; P4 rule sentences 3, 4 and 5).
- `form: state` on all five edges; no `fallback_reason` anywhere (consistent).
- `resolved_by` equals the depended-on policy's `target_tool` on all five edges.
- `kind`/`gate`: P1→P2 value_input on `etf_billed` (exists in P1 compute, and the ETF line is exactly what it sums); P4→P6 and P4→P7 value_input on `adj_win` (exists; rebill credits are cni_adjustment rows it sums); P1→P3 and P4→P5 state_gate on `cni_billing.line_type` (a real field). `condition` texts restate the sentences at the same scope, with no authoring-viewpoint phrasing.
- PASS.

### prerequisite_sentences

Four-point test per edge:

| edge | sentence (own rule) | connective | waited-on state (record-visible) | tool/id/snake_case | scope vs condition |
| --- | --- | --- | --- | --- | --- |
| P1→P2 | "The termination security is fixed only after the bill of the terminating contract carries its early termination fee line." | only after | ETF line on the terminating contract's bill | none | equal |
| P1→P3 | "The termination security is not worked out until every contract of the same business that closed before its supply began carries its early termination fee line." | not … until | ETF line on every pre-supply-closed contract of the business | none | equal (open set stated as "every") |
| P4→P6 | "The review amount is fixed only after every block line posted in the review window carries a rebill credit for any part of it billed above the block price in force for its cycle." | only after | rebill credit on each over-billed block line in window | none | equal |
| P4→P7 | "The review amount is not worked out until every index line posted in the review window carries a rebill credit for any part of it billed above the index price the contract allows." | not … until | rebill credit on each over-billed index line in window | none | equal |
| P4→P5 | "Before the review amount is worked out, every contract of the same business that closed during its term by a final bill or by another supplier's enrollment must carry its early termination fee line." | before | ETF line on each closed-in-term final-billed/switched contract | none | equal |

Unique writer per state-form edge (derivation a reader performs from the other rules):
- "ETF line on the terminating contract" (contract in termination_pending from written notice): P2's rule scope is exactly "a contract whose authorized signatory gave written notice to end it during its term and which is in termination_pending status"; P3 requires closed/terminated_before_flow, P5 requires closed/final_billed or switched — neither can act on a termination_pending contract. One writer: P2.
- "ETF line on every contract that closed before its supply began": only P3 ("closed with close_reason terminated_before_flow"). One writer.
- "ETF line on every contract closed during its term by final bill or another supplier's enrollment": only P5. One writer.
- "Rebill credit on an over-billed block line": among extended policies only P6 posts block-line credits. One writer. Observation O-4: the sentence covers every over-billed block line in the twelve-month window, while P6 corrects only the pass-through cycle's block line; an over-billed block line of another cycle could only be resolved under base `cni_billing_correction`, which has no task tool. Neither task world contains such a line (checked in each task file), so no consequence.
- "Rebill credit on an over-billed index line": only P7 among extended policies; same observation O-4 applies.
- No rule carries a second wording, a tool name or another problem's id for any edge; no depended-on rule (P2, P3, P5, P6, P7) restates the sentence. No rule states a cross-problem order outside these five edges (base `cni_enrollment_processing`'s "submitted to the utility only after any required security deposit has been posted" grounds no edge in either tree).
- PASS.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry.

P1 (refs cni_agg_deposit_cap, cni_security_deposit):
- cni_agg_deposit_cap: "Security deposits are combined across all of the customer's C&I contracts." — P1 nets only "the security deposits held on the contract"; the base sentence frames the ceiling measure, not the netting base. Observation O-5 (no consequence in task 0: the customer holds deposits on one contract only). "The deposit required … divided by cents_months_divisor …" — declared (overwrite 2). Ceiling sentence — followed (inherited; not binding in task 0). "A grade with 0 months requires no deposit." — declared (overwrite 3), but the replacement sentence governs a different quantity (damages grade share), so the overwrite pairs a base sentence with an unrelated text. Observation O-6. "The grade used is the one on the customer profile when the contract is executed …" — followed (P1 reads the deposit's recorded grade, which is that execution grade).
- cni_security_deposit: "recorded only on a contract that is pending_enrollment or active" — declared (overwrite 1). Months/grade record sentence — see O-3. Refund sentences — followed. "An unpaid early termination fee is not netted against the deposit by the care desk." — followed (P1 sizes new security; it does not apply the deposit to the fee).

P2 (refs cni_etf, cni_termination): status, single-fee, no-fee-from-holdover, termination-date and no-waiver sentences followed; the remaining-months sentence and the kWh/fee sentence are declared. Observation O-7: the second overwrite's `replaced_by` ("The annual kWh of a noticed termination are the kWh billed …") restates only the baseline kWh sentence, not the rate scaling and month rules the rule then applies; the superseded sentence is named in full, so the override is declared. cni_termination sentences followed.

P3 (refs cni_etf, cni_termination):
- cni_etf: pre-flow full-term clause declared; kWh/fee sentence declared (same O-7 shape: `replaced_by` states min_annual_kwh, which the rule's bizpower ladder then overrides).
- **cni_termination: "An executed contract may be terminated before supply starts; it closes immediately with close_reason terminated_before_flow and the early termination fee is computed on the full term per etf_preflow_basis." — NOT named in P3's `overwrite`.** P3's rule counts "at most unsubmitted_months of its term_months" / "at most submitted_months" for unconfirmed contracts. Undeclared override → finding F-1 (SOURCE-POLICY RED).

P4 (refs cni_agg_deposit_cap, cni_security_deposit): deposit formula declared; "A grade with 0 months requires no deposit." followed (months_grade_a 0); "combined across all contracts" — O-5 shape (task 1: the other contract's deposit is fully refunded, so no consequence); grade-at-execution sentence followed; active-status recording followed; refund sentences followed ("it never refunds security").

P5 (refs cni_etf, cni_termination): termination-date sentence followed (close_date); remaining-months sentence followed verbatim (exit months identical formula); kWh/fee sentence declared; cni_termination switch-away/final-bill sentence followed.

P6 (refs cni_billing_correction, cni_market_notices, cni_energy_billing): rebill amount sentence declared; lookback, once-per-line and agent-limit (500.00 per line) sentences inherited; market-notice timing sentence followed exactly (the 30-day rule); block billing sentence followed by the block tier.

P7 (refs cni_billing_correction, cni_energy_billing): rebill amount sentence declared; lookback/once/limit inherited.
- **cni_energy_billing: "During holdover, all kWh are billed on an index_energy_charge line at the month's index price plus holdover_adder_cents_kwh, except that the adder is not charged when late_expiry_notice_holdover_adder_waived is true and the expiry notice was missing or not compliant." — NOT named in P7's `overwrite`.** P7's rule gives a holdover pass-through cycle "holdover_adder_cents_kwh" unconditionally, and its index-kWh sentence gives a holdover cycle "the metered kWh above block_kwh_per_cycle" (block structure) or "none" (fixed structure) where base bills all kWh. Undeclared override → finding F-2 (SOURCE-POLICY RED, charter-global; no consequence in either task world).

### factor_ladders

Counts per policy (label as declared → after the auditor's tests):

| policy | factors | parameter | method | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| P1 | 6 | 4 | 2 | gas_relationship_relief (agreement status AND bizgas_billing count) | bizgas |
| P2 | 6 | 4 | 2 | none strictly (gas status + drop date sit on one row; load trend reads one ledger) | bizgas |
| P3 | 4 | 2 | 2 → 1 (see F-6) | small_business_usage_basis is single-condition; site_retention_relief reads one row | bizpower |
| P4 | 6 | 5 | 1 | index_price_loading (variant energy_price_basis AND billing kWh share) | bizpower |
| P5 | 6 | 5 | 1 | exit_reason_share (close_reason AND posted final cycle) | none |
| P6 | 4 → 3 or fewer (F-3, F-4) | 2 | 2 | none | none |
| P7 | 4 → 3 (F-5) | 2 | 2 | index_adder_for_cycle (cycle date vs end date AND structure) | none |

Per task: task 0 policies {P1,P2,P3} carry a multi-source factor (P1 gas relief) and cross-difficulty factors (bizgas, bizpower); task 1 policies {P4,P5,P6,P7} carry multi-source (P4 loading, P5 reason) and cross-difficulty (P4 bizpower). The per-task floors hold.

Per-factor structure (bindings disjoint within each policy; every `decides` is an input, never `result`; every ladder has three stated, pairwise-disjoint tiers; every fall-through equals the factor's `baseline`, and the baseline equals what `baseline.rule` states for that input except where noted):

- P1 damages_grade_share (A 0.50 / B 0.75 / else 1): distinct. Observation O-8: base sizing gives grade A 0 deposit months and "A grade with 0 months requires no deposit", so a posted deposit recording grade A cannot arise from base sizing; the A tier is reachable only through a receipt that copies an A grade (both deposit tools allow it). Same shape in P4 review_months_by_grade.
- P1 damages_notice_share, supply_tenure_coverage, gas_relationship_relief: distinct values, conditions a supplier weighs. Pass.
- P1 monthly_supply_rate_measure (method): three different aggregations. Pass. exposure_days_count (method): tier 1 is a date count, tiers 2/3 constants; accepted as method (borderline, O-9).
- P2 remaining_term_rate_share, renewal_history_share, gas_agreement_share, load_factor_share: distinct; plausible. Pass. annual_kwh_load_trend (method): Pass. partial_month_count (method): the fall-through ("the months as counted with a partial final month counted as one") applies only when there is no partial final month, where it coincides numerically with tier 1's whole-month count; the ladder genuinely divides only partial-month customers by notice lead. Observation O-10 (no two tiers share a stated method; not a RED).
- P3 small_business_usage_basis (method), cancellation_lead_share, site_retention_relief: distinct, plausible. enrollment_stage_months: labelled `method`, but its three tiers are `MN(term_months, 12)`, `MN(term_months, 18)` and `term_months` — one formula with a cap constant substituted → finding F-6 (mislabelled effect).
- P4: all six distinct and plausible; Pass (O-8 for the A tier).
- P5: all six distinct and plausible; Pass.
- P6 block_price_in_force (method): tier 1 ("regulatory_passthrough_allowed is false" → "contract_rate_cents_kwh stays in force for every cycle") and tier 2 ("notice_date fewer than regulatory_change_notice_days days before its stated effective date" → "the pass-through cycle keeps contract_rate_cents_kwh") select the same value for the decided quantity `corr_price` (compute: `F('contract_rate_cents_kwh') if not P(...) else (F('contract_rate_cents_kwh') if notice_lead < … else pt_rate)`); and the tiers substitute a price, not an algorithm → finding F-3 (duplicate tier outcome + mislabelled effect). Further, tier 1's condition never holds for a contract that has block_energy_charge lines (the only structure that bills them, Block and Index, has regulatory_passthrough_allowed true).
- P6 block_fixed_price_kwh (parameter): block lines are billed only on a block and index structure (base cni_energy_billing: "the first block_kwh_per_cycle kWh are billed on a block_energy_charge line … when usage is below the block, the whole block is still billed on the block line"), so tier 1 ("energy_price_basis fixed_block_plus_index_balance") holds of every contract that reaches this write in its own term, and tiers 2/3 ("none", "the cycle's metered kWh") are treatments no supplier would apply to a block line it billed on the block size → finding F-4 (unreal ladder; baseline "metered kWh" is a straw man).
- P6/P7 carrying rate: distinct, plausible. Pass.
- P6/P7 carrying period (method): the tier is chosen by whether a monthly_index_price notice is effective on the cycle's billing_period_start (i.e. whether the cycle began on the 1st) and, otherwise, by whether the cycle had 25 or more billing_days (actual/365 vs actual/360). No retail energy supplier selects the interest day-count of a refund by the calendar alignment or length of the billing cycle being corrected → finding F-7 (unreal ladder condition; a domain judgement, not a charter-text contradiction).
- P7 index_kwh_by_structure (method): tier 2 ("energy_price_basis fixed" → "no index kWh"): a fixed-structure contract carries index_energy_charge lines only during holdover, where base bills "all kWh … on an index_energy_charge line"; "none" would treat the entire holdover line as over-billed — a treatment no supplier would publish → finding F-5 (unreal tier; also the F-2 conflict).
- P7 index_adder_for_cycle: distinct values; tier 2 conflicts with the base waiver (F-2). Otherwise Pass.

### findings

- **F-1 SOURCE-POLICY RED — undeclared override in P3 (cni_ext_preflow_termination_damages).** Symptom: P3 counts at most 12 (or 18) months for a pre-flow termination never confirmed by the utility. Root cause: base `cni_termination` (in P3's `base_policy_refs`) says "…it closes immediately with close_reason terminated_before_flow and the early termination fee is computed on the full term per etf_preflow_basis."; P3's `overwrite` names only the `cni_etf` clause "for a pre-flow termination all term_months count as remaining, per etf_preflow_basis." Evidence: cni.extended.yaml lines 908-913 (base) vs 1495-1505 (overwrite) and 1529 (rule). Consequence: on any unconfirmed pre-flow contract with term_months > 12 the base sentence yields months = term_months and P3 yields 12 — two defensible ETF amounts. Bears on task 0 (demonstrated there).
- **F-2 SOURCE-POLICY RED — undeclared override in P7 (cni_ext_passthrough_index_rebill) of base cni_energy_billing's holdover sentence.** Evidence: base "During holdover, all kWh are billed on an index_energy_charge line at the month's index price plus holdover_adder_cents_kwh, except that the adder is not charged when late_expiry_notice_holdover_adder_waived is true and the expiry notice was missing or not compliant." vs P7 "a pass-through cycle that began after contract_end_date, a holdover cycle, carries holdover_adder_cents_kwh" and "on a structure whose energy_price_basis is fixed_block_plus_index_balance they are the metered kWh above block_kwh_per_cycle … on a structure whose energy_price_basis is fixed there are none". Consequence (demonstrated on a constructed situation): a holdover pass-through cycle on a fixed contract with no expiry notice — base: all kWh at index, no adder; P7: zero index kWh and the full holdover adder — different correct amounts, hence different credits. Not reached by task 1's world (its pass-through cycle is in term); recorded charter-wide.
- **F-3 SOURCE-FACTOR RED — P6 block_price_in_force: two tiers select the same value, and the `method` label is dishonest.** See factor_ladders. Bears on task 1 (factor count).
- **F-4 SOURCE-FACTOR RED — P6 block_fixed_price_kwh: unreal ladder (tier 1 restates the write's scope; tiers 2/3 and the baseline are not treatments a supplier applies to a block line).** Bears on task 1.
- **F-5 SOURCE-FACTOR RED — P7 index_kwh_by_structure tier 2 is not a published treatment (contradicts base holdover billing).** Bears on task 1 (factor count).
- **F-6 SOURCE-FACTOR RED — P3 enrollment_stage_months labelled `method` while its tiers substitute a cap constant into one formula.** After relabelling P3 still has one method (small_business_usage_basis), so the count floors hold; the defect is the dishonest label. Bears on task 0.
- **F-7 SOURCE-FACTOR RED (domain judgement) — P6 block_carrying_period and P7 index_carrying_period select the interest day-count by the corrected cycle's calendar alignment / length, a condition no supplier weighs for that quantity.** Bears on task 1.
- Observations (no rework grounds): O-1 compute decides an undefined 3-month case (P1/P4); O-2 evaluator rounding is Python `round`, the rule says half up; O-3 deposit_months=0 on termination security; O-4 rebill prerequisite sentences are broader than P6/P7's scope; O-5 per-contract netting vs base "combined across all … contracts"; O-6 P1 overwrite 3 pairs a base sentence with an unrelated replacement; O-7 `replaced_by` texts restate only baseline sentences (P2, P3); O-8 grade-A tiers not reachable from base sizing; O-9 exposure_days_count label borderline; O-10 partial_month_count fall-through coincides with tier 1 on its own domain; O-11 every rule carries both baseline sentences ("No gas relationship relief applies to the termination security.") and factor sentences that contradict them literally ("…gives a relief of gas_relief_full"), with the precedence never stated in the rule — the framework's mandated shape, recorded so the KB render keeps the precedence explicit.

## closing_checklist

Written after both reveals (2026-10-04T16:24:19Z). The charter-global section above was frozen at 16:22:20Z (file mtime; the 16:25Z in its header is an estimate written at the time) and was not changed after the reveal. **The difficulty is not closed: not every relationship passes.**

- Audit files: `0.md` and `1.md` correspond one-to-one with tasks/0.json and tasks/1.json; both have a frozen derivation followed by a comparison. Comparison verdicts: task 0 — SOURCE-POLICY RED, SOURCE-FACTOR RED, SOURCE-TASK RED (problem tree PASS); task 1 — SOURCE-FACTOR RED (policy on its own world, problem tree and unique solution PASS). Not all PASS.
- Coverage and scope: charter_scope task 0 = {termination_security, noticed_termination_damages, preflow_termination_damages}, task 1 = {anniversary_security_review, contract_exit_damages, passthrough_block_rebill, passthrough_index_rebill} — pairwise disjoint, each a whole tree, union = all 7 extended policies and all 7 task tools. PASS. uuid8s independent and frozen: PASS.
- Problem trees: task 0 n=2 with 1 value_input; task 1 n=3 with 2 value_input; each root resolved by an owner=user tool; the difficulty's graph is acyclic with no cross-task edge. PASS.
- Factors: every factor bears weight on its task's world against an honest baseline, and every whole baseline gives a definite number different from gold (task 0: 4800.02 / 10377.50 / 6739.03; task 1: no credit / no credit / 10650.27 / 21248.50). FAIL on ladder structure: F-3, F-4, F-5, F-7 (P6 and P7 below four surviving factors), F-6 (dishonest label in P3), and the false tier assertion in tasks/1.json for P4 index_price_loading.
- Policy self-consistency: FAIL — F-1 (undeclared override in P3, demonstrated in task 0) and F-2 (undeclared override in P7, demonstrated on a constructed holdover situation, not reached by task 1).
- Gates re-run on the final form: not applicable this round — the artifacts were not changed by this audit and the difficulty does not close; the orchestrator's gate snapshot remains the latest.
- Blind-derivation result (round 1 focus): both tasks' independent derivations land exactly on GT for every scored argument, owner and order (task 0: three writes; task 1: four writes); the prerequisite trees, edge-skip figures and every per-factor baseline figure also match GT figure for figure.

## revision_2

### charter_global_frozen (revision_2)

- Auditor: same independent auditor, round 2 (re-audit after rework). Written before either task's round-2 GT was opened; nothing in this section derives from a revealed GT.
- Hash comparison against round 1: `cni.extended.yaml` 9887dd90…dd9c9 → **64663a3b70f98a85614968bc0a1df98c52876d8bce68c75f8a4b6aa9c0ea47db**; `task_tools.py` 661a0e12…7e2b43 → **d2914696e57b4006cf41ee8d7ba91b08ce56b3c489e821f3dd1423260392818c**; masked views task_0 96c7f7d0…3298, task_1 07a735d3…0b (both changed). Both shared inputs moved, so every charter-global section is re-derived in full below; nothing is carried forward by reference. `blueprint/products/cni.yaml` unchanged (mtime before round 1), and the extended file's base section is still structurally identical to it (all ten keys equal).
- Gate snapshot supplied (orchestrator re-run): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK, traceability deferred. Entry conditions met.
- Permitted / masked: as round 1.

### policy_conflict_scan (revision_2)

Extended policies: P1 termination_security, P2 noticed_termination_damages, P3 preflow_termination_damages, P4 anniversary_security_review, P5 contract_exit_damages — unchanged ids/tools; **P6 is now `cni_ext_passthrough_fixed_price_rebill` → `credit_fixed_price_line_5b24cf0d`** (replaces the round-1 block-rebill policy and `credit_block_line_fffec1b8`, which no longer exist); P7 `cni_ext_passthrough_index_rebill` → `credit_index_line_725777e6`.
- Subjects still overlap three ways (deposit_post P1/P4; etf_charge P2/P3/P5; adjustment P6/P7) with disjoint objects: P6 now corrects the pass-through cycle's fixed-price energy line (block_energy_charge on block and index, energy_charge on a fixed structure); P7 the same cycle's index_energy_charge line. No line type is claimed by both. Other anchors, cross-category reads and terminal states as round 1.
- Graph components: {P1,P2,P3} and {P4,P5,P6,P7}; with M=2 the only whole-tree partition still covers all 7 policies once.

### rule_compute_equivalence (revision_2)

- P1, P4: the 3-to-11-cycle tier now reads "three to eleven cycles, at least one of them posted in the latest three months … any other count gives …", matching compute `cyc12 >= 3 and cyc3 > 0` (round-1 O-1 closed); ladder text updated to match.
- P2, P5: unchanged; equivalence holds.
- P3: unchanged compute; `enrollment_stage_months` relabelled (see factor_ladders).
- P6: every binding quoted. `price_in_force` = contract rate when pass-throughs are not allowed or the late notice's 30-day day falls after the whole cycle (`days_before >= fx_days`); day-weighted `(contract × days_before + new × (fx_days − days_before)) / fx_days`, unrounded, when the cycle runs past that day; else new rate — equals the rule. `fixed_kwh` (block, cycle < 28 days → block × days / 30; block → block; else metered) equals the rule. `other_credits` = window rebill-credit count minus pass-through-cycle credits = "rebill credits for cycles other than the pass-through cycle posted … in the twelve months". Carrying period fixed at months × 30 / 360 and stated in the rule. Sweep back: no rule sentence without compute.
- P7: `idx_kwh` = MX(0, metered − block × days / 30) on a short in-term block cycle; MX(0, metered − block) on other in-term block cycles; metered otherwise (RTI or any holdover). `adder` = 0 for in-term block **or** holdover with waiver true and expiry notice missing/non-compliant (`exp_ok` = lead between expiry_notice_latest_days and expiry_notice_earliest_days); holdover adder for other holdover; contract rate otherwise. Equals the rule. Observation R2-O-a: the rule phrase "the metered kWh above block_kwh_per_cycle prorated by its billing_days over days_per_month_basis" also parses as "(metered − block) prorated"; on a constructed 25-day in-term cycle with metered 160,000 and block 150,000 the compute reading gives 35,000 kWh and the other gives 8,333. The postmodifier most naturally attaches to block_kwh_per_cycle, and P6's rule states the prorated block explicitly, so the compute reading is the better-supported one. Not reached by task 1 (31-day cycle). Recorded as an observation.

### action_binding_and_uuids (revision_2)

- Seven `(target_tool, computes)` pairs, one per policy. New tail `5b24cf0d` is distinct from b7051944, 6fb56a64, 230b7c5e, f4180914, 2ce88247, 725777e6 and from the retired fffec1b8; no shared prefix or sequence. PASS.
- `credit_fixed_price_line_5b24cf0d` body: one `ctx.create` of a rebill_credit dated today, carrying the source line's billing_period_start; no validation. Module-wide grep finds no status check, error return or cross-tool ordering word (only "terminated before … supply" business wording). PASS.

### prerequisite_graph (revision_2)

Edges P1→P2 (value_input, etf_billed), P1→P3 (state_gate), P4→P6 (value_input, adj_win, resolved_by credit_fixed_price_line_5b24cf0d), P4→P7 (value_input, adj_win), P4→P5 (state_gate). All sentences verbatim in their own rules; form state, no fallback_reason; acyclic; resolved_by = target_tool everywhere; gates exist. PASS.

### prerequisite_sentences (revision_2)

The five sentences are unchanged and pass the four-point test as in round 1. Unique writer check re-done: "rebill credit on an over-billed block line" — among extended policies only P6 writes credits on block lines (P7 writes on index lines only). PASS. O-4 persists in a slightly wider form: P6 also corrects fixed-structure energy_charge lines, which the P4 block-line sentence does not gate. No consequence in task 1 (Aurora is block and index).

### override_declarations (revision_2)

- P3: the cni_termination clause "the early termination fee is computed on the full term per etf_preflow_basis." is now named (overwrite 2). **F-1 closed.**
- P6 (refs cni_billing_correction, cni_market_notices, cni_energy_billing): rebill-amount sentence declared; cni_market_notices clause "the new price applies to cycles beginning on or after the later of the stated effective date and notice_date plus regulatory_change_notice_days." declared, replaced by the day-weighted proration; cni_energy_billing clause "the first block_kwh_per_cycle kWh are billed on a block_energy_charge line at contract_rate_cents_kwh" declared, replaced by the short-cycle proration. Lookback, once-per-line, 500.00 agent limit inherited. Observation R2-O-b: the same base sentence's trailing clause "when usage is below the block, the whole block is still billed on the block line" is not named; for a short cycle with usage below the prorated block it reads as "the whole (prorated) block" in harmony with P6. A reader who takes "the whole block" as the full block_kwh_per_cycle would find a short-cycle block line billed at the full block correct. Not reached (31-day cycle).
- P7 (refs cni_billing_correction, cni_energy_billing): rebill sentence declared; the same cni_energy_billing first clause declared (replaced by the prorated-index text). The base holdover sentence is now **followed**: holdover cycles carry all metered kWh and the holdover adder is waived when late_expiry_notice_holdover_adder_waived is true and the expiry notice was missing or non-compliant. **F-2 closed.**
- P1, P2, P4, P5: unchanged sweep; findings as round 1 (no undeclared override).

### factor_ladders (revision_2)

| policy | factors | parameter | method | notes |
| --- | --- | --- | --- | --- |
| P1 | 6 | 4 | 2 | unchanged; monthly rate ladder now fully defined |
| P2 | 6 | 4 | 2 | unchanged |
| P3 | 4 | 3 | 1 | `enrollment_stage_months` now `parameter` (cap values). **F-6 closed.** |
| P4 | 6 | 5 | 1 | unchanged; exposure ladder now fully defined |
| P5 | 6 | 5 | 1 | unchanged |
| P6 | 4 | 2 | 2 | new: price_in_force_for_cycle (method), fixed_price_kwh_basis (method), fixed_price_carrying_rate, fixed_price_repeat_uplift |
| P7 | 4 | 3 | 1 | index_kwh_for_cycle (method), index_adder_for_cycle, index_carrying_rate, index_repeat_uplift |

- P6 price_in_force_for_cycle: tiers give contract rate / a day-weighted average / the new rate — three distinct outcomes; tier 2 is a different computation, so `method` is honest; pro-rating a mid-cycle price change by days is ordinary utility practice. Tier 2 is multi-source (notice dates and the cycle's billing_days). **F-3 closed.**
- P6 fixed_price_kwh_basis: the policy now covers fixed structures as well, so the ladder separates block-and-index short cycles (prorated block), other block-and-index cycles (block) and fixed structures (metered — the base fixed-price billing basis). Each tier is the real billing basis for its case; the baseline (metered) is the standard method and the fall-through. **F-4 closed.**
- P6/P7 carrying rate: unchanged, plausible. Repeat uplift (≥2 other-cycle credits ×1.50, one ×1.25, none ×1): distinct, a plausible penalty for repeated billing errors, rests on rebill_credit rows. Carrying period is no longer a factor; it is a fixed sentence (months × 30 / 360) of the rule and baseline. **F-7 closed.**
- P7 index_kwh_for_cycle: tier "fixed → none" removed; holdover cycles take all metered kWh as base bills them. Tiers distinct and real. **F-5 closed.** index_adder_for_cycle: tier 1 is a disjunction (in-term block, or a waived holdover) with one value; tiers distinct.
- Baselines: P6 baseline.rule (new rate, metered kWh, zero carrying rate, fixed period) and P7 baseline.rule (metered kWh, contract-rate adder, zero carrying rate) are self-sufficient and equal every factor's fall-through. The uplift's baseline (1) is not stated in baseline.rule, which zeroes the rate it multiplies — the same shape round 1 noted for the carrying period; observation.
- Per-task floors: task 0 multi-source (P1 gas relief), cross-difficulty bizgas/bizpower; task 1 multi-source (P4 loading, P5 reason, P6 price tier 2), cross-difficulty bizpower. PASS.

### findings (revision_2)

| round-1 item | status in revision_2 |
| --- | --- |
| F-1 P3 undeclared override of cni_termination | closed (overwrite 2 names the clause) |
| F-2 P7 vs base holdover billing | closed (holdover sentence now followed) |
| F-3 P6 duplicate tier / mislabel | closed (policy replaced; three distinct outcomes, real method tier) |
| F-4 P6 unreal block-kWh ladder | closed (ladder now divides block / short block / fixed) |
| F-5 P7 "fixed → none" tier | closed (removed) |
| F-6 P3 mislabel | closed (relabelled parameter) |
| F-7 carrying-period ladders | closed (no longer a factor) |
| O-1 undefined 3-month case | closed (rule text defines it) |
| O-2 … O-11 | unchanged observations (O-4 slightly wider, see above) |

New in revision_2: observations R2-O-a (P7 prorated-index phrase admits a second parse, not reached) and R2-O-b (P6 leaves the "whole block" trailing clause unnamed, not reached). No new charter-global RED.

### closing_checklist (revision_2)

Written after both round-2 reveals (18:02:04Z). The revision_2 charter-global section above was frozen at 18:01:16Z (sha256 7b8bc0b8…ca9b at reveal) and not changed after the reveal.

- Audit files: `0.md` and `1.md` each have round-1 and revision_2 sections, with the older text preserved. Both revision_2 comparisons carry PASS on all four relationships.
- Coverage and scope: task 0 {P1,P2,P3}, task 1 {P4,P5,P6,P7}, pairwise disjoint, whole trees, union = all 7 extended policies and all 7 task tools (credit_block_line_fffec1b8 retired; no task references it). uuid8s independent and frozen. PASS.
- Problem trees: task 0 n=2 / 1 value_input; task 1 n=3 / 2 value_input; owner=user root in each; difficulty graph acyclic with no cross-task edge. PASS.
- Factors: P1 6, P2 6, P3 4, P4 6, P5 6, P6 4, P7 4; each has ≥2 parameter and ≥1 method with honest labels and three distinct, real tiers stated in the rule. Per task ≥1 multi-source and ≥1 cross-difficulty. Every factor bears weight against an honest baseline; every whole baseline differs from gold. PASS.
- Policy self-consistency: F-1 and F-2 closed; no undeclared override remains. PASS, with observations R2-O-a and R2-O-b (constructed short-cycle readings, not reached by either task) and O-2 … O-11 carried.
- Gates on the final form: the orchestrator's round-2 snapshot (all green, traceability deferred) is the run on this exact form (hashes 64663a3b… / d2914696…). check_traceability remains outstanding until the KB is published.
- **Difficulty verdict (revision_2): source-layer audit PASS.** Every round-1 RED is closed, no new RED was found, and nothing regressed.

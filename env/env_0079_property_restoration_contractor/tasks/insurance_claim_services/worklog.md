# insurance_claim_services — worklog

## Step 0 draw (draw_counts.py --tasks 2)
{"task": 0, "prerequisite_problems": 3, "problems": 4, "factor_counts": [6, 6, 6, 6]}
{"task": 1, "prerequisite_problems": 1, "problems": 2, "factor_counts": [5, 4]}

## Design (see plan.md for the structural finding and the trees)
Tool names (uuid8 generated once each, frozen):
- submit_code_reconciliation_supplement_37cdbc2e (owner=user)  -> claims_ext_code_reconciliation_supplement (task 0 root)
- post_code_waiver_writeoff_45243a0f (agent)                   -> claims_ext_code_waiver_writeoff (task 0)
- submit_regulated_material_supplement_a5be6b72 (agent)        -> claims_ext_regulated_material_supplement (task 0)
- submit_building_department_fee_supplement_9f81d61c (agent)   -> claims_ext_building_department_fee_supplement (task 0)
- submit_depreciation_release_d117c1f9 (owner=user)            -> claims_ext_insured_depreciation_release (task 1 root)
- post_removed_scope_writeoff_098877f3 (agent)                 -> claims_ext_removed_scope_writeoff (task 1)

## Progress log
- 2026-10-23 round 1 (resumed): claims.extended.yaml carries all 6 extended policies (written piece by piece);
  task_tools.py written (6 tools, Decimal half-up helper as class static method, no forbidden tokens).
  Tool rename: the mold tree uses submit_mold_reconciliation_supplement_c8ac8fa6 and post_mold_overapproval_writeoff_0ae79d4b
  (fresh uuid8 each); post_removed_scope_writeoff_098877f3 was never used (design changed: task 1 is the mold tree).
- Final tree design (supersedes plan.md task-1 section):
  task 0 (HDP, TX): root claims_ext_code_reconciliation_supplement (user) <- regulated_material_supplement (user, value),
  <- code_waiver_writeoff (agent, value), <- insured_depreciation_release (user, state); release <- code_waiver_writeoff (value).
  Supplements in call: 2 (= HDP max pending 2, none pending at opening).
  task 1 (HDP): root claims_ext_mold_reconciliation_supplement (user) <- mold_overapproval_writeoff (agent, value).
- Task 0 assembled (tasks/0.json via scratch authoring scripts in /tmp/insurance_claim_services_0079): per-task gates
  check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all OK
  for --task 0 (first replay red: empty FK strings and two unread rebuild tables -> FK fields dropped when empty, reads of
  change orders and draws added; solvability red: field-level evidence and intent kind -> fixed).
  Values: write-off 446.20, regulated-material supplement 1390.98, release 3527.39, reconciliation 725.62.

## XF tables (round 1)
### A1 factor-reads (factor -> bindings it reads -> owner)
- regulated_material: lead_setup_counting -> wj_lead, wj_built, wj_rrp_cutoff (plain), rb_lead (own); rrp_cleanup_lines -> wj_cont, wj_hepa (own), wj_built, wj_rrp_cutoff (plain); abatement_disposal_line -> wj_haul, wj_dump (own), wj_built, wj_asb_cutoff, wj_asb (plain); regulated_ppe_line -> wj_ppe_billable, wj_ppe_rate, wj_ppe (own), wj_asb, wj_lead (plain); setup_day_labor -> wj_setup_date, wj_tech_setup, wj_sup_setup (own); regulated_op_rate -> rm_codes (own, raw XCOUNTs), F/P (plain). No factor reads another factor's binding.
- code_reconciliation: expediting_counting -> rb_expedite_all, rb_expedite_bldg (own), rb_types, rb_drawings (plain); drawing_line_counting -> rb_bldg_permit, rb_drawing_fee (own), rb_drawings (plain); letter_line_counting -> rb_letters, rb_letter_fee (own), rb_drawings (plain); property_setup_counting -> rb_built, rb_rrp_cutoff, rb_setup, wj_setup_line (own); mitigation_sampling_lines -> wj_year, wj_sampling_cutoff, wj_floodcut, wj_sampling, wj_haul_line (own); reconciliation_op_rate -> rc_op_types (own).
- code_waiver_writeoff: duplicate_credit_counting -> wj_credit_dup (own), wj_status, wj_balance (plain); goodwill_credit_counting -> wj_gw_cap (own), wj_goodwill, wj_status (plain); credited_op_rate -> wj_credit_n (own); refund_offset_rule -> wj_refunds (own), wj_balance (plain); late_fee_relief_rule -> wj_late_fees, wj_late_min (own), wj_goodwill (plain); carrier_cut_rule -> ap_request_id, ap_requested, ap_reinspect (own), ap_amount, cw_lines (plain assembly).
- insured_depreciation_release: incurred_cost_shortfall -> rb_final, rb_amount, rb_co_charges, rb_co_credits, wj_final (own), rb_status, rl_initial (plain); deductible_carry_rule -> rl_initial_withheld, rl_acv_paid, rl_acv_gap, rl_deductible_full (own), rl_initial (plain); code_holdback_cut_rule -> rl_code_lines (own), rl_sup_withheld, rb_status (plain); pending_release_rule -> rl_prior_requested (own), rl_n_release_pay, rl_released (plain); goodwill_release_offset -> own water reads; supplement_overpayment_rule -> rl_sup_paid, rl_sup_approved, rl_sup_excess (own), rl_sup_withheld, rl_n_release_pay, rl_released (plain).
- mold_reconciliation: containment_equipment_days, clearance_fee_counting, minimum_charge_counting (reads ml_min_lines plain), mold_regulated_lines (reads ml_lead, ml_asb plain), mold_op_rate — each owns its raw reads.
- mold_overapproval_writeoff: closed_job_credit_counting (mo_dup own, mo_err plain), closed_job_goodwill_counting (reads mo_err plain), after_hours_premium_rule (own), mold_cut_rule (own; mo_unbilled plain assembly).
### A3 defining sentences: each policy's rule = scope/eligibility sentences (base, inherited verbatim), overwrite restatement, prerequisite sentence(s), one generic assembly sentence (plain), the baseline sentence(s), then one paragraph per factor ladder; caps/room sentence plain.
### A7 all-pairs method tiers (distinguishing input)
- lead_setup_counting: excess-over-contract (adds rebuild line + MX) | zero | as billed.
- rrp_cleanup_lines: containment+HEPA (two inputs) | HEPA only | none.
- property_setup_counting: larger of two setups (max) | contract setup | none.
- mitigation_sampling_lines: sampling+haul | sampling | none.
- incurred_cost_shortfall: final-invoice measure | contract-sum measure (adds change order inputs) | zero.
- code_holdback_cut_rule: excess above lines (difference) | whole withheld | zero.
- pending_release_rule: all prior requested | prior requested above payments (difference) | zero.
- carrier_cut_rule / mold_cut_rule: ratio scaling | difference reduction | as is.
- after_hours_premium_rule: premium on two inputs | one input | none.
- minimum_charge_counting: billed minimum lines | lines + shortfall to tier minimum | none.
### B2 decoy/absent probes (scratch run, /tmp/insurance_claim_services_0079/probes.py)
- task0 world without water job: regulated 0, write-off 0.00, release 0.00, reconciliation 903.60 (out of scope: the scope sentence requires one water job).
- task0 world without contract: release 4760.00, reconciliation 0.00 (out of scope: one contract required).
- task0 approvals removed: write-off 0.00, release 0.00. Decoy cancelled contract listed first: release 4760.00 (CFIELD first match) — scope sentence excludes it (exactly one contract).
- task1 without mold jobs: write-off 4260.00 (out of scope: exactly two mold jobs); approvals removed: 0.00.
### A6 T1/T2
- T1 (world): every factor's baseline substitution moves result (check_compute OK; figures in computations[].factor_sensitivity).
- T2: each ladder has a producible world where it alone moves result (each factor's evidence is independent of the others' records; e.g. a pre-1978 house with a contract lead-safe line and no other regulated line moves only property_setup_counting).
### Known risks / BLUEPRINT-KNOWN candidates
- Claims charter gives the insured no numeric own write except release on direct-pay tiers; scoped overwrite of the Homeowner Direct Pay supplement sentence (insured submits from the portal) declared in the three supplement policies.
- Write-off reason enum has no "not incurred" value; carrier_denied_line is used for credited / unbilled approved amounts.
- DSL: XSUM is customer-wide and CFIELD first-match; policies are scoped to one water job / one contract / two mold jobs by stated record tests.
- Realism flags for the audit: overhead-only middle tiers, setup-day labor, late-fee relief, dehumidifier exclusion; regulated supplement counts billed containment including a credited duplicate.

## Final gate block (no --task), round 1
check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks REPLAY OK; check_solvability SOLVABILITY OK;
check_compute COMPUTE OK (suite means branches 106.00, steps 18.00; history_rows_max 14; branches_max 159); check_grounding GROUNDING OK;
check_cross_fire SCOPE OK. check_traceability deferred until docs are published.
ROUND 1: gates 7/7 green

## REWORK round 2 — plan (written before changes)
Audit: audits/policy_task/insurance_claim_services/{_difficulty,0,1}.md read in full. Verified each finding against the
charter and worlds; all CG-1..CG-17, T0-1..T0-3 reproduce (no dispute on facts).
Approach (coordinator ruling: re-tree allowed, draws fixed, F1 customer write):
- Trees kept (SOURCE-CHAIN PASS in both tasks); every policy rewritten from a structured generator so that every
  compute_basis quote is a sentence of its own rule (B6) and the assembly sentence is generic (A2/A5).
- Every factor rebuilt so that tier conditions read attributes independent of the inputs the tier formulas use
  (property type, tier, dispatch window, growth location, era, contract status, approval-vs-request), and no tier
  restates another tier's formula with an input at zero (A7/CG-2); flagged unreal families dropped (overhead-only tiers,
  refunds / late fees / goodwill on carrier write-offs, drawings-keyed expediting, schedule-fee substitution, threshold-keyed
  cut, presence-keyed credit/goodwill tiers) (CG-4); cut/assembly factors read only plain bindings (CG-5).
- Baselines rewritten as defaults silent about variation (CG-1).
- carrier_denied_line uses get a scoped overwrite that names the base defining sentence and the carrier act (CG-7).
- Supplement overwrites restate the retired clause for every other supplement and name their siblings (CG-8).
- Rule/compute aligned (write-offs "of it" via source_approval_id, coverage filters stated) (CG-9), mo_err quote (CG-10).
- Waits carry de minimis / over-cap carve-outs (CG-14); tool bodies enforce positivity / integers (CG-15);
  sibling treatments aligned (credited lines netted in the supplements) (CG-16); subjects restated to match formulas (CG-17).
- Task 0 seed: unproducible earlier release request removed (T0-1); proofs regenerated from recomputation (T0-2, T0-3).

### REWORK round 2 — progress (resumed after account cut)
- claims.extended.yaml regenerated from /tmp/insurance_claim_services_0079/r2 specs: RMS 5 factors, S_cat 6, CWW 4, IDR 5, MJS 4, MRS 4; policy-structure checks pass.
- task_tools.py rewritten: 6 tools (RMS/S_cat/MJS/CWW agent-owned; MRS/IDR user-owned), bodies reject non-positive amounts and non-integer or <1 sequence numbers (CG-15).
- T1 world rebuilt (r2/t1.py): MJS 2569.44 then MRS 698.40; opening MRS 3267.84.
- Next: T0 world (PA tier), tasks/0.json + 1.json, full gate block, per-item list.
- Draw is gate-enforced (check_compute): T0 [6,6,6,6], T1 [5,4]. Policies brought to the draw: CWW 6 (billing / duplicate / goodwill inclusion by estimate source, removed scope, water-line and contract-scope pricing), RMS 6 (+ cleaning-verification labor), IDR 6 (+ supplement depreciation already paid), MRS 5 (+ regulated lines by growth location), MJS 4.
- T1 regenerated (tasks/1.json): MJS 2457.15 (held to mold room 7000.00 - 4542.85), MRS 810.69; per-task gates extended/replay/solvability/compute/grounding green.
- T0 world rebuilt (r2/t0.py, PA tier): CWW 498.62, RMS 2326.95, S_cat 1172.85, IDR 2273.53.

## XF tables (round 2; supersede the round-1 tables above)
### A1 factor-reads (each factor reads only its own bindings and plain baseline bindings; no factor reads another factor's binding)
- regulated_scope (RMS): rrp_cleanup_scope -> rs_tier, rs_cont, rs_hepa (own), rs_built, rs_rrp (plain); abatement_disposal_line -> rs_haul, rs_dump (own), rs_built, rs_asbcut, rs_asb (plain); regulated_ppe_line -> rs_ppe_ok, rs_ppe_rate, rs_ppe_lines (own), rs_asb, rs_lead (plain); certified_renovator_labor -> rs_ptype, rs_setup_date, rs_sup, rs_tech (own), rs_built, rs_rrp, rs_asbcut (plain); regulated_tearout_lines -> rs_ptype_t, rs_flood, rs_base (own), rs_built, rs_rrp, rs_asbcut (plain); cleaning_verification_labor -> rs_ptype_v, rs_hepa_date, rs_v_tech, rs_v_sup (own), rs_built, rs_rrp, rs_asbcut (plain).
- category_reassessment (S_cat): every factor -> its own quantity/rate reads; sc_tier, sc_cat, sc_area, sc_large, sc_clean, sc_gray (plain); reassessed_regulated_lines also sc_reg_pending (own; the prerequisite gate).
- credited_line_writeoff (CWW): billing_error_inclusion -> cw_err, e_est, e_dry, e_inv, e_equip (own); duplicate_line_inclusion -> d_* (own); goodwill_inclusion -> g_* (own); removed_scope_inclusion -> r_est, r_co_last, r_co, r_add_last, r_add, r_markup (own); water_line_pricing_basis -> wp_tier, wp_trades, wp_opened (own; decides a multiplier); contract_scope_pricing_basis -> cp_tier, cp_trades, cp_signed (own; decides a multiplier). The assembly (plain) multiplies family sums by the multipliers, so no factor reads another factor's output (CG-5).
- insured_depreciation_release (IDR): contract_cost_measure -> rb_status, rb_paid, rb_final (own), rb_amount, rb_co, rb_cr (plain); water_cost_measure -> wj_status, wj_final, wj_credits (own), wj_posted (plain); deductible_carry_rule -> rl_init_wh, rl_acv, rl_gap, rl_ded_amt (own), rl_init_amt (plain); advance_recoupment_rule -> rl_adv, rl_adv_gap (own), rl_init_amt, rl_init_wh, rl_acv (plain); code_holdback_cut_rule -> rl_sup_wh, rb_status_c, rb_co_c (own); supplement_depreciation_paid -> rl_sup_amt, rl_sup_wh2, rl_sup_paid (own).
- mold_protocol (MJS): surface -> mp_loc, mp_soda, mp_handler, mp_coil (own), mp_area, mp_brush, mp_encap (plain); removal -> mp_loc_rm, mp_debris_fee (own), mp_area, mp_drywall, mp_insul (plain); air -> mp_cont_req, mp_negair_req, mp_cont_fee, mp_scrub_rate (own), mp_dehu_rate, mp_cap (plain); regulated fee -> mp_ptype, mp_built, mp_rrp, mp_asbcut, mp_leadfee, mp_asbfee, mp_loc_rg (own).
- mold_reconciliation (MRS): surface -> mr_loc, mr_blast, mr_hvaclines (own), mr_brush (plain); removal -> mr_loc_rm, mr_debris (own), mr_insul, mr_drywall (plain); air -> mr_cont_req, mr_negair_req, mr_cont, mr_scrub (own), mr_dehu (plain); regulated lines -> mr_loc_rg (own), mr_lead, mr_asb (plain); after-hours labor -> mr_loc_lb, mr_mult (own), mr_ah (plain).
### A2/A3 defining sentences
Every rule = scope and base eligibility sentences, the overwrite restatement where declared (CWW meaning; MRS recording; IDR amount), the prerequisite sentence(s), one generic assembly sentence ("each family/deduction settled below"), the baseline sentence(s) (standard method, silent about variation), then one sentence per factor ladder. Every compute_basis value is a whole sentence of its own rule (sweep: no miss).
### A7 all-pairs tiers (the input or shape that keeps each pair apart on the other tier's domain)
- RMS: cleanup HEPA | containment+HEPA | 0 (conditions: tier, build year; containment/HEPA billable on any tier). disposal haul | dumpster | 0 (data-selected line). PPE billed PPE | one tech-day at the tier rate | 0. renovator labor supervisor on containment date | technician+supervisor on that date | 0 (property type, build year). tear-out flood cut+baseboard | baseboard | 0. verification technician on HEPA date | technician+supervisor | 0.
- S_cat: every family T1 (Gray/Clean -> category_3 rates) | T2 (Clean -> category_2 rates or an added line) | 0; T1 and T2 use different rate tables or line classes; the fall-through domain includes downward reassessments, where T1/T2 formulas are non-zero (negative), so no tier restates another.
- CWW: inclusion families all credits | latest equipment-day line credit | 0 (estimate date against invoice/drying dates, independent of the credit amounts); removed scope all CO credits | credits less additive charges net of markup | 0; pricing multipliers (1 - program discount) | (1 + overhead + profit) | 1.
- IDR: contract cost paid | final invoice | amount + CO - credits; water cost final - credits | final | posted charges; deductible whole | deductible - gap | 0; advance whole | advance - gap | 0; code cut withheld - CO charges | whole withheld | 0; supplement depreciation paid whole withheld | payments - (approvals - withheld) | 0.
- MJS: surface soda x area | handler+coil fees | brush+encap x area; removal insulation x area + one debris load | drywall x area | both; air containment + (scrubber+dehumidifier) x cap | scrubber x cap | dehumidifier x cap; regulated fee lead+asbestos fee | asbestos fee | 0 (location, property type, build year; fees are tier parameters, non-zero on every domain).
- MRS: surface blasting lines | HVAC lines | brush+encap lines; removal insulation+debris | drywall | both; air containment+scrubber+dehumidifier | scrubber | dehumidifier; regulated asbestos only | 0 | lead+asbestos; labor after-hours / multiplier | 0 | after-hours as billed (growth location is independent of what was billed).
### B2 decoy / absent / edge probes (r2/probes.py, scratch)
- T0 absent water job: CWW 251.47 (removed scope only), RMS 0.00, S_cat 0.00, IDR 0.00; absent contract: CWW 247.15, IDR 0.00; absent approvals: CWW 0.00, IDR 0.00; absent payments: IDR 6786.25 (no exception).
- T0 None estimate / deductible: CWW 255.60, IDR 6426.25; zero estimate: CWW 608.16 (division guard holds); None year_built: RMS 913.75.
- T0 date edges: estimate on the invoice date -> invoice-source tier (498.62, inclusive); on the drying complete date -> fall-through (251.47); CO credit on the estimate date -> no removed scope (247.15); additive charge on the credit date -> swap tier (247.15).
- T0 decoy water job of another file listed first: every figure unchanged (CFIELD filters claim_file_id). Category not reassessed: S_cat 0.00. Supplement paid in full: IDR 3226.25; ACV net of deductible and advance: IDR 4526.25.
- T1 absent mold jobs: 0.00 / 0.00; absent approvals: MJS 2462.44, MRS 3267.84 (room 7000.00); None sublimit: 0.00 / 0.00; HVAC growth: 1713.04 / 1487.44; built 1985: MJS 2037.44.
- Half-cent sweep over every scored, factor-baseline and whole-baseline raw figure in both solve chains: no figure within 1e-6 of a half cent.
### A6 T1/T2
- T1: every factor's baseline substitution moves its result in its task world (check_compute COMPUTE OK; computations[].factor_sensitivity).
- T2: each ladder's condition reads evidence no other factor of the policy reads as a condition (dates of the estimate, credits and change orders; tier and trade count; property type and build year; growth location; ACV, advance and supplement payments), so a producible world exists where only that factor's tier changes.

## REWORK round 2
Audit read in full: _difficulty.md, 0.md, 1.md. Every item verified against the round-1 charter and worlds (all reproduced); closures:
- CG-1 CLOSED: every baseline sentence rewritten as the standard method/default value, silent about the factors (e.g. RMS "takes the lead-safe setup and asbestos sampling lines", CWW "counts the credit families only as settled below").
- CG-2 CLOSED: all 19 coinciding ladders removed; every new ladder keys on conditions independent of its formula inputs and keeps the pairs apart (A7 table above).
- CG-3 CLOSED: RMS lead_setup_counting and IDR incurred_cost_shortfall removed; every new tier is reachable inside its own scope (e.g. CWW Carrier Program tier is in the CWW scope; IDR contract T3 = substantially_complete contract).
- CG-4 CLOSED: overhead-only, relief, refund, threshold-cut and drawings-keyed ladders removed; replacement levers are base-grounded (claims O&P and program discount, water reassessment sentence, RRP/NESHAP year cutoffs, deductive credit without markup, change order markup). Goodwill re-enters CWW only as an estimate-source family on an incurred-price basis (flagged in KNOWN RISKS).
- CG-5 CLOSED: no factor reads another factor's binding; CWW pricing factors decide multipliers combined in the assembly; MOW removed.
- CG-6 CLOSED: every policy rebuilt to the draw (T0 6/6/6/6, T1 5/4) with distinct, record-keyed tiers.
- CG-7 CLOSED: task 1 no longer posts a write-off; CWW declares a scoped overwrite of "carrier_denied_line records a line the carrier declined after approval;" naming the carrier act (decline at final-invoice review) and restating the base meaning for every other write-off.
- CG-8 CLOSED: each overwrite restates the retired clause for every other write (CWW meaning, MRS recording clause naming the protocol supplement, IDR amount sentence).
- CG-9 CLOSED: "less earlier write-offs of it" computed through source_approval_id; coverage filters stated in the rules; S_cat "never below zero" stated; probes show rule = compute on edge worlds.
- CG-10 CLOSED: MOW removed; compute_basis verbatim sweep over all six policies finds no miss.
- CG-11 CLOSED: every assembly sentence combines generically ("each family/deduction settled below").
- CG-12 CLOSED: RMS has no room; its assembly fixes sum then rounding.
- CG-13 CLOSED: every prerequisite sentence is action form with a declared fallback reason and a record-visible condition; proofs cite only seeded fields.
- CG-14 CLOSED: every wait carries its carve-out ("where it reaches the supplement minimum", "where it comes to more than nothing and within the desk write-off cap").
- CG-15 CLOSED: tool bodies reject non-positive or non-numeric amounts and non-integer or below-1 sequence numbers before writing (Error strings, nothing recorded).
- CG-16 CLOSED: MOW/MRS pair gone; MJS and MRS treat attic regulated work alike (asbestos only); CWW and IDR both treat goodwill as lowering the incurred price.
- CG-17 CLOSED: subjects restated to what the formulas keep (CWW names credited, conceded and removed work; S_cat price_variance; RMS scope_omission).
- T0-1 CLOSED: the unproducible release request row is gone; no factor reads release requests.
- T0-2 CLOSED: design_rationale and proofs regenerated from the recomputed world; every why_false cites seeded fields (credit and change-order dates, categories, reasons).
- T0-3 CLOSED: the rationale carries no line counts; every figure in it was recomputed.

## Final gate block (no --task), rework round 2
check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks REPLAY OK (0.json 22 acts, 1.json 14 acts, closures match);
check_solvability SOLVABILITY OK; check_compute COMPUTE OK (suite means branches 110.50, steps 18.00; history_rows_max 10; branches_max 145);
check_grounding GROUNDING OK; check_cross_fire SCOPE OK. check_traceability deferred until docs are published.
Values: T0 write-off 498.62, regulated-scope supplement 2326.95, reassessment supplement 1172.85, release 2273.53; T1 protocol supplement 2457.15, final mold supplement 810.69.
REWORK round 2: gates 7/7 green

## REWORK round 3 — plan (written before changes)
Audit revision_2 read in full (_difficulty.md r2, 0.md r2, 1.md r2); open ids CG-1, CG-4, CG-5, CG-6, CG-7, CG-9, CG-16(a-d), CG-17, CG-18, CG-19, CG-20, CG-21; every finding re-derived against the r2 charter and both worlds (all reproduce).
Approach: keep both trees; IDR treats every pending dwelling supplement as an expected approval against billed cost (one principle, closes CG-16(c));
CLW keyed on the credit and change-order records (no carrier act, CG-7), tie-free last-day equipment tiers (CG-20); effect labels by A7 shape (CG-18);
world fixes for CG-16(b)/(d); MPS/MRS regulated ladders keyed on the file's ordinance-or-law limit and the job (CG-21); MRS claims every billed line family (CG-17); tool bodies write themselves (CG-19, done).

## XF tables (round 3; supersede the round-2 tables)
### A7 all-pairs method table (effect labels follow the shape: method = a tier adds an input or an operation; parameter = tiers select values)
- RSS: rrp_cleanup_scope METHOD (HEPA | containment + HEPA | 0: adds an input); disposal, PPE, renovator labor, tear-out, verification labor PARAMETER (data-selected lines or a tier rate).
- CAT: extraction, carpet, monitoring, air scrubber PARAMETER (rate tables of the recorded tier); PPE METHOD (billed tech-days x rate gap | technician labor line count x recorded-tier rate: different inputs); antimicrobial METHOD (affected area x recorded-tier rate less billed, floored | billed sq ft x rate gap).
- CLW: billing_error, duplicate_line, goodwill inclusion PARAMETER (all credits | credits on the last equipment day | 0); removed_scope METHOD (all change order credits | credits less additive charges net of markup, floored | 0); water-line and contract-scope pricing PARAMETER (program discount | overhead + profit | 1).
- IDR: contract cost, water cost METHOD (paid | final invoice | amount + change orders - credits; final - credits | final | posted charges); code holdback cut METHOD (excess | whole | 0); deductible carry, advance recoupment, supplement depreciation paid PARAMETER (clamp regions of distinct records).
- MPS: surface METHOD (area x soda rate | fixed handler + coil fees | area x brush + encapsulation rates); removal, air, regulated fee PARAMETER.
- MRS: surface, removal, air, regulated lines PARAMETER (data-selected line families); labor METHOD (labor with the after-hours part divided by the tier multiplier | supervisor labor only | all labor).
- Pair check: no tier formula equals another tier's formula over that tier's whole producible domain (every fall-through domain contains worlds where the other formulas are non-zero: downward reassessments for CAT, credits off the last equipment day for CLW, ordinance-or-law files and HVAC jobs carrying billed regulated lines for MPS/MRS).
### A1 factor-reads: every factor reads only its own bindings and plain baseline bindings (IDR advance now carries its own initial-withheld and ACV reads; CLW last-day families each carry their own per-type lookups).
### Multi-source (CG-21): MPS protocol_regulated_fee and MRS final_regulated_lines combine the claims file's ordinance-or-law limit with the mold job's growth location, property type and build year; task 0 keeps CLW removed_scope (rebuild change order dates against the claims estimate date).
### B2 probes (r3/probes.py, scratch; figures kept out of this section's REWORK list)
- Absent water job / contract / approvals / payments, None estimate, None deductible, zero estimate, None year_built, decoy water job and cancelled contract of another file listed first, a second scope_omission request, category not reassessed, Clean tier recorded category_3, supplement paid in full, ACV net of deductible and advance: no exception; decoys leave every figure unchanged.
- Date edges: estimate on the invoice date takes the invoice tier (inclusive); estimate on the drying complete date falls through; estimate between drying complete and invoice takes the last-equipment-day tier; change order credit on the estimate date gives no removed scope; additive charge on the credit date takes the swap tier.
- T1: absent mold jobs / approvals, None sublimit, ordinance-or-law file, HVAC, living-area growth, 1985 build year, two jobs awaiting clearance: no exception.
- Edge skips on the T0 chain recomputed through the real tools; every skipped edge moves the release.
- Half-cent sweep over every scored, factor-baseline and whole-baseline raw figure: no hit. compute_basis verbatim sweep: no miss.

## REWORK round 3
Audit revision_2 read in full (_difficulty.md r2, 0.md r2, 1.md r2) and realism_bar.md; each item verified before change (all reproduced, none disputed).
- CG-1 CLOSED: CAT baseline restated as a default ("starts from nothing; a line family adds a difference only as settled below"); no other baseline names a tier or method.
- CG-4 CLOSED: MRS labor HVAC tier now keeps the supervisor labor and drops only the technician time the per-vent and per-unit HVAC cleaning fees already price (no performed labor valued at nothing); swept all ladders for X4 shapes.
- CG-5 CLOSED: IDR advance_recoupment_rule reads its own initial-withheld and ACV bindings; A1 sweep over all six policies clean.
- CG-6 CLOSED: after relabelling by shape every policy meets the floor with distinct tiers (RSS 5p/1m, CAT 4p/2m, CLW 5p/1m, IDR 3p/3m, MPS 3p/1m, MRS 4p/1m).
- CG-7 CLOSED: CLW's scoped overwrite now records the approved value of work the jobs credited, conceded or removed after the approved estimate carried it, keyed on the credit and change-order records; no carrier act is asserted (RULE-3); tool docstring aligned.
- CG-9 CLOSED: MPS and MRS scopes require a loss_type other than mold, so no part of the initial approval is a mold amount and the supplement-approval sum is the mold approved amount; IDR/CLW approval reads swept (rules say what they sum).
- CG-16 CLOSED: (a) RSS states the approved estimate leaves regulated-material work to its own supplement, CLW states the invoice-built estimate carried the invoiced mitigation lines, CAT no longer asserts any approved-scope fact (its regulated-line family and its read of the regulated-scope supplement are gone); (b) the billing_error credit now sits on a line no supplement prices, and RSS and CAT scopes exclude credits on any line they read; (c) IDR carries every pending scope_omission and price_variance supplement as an expected approval against billed cost, consistent with CLW's billed-work premise; (d) the attic job bills no lead-safe setup, and MPS and MRS share one regulated ladder.
- CG-17 CLOSED: MRS subject claims every line family billed on the job awaiting clearance as its ladders settle them; core now includes PPE, clearance test and minimum charge lines, labor includes business-hours labor.
- CG-18 CLOSED: effect labels re-set by A7 shape (CAT carpet and scrubber, CLW pricing pair, MPS air and regulated fee, MRS air now parameter; CAT PPE and antimicrobial, CLW removed scope, MPS surface, MRS labor are method with an added input or operation).
- CG-19 CLOSED: every write tool calls ctx.create (and ctx.update for the write-off) in its own body; the helper only checks arguments and builds the row.
- CG-20 CLOSED: CLW middle tiers take the credits against the equipment-day lines dated on the last equipment day, one lookup per equipment type (one line per type per day), and the duplicate tier matches by line amount, so no same-day tie decides the figure.
- CG-21 CLOSED: MPS and MRS regulated ladders combine the claims file's ordinance-or-law limit with the mold job's fields (two records).
- Observation (r2) on RSS containment/HEPA dates: rules now say "latest" containment setup / HEPA line.
- No factor needed the R6 waiver tier.

## Final gate block (no --task), rework round 3
check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK;
check_grounding GROUNDING OK; check_cross_fire SCOPE OK. check_traceability deferred until docs are published.
REWORK round 3: gates 7/7 green

## REWORK round 4 — plan (written before changes)
Audit revision_3 read in full (_difficulty.md r3, 0.md r3, 1.md r3) with realism_bar.md; open ids CG-6, CG-18, CG-20, CG-22, T0-R3-1, T1-R3-1, all re-derived (all reproduce).
Plan: one A7-passing method per policy (RSS PPE tier adds a tariff parameter; MPS air prices equipment over the job's recorded containment/work window held to the cap; MRS HVAC labor nets the HVAC cleaning lines with a floor);
CLW duplicate tier redefined on a reachable record (moisture-mapping duplicates, R6); RSS verification labor skips a HEPA day that is also the containment day (CG-22);
restore CAT <- RSS through a regulated-cleanup difference family (unique numbering); seed job B balance_due = charges less payments.

## XF tables (round 4; supersede round 3 where they differ)
### A7 all-pairs table for every method factor (a pair passes only if one tier adds an input or an operation)
- RSS regulated_ppe_line: T1 PPE lines billed (record sum) | T2 one technician-day at the tier PPE rate (tariff parameter, no record sum) | T3 0. T1/T2 different inputs; T1/T3 and T2/T3 non-zero on the fall-through domain (PPE billable without asbestos or lead; tier rate). PASS. rrp_cleanup_scope relabelled parameter.
- CAT reassessed_ppe: billed tech-days x rate gap | technician labor line count x recorded-tier rate | 0 — different inputs. PASS. reassessed_antimicrobial: affected area x recorded-tier rate less billed, floored | billed sq ft x rate gap | 0 — area input plus floor. PASS. reassessed_regulated_cleanup is labelled parameter.
- CLW removed_scope_inclusion: all change order credits | credits less additive charges divided by one plus markup, floored | 0 — adds charges, tariff and floor. PASS.
- IDR contract_cost_measure (payments | final invoice | amount + charges - credits), water_cost_measure (final - credits | final | posted charges), code_holdback_cut_rule (withheld - change order charges | whole withheld | 0): each pair differs by an input. PASS.
- MPS protocol_air_treatment: T1 containment fee + (scrubber + dehumidifier rates) x min(cap, days from containment date to clearance request) | T2 scrubber rate x min(cap, days from scheduled start to clearance request) | T3 dehumidifier rate x cap. T1/T2: containment fee, a second rate and a different date window; T2/T3: a data-selected window under a min against a bare tariff cap; T1/T3: fee, window, min. PASS. protocol_surface_method relabelled parameter.
- MRS final_labor_basis: T1 labor less after-hours labor plus after-hours labor divided by the tier multiplier | T2 max(0, labor less HVAC cleaning lines) | T3 labor. T1/T3: tariff division; T2/T3: another record's lines and a floor; T1/T2: different inputs and operations. PASS.
- Floors after the table: RSS 5p/1m, CAT 4p/2m, CLW 5p/1m, IDR 3p/3m, MPS 3p/1m, MRS 4p/1m.
### Impossible-case sweep (CG-20 class): every tier of every ladder checked against the owning charter's grain and billing rules; the CLW duplicate middle tier now keys on moisture mapping, booked once per job (a second line is a producible double-keyed duplicate); equipment-day and monitoring tiers rely only on one line per type per day.
### Same-line double-claim sweep (CG-22 class): RSS renovator (containment day) and verification (HEPA day) labor are disjoint by role on housing and by date on commercial; MRS labor and core share no line; CAT prices rate gaps, never the lines RSS claims; CLW credit families are disjoint by reason and one credit per line.
### Seed-state sweep (T1-R3-1 class): every job and contract balance equals charges less payments and credits (job B carries its open charges; closed jobs and the contract carry zero); claims receivables equal approvals less payments.
### B2 probes (r4/probes.py): round-3 table re-run plus missing containment date, early clearance request, HVAC tier labor floor, commercial HEPA on the containment day, log-based estimate duplicate tier; no exception, decoys unchanged, every skipped edge moves its dependent, no half-cent hit, compute_basis verbatim.

## REWORK round 4
Audit revision_3 read in full (_difficulty.md r3, 0.md r3, 1.md r3) and realism_bar.md; every finding verified before change (all reproduced, none disputed).
- CG-6 CLOSED: every policy keeps at least one method that passes the literal A7 pair test and at least two parameters (table above).
- CG-18 CLOSED: RSS method moved to regulated_ppe_line (tariff-rate tier) with rrp_cleanup_scope relabelled parameter; MPS air prices equipment over the job's recorded containment or work window held to the cap (data-selected window and min), surface relabelled parameter; MRS HVAC labor tier nets the HVAC cleaning lines with a floor; all-pairs table written for every method.
- CG-20 CLOSED: CLW duplicate-line middle tier takes duplicate credits equal to the tier's moisture mapping fee (moisture mapping is booked once per job, so a second line is a reachable double-keyed duplicate the log-based estimate copied); whole-charter impossible-case sweep done. R6: this tier is tagged R6 (keyed on a recorded fee, plausible, no base conflict, not X1-X4, XF-clean, the only R6 factor).
- CG-22 CLOSED: RSS commercial verification labor skips a HEPA date that is also the containment setup date; class sweep found no other line claimed twice.
- T0-R3-1 CLOSED: CAT <- RSS restored through CAT's regulated-cleanup family (a pending scope_omission supplement naming the job turns the HEPA difference into the containment and HEPA difference, reasoned on the Black Water cleanup standard, with no approved-scope assertion); supplement numbering is now forced and the terminal state unique.
- T1-R3-1 CLOSED: job B balance_due now equals its charges less payments and credits; balances across both worlds swept.

## Final gate block (no --task), rework round 4
check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK;
check_grounding GROUNDING OK; check_cross_fire SCOPE OK. check_traceability deferred until docs are published.
REWORK round 4: gates 7/7 green

## REWORK round 5
Audit revision_4 read in full (_difficulty.md r4, 0.md r4, 1.md r4) and realism_bar.md; CG-4 and CG-6 verified (both reproduce: the round-4 HVAC tier could value performed labor at nothing and fell as vents were added). Task 0 artifacts left as passed; edits confined to MRS, the task-1 world and task-1 proof text.
- CG-4 CLOSED: MRS final_labor_basis no longer nets anything out of labor. Its three treatments differ only in how the after-hours premium is taken: attic or crawlspace growth takes the after-hours part at the business-hours rate (the premium is the customer's choice in an unused space); HVAC growth keeps it as billed (the system can be shut down for cleaning only outside working hours); living-area or basement growth follows the standard method, which takes the premium as the owner's choice in a single-family house or condominium unit and as billed in a multifamily unit or commercial property (shared occupancy). Labor is never valued at nothing and rises with every hour billed; probed over every growth location x property type x added after-hours labor (r5/labprobe.py), and HVAC cleaning lines no longer enter labor at all.
- CG-6 CLOSED: MRS keeps one method that passes XF A7: T1 adds the tier multiplier as a division, T3 adds a conditional pick on the job's property type, T2 is the plain sum; every pair differs by an input or an operation. MRS floor 4 parameter / 1 method; no other policy changed.
- Task-1 world: the mold jobs' property type is a multifamily unit (the insured lives in one side of a two-family house she owns), so the labor family bears weight against its standard treatment; the persona, read objectives and rationale were updated; MPS and MRS regulated tiers (housing built before the RRP cutoff) are unaffected.
- Probes re-run on a scratch copy (r5/probes.py, r5/labprobe.py): no exception, decoys unchanged, no half-cent hit, compute_basis verbatim.
REWORK round 5: gates 7/7 green

## REWORK round 6
Renderer findings render_r1.md read in full; each verified against the charter (1a, 1b and 2 reproduce; the A6-T2 note reproduces). Edits are scope sentences and one compute guard; no scored value moves.
- 1a CLOSED: the credited-line write-off scope now requires the insured to hold at most one reconstruction contract, linked to the file when held, so its customer-wide change-order credit and charge reads are this file's contract; the signed-date and markup reads were already keyed to the file.
- 1b CLOSED: the regulated-scope, reassessment and credited-line scopes now read "holds exactly one water mitigation job, and that job is linked to the file" (the release's form), so every water read is that job; class sweep: the mold policies now read "exactly two mold jobs, both linked to the file" (their reads were already keyed to the job), and the release's scope already covered its water and rebuild reads.
- 2 CLOSED: the supplement-depreciation-paid compute drops the unstated "some supplement approval exists" condition, so with no supplement approval the first tier takes the whole withheld amount on no approvals, which is zero, exactly as the rule reads; class sweep of every ladder found no other compute-only condition.
- A6-T2 note (water_line_pricing_basis, contract_scope_pricing_basis) CLOSED as R6: both are real conversions the claims charter states (program pricing discount, overhead and profit at the trade minimum), bear weight on the task world (A6 T1 holds), but can move the result only through a credit family that is itself factor-decided, so T2 cannot hold by construction; tagged R6 under realism_bar.md (recorded keys, plausible, no base conflict, not X1-X4, needed to meet the policy's drawn count). R6 factors now: these two and the duplicate-line middle tier.
- Probes re-run on a scratch copy (r6/probes.py): no exception, decoys unchanged, every skipped edge moves its dependent, no half-cent hit, compute_basis verbatim.
REWORK round 6: gates 7/7 green

## REWORK round 7
Audit revision_6 read in full (_difficulty.md r6, 0.md r6, 1.md r6). Coordinator ruling recorded: the drawn factor count is gate-enforced, so the two pricing factors stay; the T2 waiver is not granted because they acted only through other factors' outputs (XF A4); route = the standard method defines the credit families at a stated default, the inclusion factors narrow them from records, and the pricing factors act on that baseline-defined quantity.
- CG-23 CLOSED: the credited-line write-off's standard method now takes every credit recorded on the water job (billing_error, duplicate_line, goodwill) and every change order credit on the contract at their recorded amounts; each inclusion ladder narrows its family (estimate built from the scope sheet: none; built from the drying log: the last-day equipment credits, or the moisture-mapping duplicate; otherwise the standard family), the change-order ladder narrows by the estimate date and the owner-upgrade swap, and the two pricing factors multiply families the standard method already defines, so with every other factor at baseline each of the six moves the result (A6 T1 and T2 both checked on the task world, r7/t2check.py); no factor reads another factor's binding, and the combination sentence stays generic and ordered (families as the standard method takes them, each narrowed, each priced, then approval share, hold, rounding).
- Because inclusion factors now narrow rather than add, the task-0 world had to take narrowing tiers for them to bear weight: the estimate now falls between the water job's drying completion and its invoice (invoice date moved later), a second, thermal-imaging duplicate credit was seeded, and the owner-upgrade change order now follows the deductive credit (re-sized and renumbered to stay within the rebuild charter's change-order minimum). Task-0 scored figures moved honestly as a result (write-off and release; the two supplements are unchanged); every proof, tracing, edge-skip and rationale sentence was regenerated from the recomputation.
- Task 1 untouched (its file is content-identical; only key order of the replay closure differs).
- Probes re-run on a scratch copy (r7/probes.py): no exception, decoys unchanged, every skipped edge moves its dependent, no half-cent hit, compute_basis verbatim. R6 factors now: only the duplicate-line middle tier.
REWORK round 7: gates 7/7 green

## REWORK round 8
Renderer findings render_r2.md read in full; the new item reproduces (the code holdback cut's rule said the file's supplement approvals while compute reads dwelling supplement approvals only).
- code_holdback_cut_rule (XF B1, coverage part) CLOSED: the rule now says "the file's dwelling supplement approvals" in both places, matching compute; the compute_basis quotes regenerate from the rule sentence and stay verbatim.
- Class sweep (filters present in compute but absent from the rule, and the reverse; coverage part, approval type, event type, status, payment type, supplement reason, adjustment reason, rate window, charge code) over every read of all six policies: one further member found and closed — the release's pending supplements were read for every coverage part while the expected approvals they join are dwelling approvals; the rule now names dwelling scope_omission and price_variance supplements and the compute filters coverage part dwelling (no scored value moves). Every other read matches its rule: approval reads name initial/supplement and dwelling where the compute filters them, payment reads name their payment type and coverage, credit reads name their reasons, mold reads name the job awaiting clearance, and the mold approved sum and the pending mold requests rely on the stated scope tests (every supplement approval decides a mold supplement; none decides one naming the job awaiting clearance).
- Probes re-run on a scratch copy (r8/probes.py): no exception, decoys unchanged, every skipped edge moves its dependent, no half-cent hit, compute_basis verbatim.
REWORK round 8: gates 7/7 green

## REWORK round 9
KB audit files read in full (audits/policy_kb/insurance_claim_services/{_difficulty,0,1}.md, audits/runtime_context/insurance_claim_services/{0,1}.md); the published water and mold docs (docs/water/, docs/mold/) read to re-price rows. KB-1..KB-3 are render-side (renderer). Each SRC item verified (all reproduce).
- SRC-1 CLOSED: the three task-0 water lines governed by published extended water pricing re-priced under it — the final HEPA vacuuming line (vacuumed floor from the pad and carpet detach-and-reset lines with the affected area, cut-cavity wall area by category, plate strip by class, regulated pass factor; dated the drying complete date), the tear-out antimicrobial line (treated floor with the detach-and-reset area, class-based wall area, coverage factor, wet-wipe rate multiplier; dated the latest flood cut) and the tear-out debris haul-off line (flooring, class-based drywall and pre-1978 trim loads, rounded up, Category 3 sanitation multiplier; dated the latest flood cut).
- SRC-2 CLOSED: the task-1 mold job awaiting clearance now carries the published work-plan visit line (supervisor labor, dated the opened date), its pre-removal asbestos sampling line priced and dated per the published sampling tariff (standard set plus the attic insulation set, opened date) and one bagged debris haul-off line (loads by the published capacities plus the one-trip charge, dated the latest removal); class sweep: the closed mold job (also returned by the gold read) re-priced the same way, and both mold jobs now carry the signing deposit the published agreement rule requires on the signing date (tier deposit less the claim coverage credit, plus the route raise and lead dust-wipe prepayment, plus the lines booked by then), with the closed job's final payment and the open job's balance due recomputed.
- Exhaustive seed pass, re-priced or re-seeded row ids (every other-product row the gold reads was checked against its owning product's published docs as of its posting date; rows not listed price at their tier's unit rate times quantity and needed no change): task 0 — water_charges dfcb5d91 (final HEPA), 8d8a3073 (tear-out antimicrobial), 6a153fab (tear-out debris haul-off); water_payments 8d3ff78c (customer payment, follows the new final invoice); water_jobs cb1a3090 (final invoice); claims_payments f7b40a4a, 3739ffe1, 21f015ad (payee route insured_only, matching the customer checks the jobs carry); rebuild rows unchanged (no rebuild docs published). Task 1 — mold_charges e9aa7226 (closed job sampling date), 851125e7 (closed job work-plan visit, new), c66dc877 (closed job haul-off), 5c4a8543 (open job sampling), 27ca343a (open job work-plan visit, new), fed77ad8 (open job haul-off); mold_payments c7d76fac and 483208cc (signing deposits, new), a93431e5 (closed job final payment); mold_jobs 13b3e213 (final invoice) and 78c1f5e2 (balance due).
- Consequences stated honestly: task-0 regulated-scope, reassessment and release figures and task-1 final mold supplement figure moved with the seeds (write-off and protocol supplement unchanged); every proof, tracing, edge-skip, rationale and worklog-independent text regenerated from the recomputation.
- Class sweep (rule vs billed-rate wording found while re-pricing): the reassessment rule spoke of "the rate billed" while compute reads the dispatch tier's rate (they now differ on the wet-wipe antimicrobial line); every such phrase now says "the dispatch tier's rate".
- SRC-3 CLOSED: the contract read objective now prints the recorded final invoice (generated from the seed).
- SRC-4 CLOSED: cleaning_verification_labor restates its test on the records (a HEPA date that is also the latest containment setup date takes none) without naming the renovator factor; final_regulated_lines drops "as the protocol supplement prices it"; sweep found no other factor text naming another factor or policy.
- Probes re-run on a scratch copy (r9/probes.py): no exception, decoys unchanged, every skipped edge moves its dependent, no half-cent hit, compute_basis verbatim.
REWORK round 9: gates 7/7 green

## REWORK round 10
- SRC-5 CLOSED: the task-0 deductive carpet-install change order (co3) and its credit (rp_cr) are now priced by the published rebuild deductive-credit rules: change-order part none, contract part at the carpet-install tier rate, less the fixed field-remeasure change-processing deduction (construction started on or before the signing date); proof text regenerated.
- SRC-6 CLOSED: task 0 now carries a second permit-expediting line (r_xe, electrical permit, Standard rate) beside the building-permit expediting line, so expediting is billed once per permit type pulled; contract final invoice regenerated from the seed.
- Exhaustive pass, task 0 re-priced rows: rebuild_change_orders co3; rebuild_payments rp_cr; rebuild_charges r_xe (new); rebuild_contracts rb final_invoice_amount; rebuild_draws dr3, dr4 and their payments pdr3, pdr4; rebuild_payments p_final. Every other rebuild row (contract sum, permit fees, plan drawing, lead-safe setup, owner-upgrade change order co2, dr1/dr2) re-checked against docs/rebuild as of its posting date and unchanged; every water row (charges, billing_error / duplicate_line / goodwill credits, customer payment, final invoice) re-checked against docs/water and unchanged; own-category history (approvals, withheld depreciation, advance, supplement payment, prior supplements) re-checked and unchanged.
- Exhaustive pass, task 1: every mold row (protocol, containment, removal, air, clearance, payments) re-checked against docs/mold, every contents row against docs/contents, and own-category history; no row needed re-pricing.
- claims.extended.yaml and task_tools.py byte-identical (sha256 checked); only tasks/0.json seeds and the proof text they drive changed; all T0 proof text (amount tracings, factor cards, edge skipped effects, read objectives, world rows) regenerated and swept for stale figures.
- Probes re-run on a scratch copy (r10/probes.py): no exception, decoy/absent/None/zero/date-edge probes behave, every skipped edge moves its dependent, no half-cent hit, compute_basis verbatim.
REWORK round 10: gates 7/7 green

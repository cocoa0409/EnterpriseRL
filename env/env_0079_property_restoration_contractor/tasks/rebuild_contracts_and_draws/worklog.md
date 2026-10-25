# worklog — rebuild_contracts_and_draws (env_0079), M=2

## Step 0 — draws (draw_counts.py --tasks 2)
- task 0: prerequisite_problems=1, factor_counts=[6,6]
- task 1: prerequisite_problems=2, factor_counts=[5,5,5]

## Difficulty pre-check
- Base read: rebuild.yaml (policies rebuild_agg_*, contract_signing, cancellation, permits_and_fees, change_orders,
  draws, evt_payments, overdue_draws, completion, warranty), db_schema rebuild_* / claims_* / water_jobs / account_agreements,
  share_tools (find_* per table, verify K=2 of phone/email/zip).
- Account charter (E9): no account rule binds rebuild pricing (checked every account policy rule).
- DSL-KNOWN: P('draw_schedule') is a mapping and the DSL has no subscript, so a milestone-percentage draw cannot be
  computed without restating tier data; only the substantial_completion draw (remainder) is used.
- BLUEPRINT-KNOWN candidates:
  1. rebuild_draws.dr_once dedup correlation (rebuild_contract_id, draw_milestone) needs a pre-action system value for
     draw_milestone, which a not-yet-requested milestone cannot have; the solvability binding cites
     rebuild_contracts.final_invoiced_date (empty, None) only to satisfy the structure.
  2. Payments must name a draw, so charges outside the contract sum (permit, professional fees) can only be paid through a
     draw; the final draw bills them as pass-through charges (fd_pass_through).
  3. No decline/void event for change order proposals exists in this difficulty, which is what makes the final-draw
     state-form prerequisite single-resolver (only the signature clears "awaiting signature").

## Scope ledger
| task | policies | tools |
|---|---|---|
| 0 | rebuild_ext_change_order_signature, rebuild_ext_final_draw | sign_change_order_7ffbf290 (user), request_final_draw_345d01eb (agent) |
| 1 | rebuild_ext_deductive_signature, rebuild_ext_overdue_draw_charge, rebuild_ext_draw_payoff | sign_deductive_change_order_5bfd6b95 (user), post_overdue_draw_charge_f6859441 (agent), pay_past_due_draw_ec4ba96a (user) |

## XF_recipe tables (task 0) [ROUND 1 — SUPERSEDED by REWORK round 2 below; figures and factor names here are historical]
### A1 factor-reads table (factor -> bindings it reads -> owner)
| factor | reads | owners |
|---|---|---|
| co_quantity_unit | qty_scope (own LATEST), co_qty | own / plain |
| co_price_basis | up_kind, up_upgrade_allowance (own), co_written_price, co_scope, scope_rate, F(funding_source) | own / plain |
| co_overhead_profit | mk_kind, mk_carrier_line, mk_trades, mk_min_trades, mk_op_pct (own), F(funding_source), F(claim_file_id) | own / record |
| co_wall_treatment | wt_scope, wt_wall_line, wt_water_category, wt_fire_job, wt_mold_job (own), F(mitigation_job_id) | own / record |
| co_lead_safe | ls_scope, ls_applies, ls_setup_lines (own), F(property_type), F(year_built) | own / record |
| co_plan_review | pr_kind, pr_scope (own), F(permit_required) | own / record |
| fd_state_retainage | rt_days_since_completion, rt_texas (own), current_sum, remainder | own / plain |
| fd_code_upgrade_hold | ch_code_total, ch_ol_limit (own) | own |
| fd_carrier_unfunded | hc_withheld, hc_released, hc_unreleased, hc_deductible (own) | own |
| fd_punch_list_hold | pu_days_since_completion, pu_reports, pu_inspections (own) | own |
| fd_owner_selection_hold | ug_upgrades (own), F(funding_source) | own |
| fd_pass_through | pt_direct_dwelling, pt_carrier_lines, pt_all_outside (own) | own |
No factor reads another factor's binding; assembly (co_line, wall_treatment, result; current_sum, remainder, held_total, result) is plain.

### A3 defining-sentence table (rule sentence -> owner)
- change_order_signature: scope sentence -> plain/overwrite; "The signature is the customer's own act..." -> plain; "The change order line is read from..." -> plain (co_qty/co_scope/co_written_price); baseline 4 sentences -> baseline; assembly sentence -> plain (result); "For every change order outside..." -> overwrite restatement; selling-unit sentence -> co_quantity_unit; unit-price sentence -> co_price_basis; markup sentence -> co_overhead_profit; wall-closing sentence -> co_wall_treatment; lead-safe sentence -> co_lead_safe; plan-review sentence -> co_plan_review; minimum sentence -> inherited base gate.
- final_draw: scope sentence -> overwrite; prerequisite sentence -> prerequisite; current sum / earlier draws / remainder sentences -> baseline (plain bindings); assembly sentence -> plain (held_total, result); held-amounts release sentence -> overwrite restatement; retainage sentence -> fd_state_retainage; code-upgrade sentence -> fd_code_upgrade_hold; carrier-hold sentence -> fd_carrier_unfunded; punch-list sentence -> fd_punch_list_hold; upgrade sentence -> fd_owner_selection_hold; pass-through sentence -> fd_pass_through.

### A7 all-pairs method table
- co_quantity_unit: whole-sheet ceiling (adds FloorDiv by sheet area) / whole-yard ceiling (FloorDiv by yard) / waste multiplier (adds a percentage input) / as written. Pairs: sheet vs yard differ by the divisor input AND operation is the same ceiling — distinguishing input: the unit area; ceiling vs waste: operation differs (ceiling vs multiply); any vs as-written: adds an operation. PASS.
- fd_state_retainage: percentage of the current contract sum (base input current_sum) / greater-of (adds a max over two inputs) / tier percentage of the remainder (input remainder). Each pair differs by input or operation. PASS.

### B2 decoy / absent-record probes (run on scratch copies, see results below)
### T1/T2
T1 = factor_sensitivity on task world (all move, see task 0 run). T2: each factor's T1 world is the task world itself.

### B2 probe results, task 0 [ROUND 1 — SUPERSEDED by REWORK round 2 below; figures and factor names here are historical] (scratch copies; [change order amount, final draw])
| probe | result |
|---|---|
| as seeded | [2140.28, 17041.10] |
| decoy voided proposal written later (tile) | [2140.28, 17041.10] (LATEST is filtered on pending_signature) |
| absent mitigation job | [1937.33, -] (no wall-closing treatment, as the rule states) |
| dwelling depreciation fully released | [-, 21277.50] (carrier hold falls to the deductible) |
| decoy contents approval withholding depreciation | unchanged (coverage_part filter) |
| second, withdrawn claim file of the customer | unchanged (reads keyed on the contract's claim_file_id) |
| contract self_pay | [1832.72, 16271.25] (tier price, tier markup, upgrade deposit share, all outside lines) |
| Louisiana address | [-, 23971.80] (tier retainage 0) |
Same-day ties (B3): the change order read is restricted to a contract with exactly one proposal awaiting signature.

## Task 0 — closed [ROUND 1 — SUPERSEDED by REWORK round 2 below; figures and factor names here are historical]
Tree: rebuild_ext_final_draw <- (value_input, state, affirmative) rebuild_ext_change_order_signature (user).
Handling-time run: change order 2140.28 (baseline 1356.71); final draw 17041.10 (baseline 33386.98); skip-signature 17255.13.
Capability cards: sign_change_order_7ffbf290 (user/write; marks the pending proposal signed with the signed amount, books one
change_order charge line, raises the balance; event rebuild_change_order_charge, triggers []); request_final_draw_345d01eb
(agent/write; creates one rebuild_draw_request row at the named milestone; event rebuild_draw_request, triggers []).

## XF_recipe tables (task 1) [ROUND 1 — SUPERSEDED by REWORK round 2 below; figures and factor names here are historical]
### A1 factor-reads
| factor | reads | owners |
|---|---|---|
| cr_billed_quantity | cq_scope (own), dc_qty | own / plain |
| cr_price_source | cp_scope, cp_upgrade_line, cp_allowance (own), dc_written_price, dc_tier_rate, F(funding_source) | own / plain |
| cr_overhead_return | op_trades, op_min_trades, op_pct, op_scope, op_added_same_scope (own) | own |
| cr_restocking | rs_scope, rs_special_order, rs_started (own), dc_signed_amount | own / plain |
| cr_permit_revision | pv_scope (own), F(permit_required) | own |
| ov_opening_balance | ob_recent_paid, ob_months_since_due (own), od_unpaid, od_requested, od_due | own / plain |
| ov_credit_application | cs_recent_credits (own), od_unpaid | own / plain |
| ov_owner_retention | tr_texas, tr_requested (own) | own |
| ov_agreement_rate | mr_agreement_status, mr_agreement_rate (own) | own |
| ov_period_share | ps_days_since_due (own), od_due | own / plain |
| py_overdue_carried | oc_on_draw, oc_on_contract, oc_suspended (own), pd_draw_id | own / plain |
| py_credit_applied | ca_recent_credits (own), pd_unpaid | own / plain |
| py_owner_retention | rh_texas, rh_requested (own) | own |
| py_outside_lines | ol_fee_lines, ol_trip_lines (own) | own |
| py_owner_selections | us_upgrades (own), F(funding_source) | own |
### A3 defining sentences
- deductive_credit: scope -> overwrite; "The credit is owed once..." / "The removed line is read..." -> plain; baseline 4 sentences; assembly -> plain result; quantity / price / overhead / restocking / permit sentences -> the five factors.
- overdue_draw_charge: scope -> overwrite; prerequisite sentence; unpaid sentence + baseline charge sentence -> baseline; assembly -> plain; opening-balance / credits / retention / rate / period-share sentences -> the five factors.
- draw_payoff: scope -> overwrite; secure-channel sentence -> plain; two prerequisite sentences; baseline sentence; assembly -> plain; overdue / credits / retention / outside lines / owner selections -> the five factors.
### A7 all-pairs method tables
- cr_billed_quantity: as task 0's quantity ladder (ceiling by sheet area / ceiling by yard / waste multiplier / as written) PASS.
- ov_opening_balance: unpaid + payments within the month (adds an input) / requested amount (different input) / unpaid. PASS.
- ov_period_share: (days - grace)/period (adds operation) / zero / one. PASS.
- py_credit_applied: subtract credits / subtract the lesser of credits and unpaid (adds a min operation) / nothing. PASS.
### B2 probes, task 1 ([credit, charge, payment])
| probe | result |
|---|---|
| as seeded | [902.74, 41.91, 11920.82] |
| agreement expired / absent | [-, 62.86, -] (tier rate) |
| decoy later carrier_direct draw | unchanged (route filter) |
| partial payment older than a month | charge basis falls to the requested amount (first-period tier), 41.91 |
| Louisiana address | [-, 46.80, 14016.82] (no owner retention) |
| work suspended | payment carries every overdue charge on the contract (same single charge) |
| construction not started | credit 1049.62 (cancellation-fee tier instead of restocking) |

## Task 1 — closed [ROUND 1 — SUPERSEDED by REWORK round 2 below; figures and factor names here are historical]
Handling-time run: credit 902.74 (baseline 868.80); charge 41.91 (baseline 194.40); payment 11920.82 (baseline 12960.00).
Skips: credit -> charge 44.02, payment 12823.56; charge -> payment 11878.91.
Capability cards: post_deductive_credit_4d7c3b22 (agent; one rebuild_change_order_credit row naming the change order, balance down;
triggers []); post_overdue_draw_charge_f6859441 (agent; one overdue_draw_charge row for the draw and YYYY-MM fee period, balance up;
triggers []); pay_past_due_draw_ec4ba96a (user; one rebuild_draw_payment row with a generated confirmation number, balance down;
triggers []). No written event triggers into another category (D7).

## Manual values gates (both tasks) [ROUND 1 — SUPERSEDED by REWORK round 2 below; figures and factor names here are historical]
- Prerequisite sentences: directions differ by result (charges "not fixed until", draw/payment "only after"); each names a record
  state only one write here produces; four-point test recorded in each dossier.
- Realism notes / risks for the audit: Texas owner retention (Tex. Prop. Code ch. 53) is stated without figures in prose
  (10 percent / 30 days live in params); punch-list hold uses the tier warranty trip charge and final cleaning fee; the plan-review
  and permit-revision items and the cleaning-verification fee (125.00) are company schedules; ladders with a duplicated zero
  outcome were avoided except where the fall-through is zero by base.
- DSL-KNOWN: half-cent residue; milestone percentages unreadable (see pre-check).
- Coverage: 5 policies, all claimed (task 0: 2, task 1: 3), pairwise disjoint; each fires at its gold call.
ROUND 1: gates 7/7 green

## REWORK round 2 — plan (audit revision_1: C-01..C-20, T0-1..T0-4, T1-1..T1-6)
- P1: scope narrowed to additive change orders and names the deductive sibling (C-01, C-19); escalation threshold kept in force (C-03);
  plan-review and lead-safe-setup items removed (C-02a/b, C-04, C-06); unit price no longer claims the written price is the carrier's
  (C-17): carrier price = approved supplement amount / quantity; quantity method re-shaped (ceiling vs greater-of minimum); new
  drying-verification factor (water job early release, IICRC class) and regulated-materials factor (RRP cleaning verification /
  asbestos sampling) — neither bills a base professional line.
- P2: overwrite of base S3 declared (C-02c); earlier draws counted before retainage (C-10); Texas retention one statute model shared
  with P4/P5 (C-14); punch-list and owner-selection holds removed (C-08, C-09); new depreciation hold, owner-share hold and
  mitigation-first hold; prerequisite sentence/condition narrowed to non-deductive proposals and matched (C-18, C-19).
- P3: replaced by a deductive change order SIGNATURE policy (user tool) that prices the credit at signing and books the credit line,
  so the credit equals the signed amount (C-01, C-07, C-17, C-19).
- P4/P5: scope = most recent customer-funded draw when every earlier customer-funded draw is paid in full (= oldest unpaid; C-11),
  tie by highest draw number (C-16), month window convention stated (C-15), owed fee periods defined (C-20), agreement-rate text
  completed (C-13), shapes repaired (C-05), outside lines summed not conditioned (C-12), upgrade amounts removed (C-09).

## REWORK round 2 [figures and factor names partly superseded by REWORK round 3 below]
### Dispositions (audit revision_1)
- C-01 CLOSED: deductive pricing moved to a deductive-signature policy (credit = signed amount, so balance and current sum agree); P1 and P3 overwrites each exclude the sibling's case by name.
- C-02 CLOSED: (a) plan-review item removed from P1, permit-revision deduction gone with old P3; (b) lead-safe setup no longer billed inside a change order (P1 bills only an RRP cleaning verification under an existing setup); (c) P2 declares the overwrite of base S3 for the substantial_completion draw.
- C-03 CLOSED: P1 restates that a material escalation line is allowed only above the tier's escalation threshold.
- C-04 CLOSED: co_lead_safe removed; co_regulated_materials never bills the per-contract setup fee, so nothing re-fires.
- C-05 CLOSED: co_quantity_unit -> co_billing_unit (ceiling vs greater-of-minimum vs written); cr_billed_quantity -> dc_unopened_units (floor vs subtract-and-floor-at-zero vs written); ov_opening_balance -> ov_balance_method (average adds an operation; requested drops the payments input); ov_period_share -> ov_period_anchor (first-charge-day anchor vs last-payment anchor vs whole period; dead zero tier removed); credit factors in P4 and P5 both labelled method (selection between the credit total and the unpaid amount, a conditional pick).
- C-06 CLOSED: carpenter-as-framing and finish-removal-as-permit-revision tiers removed.
- C-07 CLOSED: restocking on labor lines and the contract cancellation percentage removed with old P3.
- C-08 CLOSED: fd_punch_list_hold removed.
- C-09 CLOSED: P5 no longer adds upgrade amounts; P2 holds signed owner_upgrade amounts only on insurance_claim contracts inside the owner-share hold (carrier never funds them); no deposit-share tiers remain.
- C-10 CLOSED: earlier draws counted before retainage (requested / (1 - tier retainage)); withheld retainage requested only at retainage_release.
- C-11 CLOSED: P4/P5 scope = most recent customer-funded draw when every earlier one is paid in full, so it is the oldest unpaid draw the credit applies to.
- C-12 CLOSED: py_outside_lines sums fee and trip lines (no tier drops one when the other exists).
- C-13 CLOSED/DISPUTED in part: rule now states the agreement's minimum and grace are not applied (second reading closed). DISPUTED "tier 2 unreachable": tiers Minor..Full Structural carry no customer_types in their entry gates, so an insurance_carrier customer owning a property (carrier-owned building) can hold a rebuild contract and a Carrier Preferred Vendor Agreement; the tier is the complete-domain branch of the agreement terms. Domain note: an MSA customer's payment terms are applied to its rebuild draws by company rule (cross-difficulty read).
- C-14 CLOSED: one statute model in P2/P4/P5 — owner retention = Texas owner retention percentage of the contract price, held back from each customer-funded draw payment and the rest at the final draw (P2 subtracts that percentage of earlier customer-funded draws).
- C-15 CLOSED: P4/P5 state the month window: after the same day of the previous calendar month through the charge/payment date; a shorter previous month is wholly outside (= MONTHS()).
- C-16 CLOSED: tie rule = highest draw number; compute reads LATEST by draw_number.
- C-17 CLOSED: written unit price keeps its schema meaning (tier rate for install lines); the carrier price is the approved supplement amount divided by the quantity (P1: written quantity; deductive: quantity of the signed additive change orders naming the supplement). Seeds: unit_price 2.86 on install lines.
- C-18 CLOSED: P2 sentence and condition both "no proposal other than a deductive one awaiting signature".
- C-19 CLOSED: new user tool sign_deductive_change_order_5bfd6b95 records a deductive signature and posts its credit; P1's tool docstring scoped to additive proposals; P2's wait excludes deductive proposals.
- C-20 CLOSED: P4 defines owed fee periods (calendar months from the month containing the first charge day; the charge is for the earliest owed month without a charge, YYYY-MM); P5 sentence and condition use the same definition.
- T0-1, T0-2, T0-3, T0-4 CLOSED (via C-02, C-02c, C-17, C-04/05/06/08/09 and replacement factors co_drying_verification, co_regulated_materials, fd_depreciation_hold, fd_owner_share_hold, fd_mitigation_first).
- T1-1..T1-6 CLOSED (via C-01, C-02/C-06 removal, C-13 text, C-20, C-17, and the rebuilt factor sets); task 1 world rebuilt.

### Round 2 handling-time figures
- task 0: change order 2235.28 (baseline 1356.71); final draw 14628.00 (baseline 33481.98); skip signature -> 14851.53.
- task 1: deductive credit 344.73 (baseline 286.00); overdue charge 61.63 (baseline 209.21); payment 12108.08 (baseline 13947.53); skips: signature -> charge 63.01, payment 12452.81; charge -> payment 12046.45.
- All scored, baseline and sensitivity figures checked > 1e-6 from a half cent (closest: 2157.34975).

### Round 2 A1 factor-reads (no factor reads another factor's binding)
P1: co_billing_unit{qty_scope}+co_qty; co_price_basis{up_kind, up_supplement, up_approved, up_upgrade_allowance}+co_written_price, scope_rate; co_overhead_profit{mk_*}; co_wall_treatment{wt_*}; co_drying_verification{dv_*}; co_regulated_materials{rm_*}. Assembly co_line, wall_treatment, result.
P2: fd_state_retainage{rt_*}+current_sum, remainder; fd_code_upgrade_hold{ch_*}; fd_depreciation_hold{dp_*}; fd_owner_share_hold{os_*}; fd_mitigation_first{mf_*}; fd_pass_through{pt_*}. Assembly held_total, result.
P3: dc_unopened_units{uq_scope}+dc_qty; dc_carrier_price{cp_*}+dc_written_price, dc_tier_rate; dc_overhead_return{or_*}; dc_treatment_return{tr_*}; dc_processing_deduction{sf_*}.
P4: ov_balance_method{bm_*}+od_unpaid, od_requested; ov_credit_application{ca_recent_credits}+od_unpaid; ov_owner_retention{tr_*}; ov_agreement_rate{mr_*}; ov_period_anchor{ps_*}.
P5: py_overdue_carried{oc_*}; py_credit_applied{ca_recent_credits}+pd_unpaid; py_owner_retention{rh_*}; py_outside_lines{ol_*}; py_remobilization{rm_*}.

### Round 2 A7 method pairs
- co_billing_unit: ceiling vs max(minimum) (different operations); each vs written (adds an operation). PASS.
- dc_unopened_units: floor vs max(0, h - minimum) (different operations); each vs written. PASS.
- fd_state_retainage: Texas % of (sum less customer draws) vs greater-of vs tier % of remainder (inputs/operation differ). PASS.
- ov_balance_method: average of before/after (adds averaging) vs requested (drops payments input) vs unpaid. PASS.
- ov_period_anchor: days since first charge day vs days since last payment (different anchor inputs) vs whole period. PASS.
- ov_credit_application / py_credit_applied: subtract credits vs subtract the unpaid amount (conditional pick) vs nothing. PASS.

### Round 2 B2 probes (scratch copies; task 0 [change order, final draw]; task 1 [credit, charge, payment])
Task 0: voided later proposal -> unchanged; no preceding job -> 1792.33; water dried to standard -> 1995.28; class_1 -> 2140.28; built 1979 without sampling -> 2535.28 (asbestos tier); pre-1978 without setup line -> 2110.28; approval absent -> 1995.66; depreciation request 4,000 pending -> 14864.40; 1,000 forfeited -> 14628.00 (moves from depreciation to owner share); AOB arrangement -> 15108.00; mold job invoiced, balance 600 -> 16076.60; cancelled mold job on another claim -> unchanged; second pending proposal deductive -> P1 out of scope (base), P2 wait unaffected; walkthrough 37 days ago -> 21568.20.
Task 1: agreement expired/absent -> charge 92.45; later carrier_direct draw -> unchanged; same-date customer draw with lower number -> unchanged (tie by number); payment exactly one month back -> charge 114.08 (outside window); one day later -> 148.94 (inside); Louisiana -> 70.41 / 14302.83; not suspended -> payment 11783.08; resumed with no remobilization line -> 11783.08; construction not started -> credit 394.73 (plan-update tier); approval absent -> 220.56; water category_2 -> 295.53; zero-quantity deductive -> 0.00.

### Residual risks for the audit
- Company schedules: lead-safe cleaning verification fee 125.00 (RRP 40 CFR 745.85(b) step), minimum labor charge 2 hours, deductive processing deductions 95.00 / 45.00.
- P2 mitigation-first reads the claim file's mold job only (water jobs are one per loss and paid first in the seeded worlds); stated in the rule.
- THIN-CHARTER note: the rebuild charter offers few independent levers for overdue/payment amounts; py_remobilization and py_outside_lines carry tiers whose outcomes are numerically close by construction.
REWORK round 2: gates 7/7 green

## REWORK round 3 [factor names and figures partly superseded by REWORK round 4 below]
### Dispositions (audit revision_2: C-01, C-02, C-05, C-12, C-13, C-14, C-17, C-18, R2-01..R2-06; task items T0-R2-1/2, T1-R2-1..4)
- C-01 CLOSED: P3's replaced_by now restates the base deductive pricing with both branches (install/finish/labor at tier rate x quantity; flooring, cabinet and fixture upgrade lines at selected price less allowance x quantity), without markup.
- C-02 CLOSED: P5 declares an overwrite of base rebuild_overdue_draws' suspension/resumption sentence: for a draw paid by P5's payment the draw counts as paid in full once that payment posts (retention, applied credits and the claim-pending set-aside are not due), work then resumes and the remobilization fee the payment carries is booked once; every other draw keeps the base sentence. py_overdue_carried no longer gives a resumption reason.
- C-05 CLOSED: ov_balance_method tier 1 is now a day-weighted average balance over one fee period (inputs: the latest payment date and the days from it; operation: day weighting), not a re-windowed payment sum.
- C-12 CLOSED: py_outside_lines removed (its single-formula ladder is gone); replaced by py_claim_pending.
- C-13 CLOSED: ov_agreement_rate removed from P4; the account agreement left task 1's world and reads; replaced by ov_claim_pending. No account-charter figure is read any more, so the BLUEPRINT-KNOWN rounding/day-count gap for account figures no longer applies; P4/P5 now state their own day count ("calendar days from the earlier date to the later one, the earlier day not counted") and rounding.
- C-14 CLOSED: one retention model in P2/P4/P5: the owner holds back the Texas percentage from customer-funded draw payments; a Texas customer draw counts as paid in full once all but its retention is paid; P2 subtracts only the retention actually held back (the unpaid part of earlier customer draws, capped at the percentage of their requested amounts) and, on retainage tiers, the retainage already withheld. An on-time draw paid in full contributes nothing (the auditor's 1,000.00 demonstration now gives 0).
- C-17 CLOSED: claim_request_id is read only on insurance_scope change orders. P1's carrier-price tier is insurance_scope only (task 0's pending proposal is now insurance_scope; the code item is a separate signed code_required change order without a supplement id). P3 finds the supplement through the signed insurance_scope change order of the same scope code; task 1's deductive proposal carries no supplement id.
- C-18 CLOSED: P4's condition and P5's credit-edge sentence and condition all read "no deductive proposal awaiting signature".
- R2-01 CLOSED: see C-02 (resumption defined for P5's payment) and the closure text now says the payment makes the draw count as paid in full under the declared rule.
- R2-02 CLOSED: co_regulated_materials tier 1 samples any building older than the water job tier's asbestos cutoff that was not sampled, on the contract's first wall-finish change order (no re-fire); tier 2 is the RRP cleaning verification for sampled pre-1978 housing with a lead-safe setup line. Task 0's water job now carries its asbestos sampling line, as the water charter requires before flood cut.
- R2-03 CLOSED: fd_mitigation_first removed.
- R2-04 CLOSED: fd_depreciation_hold removed (depreciation is released on proof of completion and is requested with the final draw).
- R2-05 CLOSED: dc_overhead_return tiers are now disjoint by words and compute alike: carrier-priced scope (insurance_scope change order of the same scope code under an approved supplement) with enough trades -> arrangement O&P; scope added by an owner_upgrade change order and by no insurance_scope change order -> tier markup; otherwise 0.
- R2-06 CLOSED: dc_unopened_units labor tier credits the lesser of the hours removed and the added hours above the minimum labor charge, so a partial removal that leaves the minimum untouched is credited in full.
- T0-R2-1 CLOSED (C-17), T0-R2-2 CLOSED (R2-02/03/04: replacement factors fd_covered_code_hold, fd_uncovered_code_hold, fd_deductible_hold, fd_owner_item_hold, all grounded in the claims charter's ordinance-or-law limit, deductible collection and denied-line billing parameters).
- T1-R2-1 CLOSED (C-02/R2-01), T1-R2-2 CLOSED (C-17), T1-R2-3 CLOSED (C-14), T1-R2-4 CLOSED (replacement factors ov_claim_pending and py_claim_pending, grounded in the claim-pending suspension days the company's water, mold and contents charters carry; ADB balance method).

### Round 3 handling-time figures
- task 0: change order 2235.28 (baseline 1356.71); final draw 23014.46 (baseline 34820.22); skip signature -> 21002.71.
- task 1: credit 344.73 (baseline 286.00); charge 86.67 (baseline 209.21); payment 10056.92 (baseline 13947.53); skip signature -> 88.74 / 10401.65; skip charge -> 9970.25.
- All figures more than 1e-6 from a half cent (closest: 2157.34975).

### Round 3 A7 pairs (new or changed)
- ov_balance_method: day-weighted average (adds date input and weighting) vs requested (drops payments) vs unpaid. PASS.
- dc_unopened_units: floor to sheets vs min(hours, max(0, added - minimum)) vs written. PASS.
- fd_state_retainage: Texas % of sum less held-back retention / greater-of with retainage / tier % of remainder. PASS.

### Round 3 probes (scratch)
Task 0 [CO, final draw]: voided later proposal unchanged; no preceding job 1667.33; water job never sampled 2535.28 (asbestos tier); pending CO code_required 1995.66 / 20779.18 (no carrier price; code holds grow); O&L 0 -> unchanged total (uncovered = whole); O&L 5000 -> unchanged total (covered = whole); PA arrangement -> unchanged (deductible amount = due here); AOB -> 23494.46; carrier paid insured only -> 27746.20 (not carrier-funded, no holds); withdrawn second claim file unchanged; walkthrough 37 days ago -> 30088.48.
Task 1 [credit, charge, payment]: later carrier draw unchanged; payment exactly one month back 144.68 (outside), one day later 143.72 (inside); Louisiana 99.84 / 12251.67; not suspended -> 9731.92; approval 98 days ago -> 97.25 / 11819.72; supplement paid -> 97.25 / 11819.72; supplement 2 pending 640.00 -> 93.41 / 11179.72; water category_2 -> credit 295.53; zero-quantity deductive -> 0.00; no preceding water job -> 295.53 / 97.25 / 11819.72.

### Residual risks
- Company schedules still used: lead-safe cleaning verification fee 125.00, minimum labor charge 2 hours, deductive processing deductions 95.00 / 45.00.
- The claim-pending factors read the claim file's supplement approvals and payments at file level and the latest supplement request.
REWORK round 3: gates 7/7 green

## REWORK round 4 [co_lead_safe_work ladder superseded by REWORK round 5 below]
### Dispositions (audit revision_3: C-02, C-14, R2-06, R3-01..R3-05; task items T0-R3-1/2, T1-R3-1/2/3)
- C-02 CLOSED (declared): the Texas sentence in P4 and P5 now defines the statutory retention (Texas percentage of the draw's requested amount, the part above the tier retainage on a retainage tier); P4's charge overwrite restates the base charge for every other draw with the Texas carve stated (a Texas customer-funded draw's unpaid amount leaves out its retention, so a draw paid but for its retention carries no charge) and P5's suspension/resumption overwrite restates suspension and resumption with the same carve; gloss and restated base text now agree.
- C-14 CLOSED: P2 no longer measures retention held on customer-funded draws. P2, P4 and P5 state one practice: the owner holds its own retention back from its payments of customer-funded draws, and the final draw holds retention only on a carrier-funded final draw, on the share of the current sum the customer does not fund (current sum less earlier customer-funded draws counted before retainage). No unpaid-amount measure remains.
- R2-06 CLOSED: dc_unopened_units labor tier takes the removed hours first from the signed additive change orders of that scope (credited above the minimum labor charge hours) and credits any hours beyond them (the contract's own labor) in full; probe: contracted labor removal with no labor change order credits every hour.
- R3-01 CLOSED: the claim-pending set-off/set-aside and the water parameter are gone (no water read in P4/P5). Replaced by ov_carrier_pending / py_carrier_pending, grounded on the base overdue sentence that carrier-funded draws carry no charge while their funds are pending and on the claims charter's release practice (recoverable depreciation released only once the work is shown complete): withheld dwelling depreciation less releases less forfeiture write-offs, plus unpaid supplement approvals, while the contract is not substantially complete; otherwise unpaid supplement approvals; otherwise nothing. Single reading; no window parameter.
- R3-02 CLOSED: one family factor fd_code_item_hold (owner's share above the ordinance or law limit; whole total with no coverage; nothing when the coverage pays it, the work being complete at the final draw); the limit now changes the draw. Count restored with fd_depreciation_hold (recoverable depreciation the carrier still withholds until proof of completion per rebuild_completion and claims_evt_depreciation_release; owner-item hold now carries carrier_denied_line write-offs only, so forfeiture is counted once). Both pass T1 on task 0 and T2.
- R3-03 CLOSED: carrier-funded = the base draw rule's funding route is not the customer: a dwelling payment routed contractor_direct, insured_two_party or mortgagee_loss_draft; the pass-through tier keys on the same test (self_pay tier unchanged), so holds and pass-through use one definition.
- R3-04 CLOSED: co_regulated_materials replaced by co_lead_safe_work: no asbestos condition and no first-opening test; on pre-cutoff housing a lead-safe setup standing on the contract (setup line or earlier signed drywall/paint/baseboard change order) gives the RRP cleaning verification fee; none standing gives the tier's setup fee plus verification; otherwise nothing.
- R3-05 CLOSED: (a) the water job field and its ledger already agreed; the disputed total came from a stale seed-consistency note, now corrected; the water charge rows left the seed because no factor reads them. Sweep also found the task-0 depreciation window had lapsed with no forfeiture booked, so the initial approval, ACV receipt, first draw and its posting dates moved (window open, route carrier_direct only after the payment reached the company). (b) task 1 now carries the initial dwelling approval with withheld depreciation, the insured_only ACV payment and the insured_only supplement payment; carrier receivable recomputed.
- T0-R3-1 CLOSED (via R3-02, R3-04; P2 6 factors, 1 method). T0-R3-2 CLOSED (via R3-05a). T1-R3-1 CLOSED (via R3-01). T1-R3-2 CLOSED (via R3-05b). T1-R3-3 CLOSED (P3 method valid after R2-06; P4 parameters ov_owner_retention and ov_carrier_pending).

### Round 4 factor bounds
| policy | factors | parameter | method |
|---|---|---|---|
| P1 | co_billing_unit, co_price_basis, co_overhead_profit, co_wall_treatment, co_drying_verification, co_lead_safe_work | 5 | 1 |
| P2 | fd_state_retainage, fd_code_item_hold, fd_deductible_hold, fd_owner_item_hold, fd_depreciation_hold, fd_pass_through | 5 | 1 |
| P3 | dc_unopened_units, dc_carrier_price, dc_overhead_return, dc_treatment_return, dc_processing_deduction | 4 | 1 |
| P4 | ov_balance_method, ov_credit_application, ov_owner_retention, ov_carrier_pending, ov_period_anchor | 2 | 3 |
| P5 | py_overdue_carried, py_credit_applied, py_owner_retention, py_remobilization, py_carrier_pending | 4 | 1 |

### Round 4 A1 factor-reads (changed factors; plain shared bindings in brackets)
co_lead_safe_work{ls_*}; fd_state_retainage{rt_*}[current_sum, earlier_requested, earlier_before_retainage, remainder, carrier_funded]; fd_code_item_hold{ch_*}[carrier_funded]; fd_owner_item_hold{oi_*}[carrier_funded]; fd_depreciation_hold{dp_*}[carrier_funded]; fd_pass_through{pt_*}[carrier_funded]; dc_unopened_units{uq_*}; ov_carrier_pending{pc_*}; py_carrier_pending{sa_*}. No factor reads another factor's binding.

### Round 4 A7 pairs (changed)
- fd_state_retainage: Texas percentage of (current sum less customer-funded draws) vs greater-of with non-customer retainage (adds max) vs tier percentage of the remainder (all earlier draws). PASS.
- dc_unopened_units: floor to sheets vs capped pick plus excess hours vs written. PASS.

### Round 4 checks on the final state
- compute_basis verbatim sweep, baseline/replaced_by/policy_source containment: clean.
- Every scored, baseline and sensitivity figure more than 1e-6 from a half cent (raw-value scan).
- Probes (scratch copies), task 0: decoy voided proposal, absent preceding job, no setup line (setup tier), setup via earlier painted change order, post-1978 building, mortgagee loss-draft route (still carrier-funded), depreciation release recorded, forfeiture on billable and non-billable arrangements, earlier customer-funded draw (Texas share shrinks), limit none/zero/above total, non-carrier-funded world, second withdrawn claim file, walkthrough beyond the retention days — each moves only the factor it should.
- Probes, task 1: decoy later draw, past-month boundary both sides, Louisiana, not suspended, supplement unpaid, contract complete (tier 2), complete with supplement unpaid, depreciation fully released, decoy contents approval, no linked claim file, contracted labor removal, category_2 job, zero quantity, no preceding job — each as the rule reads.
- Proof text swept: traces, seed-consistency notes, rationales and step references rewritten to the final state.
- check_traceability still deferred (KB not rendered).

### Residual risks
- Company schedules still used: lead-safe cleaning verification fee, minimum labor charge hours, deductive processing deductions.
- Carrier-money tier counts the claim file's depreciation and supplements at file level (one dwelling coverage part per file).
REWORK round 4: gates 7/7 green

## REWORK round 5 [co_lead_safe_work effect label superseded by REWORK round 6 below]
### Dispositions (audit revision_4: C-02 remaining member)
- C-02 CLOSED: co_lead_safe_work no longer bills a lead-safe setup inside a change order and no longer treats a signed painted-surface change order as a standing setup. The ladder now applies only on a contract that already carries the base per-contract lead_safe_setup line, and splits by the EPA RRP minor-repair rule (R4): a drywall or baseboard line removes painted components (never minor repair) and carries the cleaning verification fee; a paint line carries it only when the quantity written exceeds the RRP interior minor-repair area (6 sq ft, stated as a constant with its source); any line on a contract with no setup line, and every other line, carries nothing. The factor is now a method (flat item vs conditional pick on the quantity vs nothing); A7 pairs pass, A1 reads only ls_* bindings, T1 holds on task 0 (same tier as before), T2 holds.
- C-02 class sweep: checked every extended rule against the in-force base fees clauses (status window for permit/professional fee postings, per-contract lead-safe setup line, once-per-type expediting, plan drawing once per contract). No extended rule now posts or prices a base fee line: P1's drying verification and wall treatment are water-tier items priced inside the change order under the declared pricing overwrite; P2's pass-through only reads fee lines already booked; P5's remobilization is the base fee booked on resumption. No other member found.

### Round 5 checks on the final state
- compute_basis verbatim sweep and baseline/replaced_by/policy_source containment: clean.
- Raw-value scan: every scored, baseline and sensitivity figure more than 1e-6 from a half cent.
- Probes (scratch copies), task 0: no setup line (no lead-safe item and nothing billed for setup), paint line above and at the minor-repair area, baseboard removal, commercial property, post-1978 building, decoy voided proposal, absent preceding job, and the round-4 final-draw probes — each as the rule reads. Task 1 untouched by this change; its figures re-verified unchanged.
- Proof text swept: task 0 argument tracing, factor trace and tier_taken, read necessity and rationale rewritten for the new ladder; no stale "setup stands" or setup-in-change-order wording remains in the policies or task files.
REWORK round 5: gates 7/7 green

## REWORK round 6 [ov_charge_days ladder and P2/P4 assembly wording superseded by REWORK round 7 below]
### Dispositions (audit revision_5: C-05, R5-01; task items of 0.md / 1.md)
- C-05 CLOSED: co_lead_safe_work selects a fee value, so it is labelled `parameter` again with value tiers (fee for a painted-component removal; fee or nothing by the RRP minor-repair area for a paint line; nothing); rule text and computation unchanged; P1 keeps co_billing_unit as its method. Class sweep: every remaining method factor (co_billing_unit, fd_state_retainage, dc_unopened_units, ov_credit_application, py_credit_applied) re-checked pair by pair — each pair differs by an input or an operation; no constant-vs-constant method pair remains.
- R5-01 CLOSED: P4's timing now has exactly one convention per date dimension, combined once in a plain assembly sentence. ov_charge_days (due date) owns the chargeable days of the fee period (days since due less grace when fewer than the fee period days; none within grace; otherwise the whole period). ov_current_days (latest payment date) owns the days at the current balance (days from the latest payment within the past month; none for a payment on the charge date, which counts from the next day; otherwise the whole period). The balance the charge is figured on counts the chargeable days beyond the current-balance days at the balance before the month's payments and the rest at the unpaid amount now, over the fee period days; the separate period-share step is gone, so the pre-payment days are counted once and consistently. ov_balance_method and ov_period_anchor are replaced by these two factors; P4 keeps its drawn count with no added lever; each new factor reads only its own bindings (A1), both pass T1 on task 1 and T2.
- R5-01 class sweep: the old "requested amount for the first fee period" tier was a second convention on the due date; it is absorbed by ov_charge_days with the general balance-days assembly. No other policy carries two timing conventions on one date (P2 one completion-date method; P3, P5 key on statuses and their own single dates).
- Task 0 item (C-05 member on its scored amount) CLOSED via C-05. Task 1 item (R5-01 engaged) CLOSED via R5-01.

### Round 6 checks on the final state
- compute_basis verbatim sweep and baseline/replaced_by/policy_source containment: clean.
- Raw-value scan: every scored, baseline and sensitivity figure more than 1e-6 from a half cent.
- Probes (scratch copies), task 1: payment exactly one month back and one day inside it now agree (both precede the first charge day), payment on the charge date, draw within grace, whole-period draw, no partial payment, plus the round-4/5 probes — each as the rule reads. Task 0 probes unchanged in outcome.
- Proof text swept: task 1 argument tracing, factor trace and tier_taken, read necessity, prerequisite skipped-effect sentences, gold-action business effects and rationale rewritten; task 0 factor trace and rationale relabelled; no stale period-share or balance-method wording remains in the policies or task files.
REWORK round 6: gates 7/7 green

## REWORK round 7 [ov_charge_days tier wording superseded by REWORK round 8 below]
### Dispositions (audit revision_6: C-05, R6-01; task 1 item)
- C-05 CLOSED: ov_charge_days' within-grace tier is unreachable under base od_grace (a charge never posts inside the grace period) and is removed. Its live third tier is now the real carry-over case on the same convention: when an overdue draw charge was already posted on the draw fewer than the fee period days before the charge date, the chargeable days run from that latest charge (no day is charged twice); otherwise the days since the due date less the grace days when fewer than the fee period days; otherwise the whole fee period. All three tiers are reachable (a charge posted late in one month followed by the next month's charge early in the following month takes the first tier).
- C-05 class sweep (every factor, parameter and method, against the in-force base gates): P1 co_billing_unit, co_price_basis, co_overhead_profit (fewer-trades tier reached on Carrier Program files), co_wall_treatment (fire and mold preceding jobs), co_drying_verification, co_lead_safe_work; P2 fd_state_retainage (retainage tiers reached on Full Structural and Commercial contracts), fd_code_item_hold, fd_deductible_hold (non-collecting arrangements reach a carrier-funded draw via two-party or mortgagee routing), fd_owner_item_hold, fd_depreciation_hold, fd_pass_through (self_pay); P3 all five (processing deduction's fall-through reached by a no-permit determination); P4 ov_current_days (payment on the charge date), ov_credit_application, ov_owner_retention, ov_carrier_pending (contract complete); P5 all five (remobilization's resumed tier reached when an earlier draw was paid and work resumed while a later draw is past due). No other unreachable tier found.
- R6-01 CLOSED: (a) P4 — the shared quantities the assembly names (the chargeable days of the fee period, the days at the current balance) are now defined once in the baseline and rule ("each the fee period days unless a rule below sets them otherwise"); the factors only set them otherwise. (b) P2 — the assembly no longer names a factor quantity: "then every amount the final draw also bills is added". Sweep of all five assembly sentences: P1, P3, P5 already generic or baseline-defined; P2 and P4 fixed.
- Task 1 item (C-05 member on ov_charge_days) CLOSED via C-05. Task 0 cited R6-01(b) CLOSED via R6-01.

### Round 7 checks on the final state
- compute_basis verbatim sweep and baseline/replaced_by/policy_source containment: clean.
- Raw-value scan: every scored, baseline and sensitivity figure more than 1e-6 from a half cent; no scored figure moved this round.
- Probes (scratch copies), task 1: earlier charge on the draw inside and outside the fee period, payment on the charge date, whole-period draw, plus the earlier probe table — each as the rule reads.
- Proof text swept: task 1 argument tracing, factor trace, tier_taken and rationale updated for the new ladder wording; no stale within-grace or pass-through-assembly wording remains in the policies or task files.
REWORK round 7: gates 7/7 green

## REWORK round 8 [P4 timing, carve-out wording and carrier-money set-off superseded by REWORK round 9 below]
### Dispositions (audit revision_7: R7-01)
- R7-01 CLOSED: verified on scratch worlds (two and three owed months uncharged at the opening): the round-7 carry-over tier priced every owed month after the first, posted the same day, at nothing. ov_charge_days' first tier now applies only to a charge already posted on an earlier day within the fee period; a charge for a later owed month posted the same day as the earlier one takes the whole fee period, so each owed month is charged on its own days and no day count resets to nothing. The second tier now requires that no charge has been posted on the draw at all.
- R7-01 remaining zero case (an earlier charge a few days back with set-offs covering the balance, and any world where the amounts set against the balance cover it): carved out with one test stated verbatim in P4's rule and in P5's waiting prerequisite sentence and condition — a fee period owes no overdue draw charge, and no charge is recorded for it, when the amounts set against the balance the charge is figured on are at least that balance. No floor creates an amount; P5's wait clears without a zero row.
- E6/E7 class sweep (every edge's resolver must write a positive, schema-legal row in every engaged world): P2 <- P1: a proposal working out below the change order minimum "is not written" under P1, which left P2's wait unsatisfiable — P2's prerequisite sentence and condition now leave such a proposal out ("is not counted, because it cannot be written"). P4 <- P3 and P5 <- P3: a deductive credit that works out to nothing would have needed a zero change order and credit row — P3 now states such a change order is not written, and P4's and P5's prerequisite sentences and conditions leave it out in the same words. P5 <- P4 handled above. No other member.
- Task 0 and task 1 worlds: every waited-on proposal and owed month works out to a positive amount; prerequisite closure text (policy sources, conditions, why-false evidence) and rationales updated to the new sentences.

### Round 8 checks on the final state
- compute_basis verbatim sweep and baseline/replaced_by/policy_source containment: clean.
- Raw-value scan: every scored, baseline and sensitivity figure more than 1e-6 from a half cent; no scored figure moved.
- Probes (scratch copies): two and three owed months uncharged (each positive and on its own days), a payment inside the period with a three-month backlog, a late-posted prior charge, an earlier charge with set-offs covering the balance (the carved no-charge case), a below-minimum additive proposal, a deductive proposal whose credit works out to nothing, plus the earlier probe tables.
REWORK round 8: gates 7/7 green

## REWORK round 9 [P1 billing unit and treatment basis, P4 window wording superseded by REWORK round 10 below]
### Dispositions (renderer render_r1: blocking 1-9, lesser L1-L6)
- 1 CLOSED: carrier-approved supplement amounts are billed as approved. P1 defines a carrier-scope line once (plain) and the assembly bills it at the quantity written, so whole-sheet and minimum-hour billing never multiply the carrier's per-unit price; the billing unit still applies to company-priced lines and to the wall-closing treatment (the area the sheets close). P3's carrier price is the approved amount over that change order's written quantity (no rounding on top); its sheet floor only lowers a credit.
- 2 CLOSED: P4's two timing factors are merged into one method factor (ov_balance_days) owning the charge span (fee-period start, first charge day, day after an earlier-day charge) and the payment weighting; the due date, earlier charges and the month's payments are its own bindings; the baseline defines only "the balance the charge is figured on is the draw's unpaid amount" (no exception hint). P4's drawn count is kept by splitting the carrier-money set-off into two real claims-charter levers: recoverable depreciation (released only on completion; an outstanding release request after completion) and supplement money (unpaid approvals; a request without a carrier decision). Task 1 seeds a second supplement request awaiting decision so both bear weight.
- 3 CLOSED: P3's baseline and fall-through tier now state the written-price fallback for scope codes with no tier rate, matching the compute.
- 4 CLOSED: P3's carrier price and overhead-and-profit return read one referent, the signed insurance_scope change order of that scope created last (its supplement's approved amount over its own written quantity).
- 5 CLOSED: P1's owner-upgrade price tier is stated for flooring, cabinet and fixture upgrade lines only, as the compute and ladder apply it.
- 6 CLOSED: P2's overwrites now restate that the tier's retainage is requested once the tier's retainage release days have passed after substantial completion, other held amounts once released.
- 7 CLOSED: Texas retention in P4 and P5 (set-off, holdback, paid-in-full and suspension carve-outs) applies only until the Texas statutory retention days after substantial completion have passed, as P2 already did.
- 8 CLOSED: a past-due payment that works out to less than half a cent is not taken and the draw counts as paid in full at once (stated in P5's rule and its resumption overwrite); no zero payment row.
- 9 CLOSED: P5 carries only overdue charges posted on the paid draw (a draw is brought current by one such payment), and carries a booked remobilization line only when no draw payment was posted between the suspension and the resumption; P2's self-pay pass-through excludes overdue and remobilization lines.
- L1 CLOSED: the no-charge carve-out (P4 rule, P5 waiting sentence and condition) is now the record-computed test "the charge worked out comes to less than half a cent", which also covers set-offs covering the balance. L2 CLOSED: P1's overwrite restores markup and rounding for every change order outside its scope, deductive ones included. L3 CLOSED: the depreciation hold states "never below zero". L4 CLOSED: the two current-days tiers are gone with the merge. L5: renderer-side split, no source change. L6: nothing to log.
- Class sweeps: zero-amount rows — P2's final draw that works out to less than half a cent is not requested (held amounts go to the retainage_release draw); P1 below-minimum and P3 nothing-credit carve-outs kept. Double collection — no other payment or draw re-bills a line. Single referent — P1 reads the one pending proposal; P2/P4/P5 claim reads are file-level aggregates or the latest dated record. Inputs used by one factor — P4 due date moved into its factor; no other plain binding is read by one factor only. History load-bearing restored in P3 by the existence count of signed insurance_scope change orders of the removed scope.

### Round 9 checks on the final state
- compute_basis verbatim sweep and baseline/replaced_by/policy_source containment: clean.
- Raw-value scan: every scored, baseline and sensitivity figure more than 1e-6 from a half cent.
- Probes (scratch copies): carrier-scope drywall and labor lines with tiny written quantities, absent supplement approval, the round-5..8 task 0 table; task 1 table plus completion, release and supplement variants, earlier charges, multi-month backlogs and a payment inside the period — each as the rules read; the only zero charges fall in the carved no-charge case.
- Proof text swept: both tasks' argument tracing, factor traces, tier_taken, read necessity, prerequisite closure effects and rationales rewritten for the moved figures and new factors.
REWORK round 9: gates 7/7 green

## REWORK round 10 [co_post_completion_items and P3 quantities superseded by REWORK round 11 below]
### Dispositions (audit revision_9: R9-01, R9-02, R9-03)
- R9-01 CLOSED: the wall-closing treatment is charged on the quantity written on the proposal, the wall area the line closes, never on whole-sheet purchase units; the assembly says "any treatment charged on the quantity written on the proposal". With no rounding left, co_billing_unit could no longer bear weight on a carrier-scope line, so it is replaced by co_post_completion_items, built from the tier's own dumpster and final cleaning fees: a change order signed on or after substantial completion carries a new dumpster placement plus re-cleaning for a drywall or insulation line, re-cleaning for any other line (dumpster and final_cleaning lines excepted), and nothing before completion. co_price_basis is now P1's method (carrier tier divides the approved amount by the written quantity; owner tier subtracts the allowance; otherwise the tier rate). P1 keeps its drawn count.
- R9-01 class sweep: P3's returned treatment is on the quantity written; no other area-priced item uses a purchase unit.
- R9-02 CLOSED: "fee period" now means only the calendar month the base defines (owed months, YYYY-MM labels, the waiting sentence). The rolling span P4 figures a charge on is named the charge window (the charge window days ending on the charge date, parameter charge_window_days), stated once, and the fee-period sentence says every owed month's charge is figured on the charge window ending on the charge date. Rule and compute agree on the span start in every case.
- R9-02 class sweep: no other policy term carries two meanings ("past month", "charge span", "billed quantity", "remainder" each defined once).
- R9-03 CLOSED: dc_carrier_price's fall-through tier now carries the written-price fallback. Full A8 sweep of all 26 ladders against rule and compute: also fixed co_post_completion_items' boundary (on or after the completion date, as compute reads it), fd_depreciation_hold's "never below zero" in both value tiers, and dc_carrier_price's upgrade tier wording ("otherwise, a flooring, cabinet or fixture upgrade line"). Every other tier's condition, boundary and value matches.
- Edge found while probing: P2's Texas retention day count now treats a missing substantial completion date as outside the statutory days (the rule's "no later than ... after the substantial completion date" cannot hold without one), so the computation no longer errors.
- Task 1 untouched in substance: its policies' computations are unchanged; only the renamed window term in its argument tracing was updated.

### Round 10 checks on the final state
- compute_basis verbatim sweep and baseline/replaced_by/policy_source containment: clean.
- Raw-value scan: every scored, baseline and sensitivity figure more than 1e-6 from a half cent.
- Probes (scratch copies), task 0: no completion yet, completion on the signing date, paint line after completion, below-minimum proposal before completion, tiny carrier-scope quantities, absent supplement approval, plus the earlier table — each as the rules read. Task 1 figures re-verified unchanged.
- Proof text swept: task 0 argument tracing, factor traces, tier_taken, prerequisite closure effects and rationale rewritten for the moved figures and the new factor.
REWORK round 10: gates 7/7 green

## REWORK round 11 [P1 carrier-scope bindings, P3 carrier price and supplement request reads superseded by REWORK round 12 below]
### Dispositions (audit revision_10: R10-01, R10-02, R10-03)
- R10-03 CLOSED: co_post_completion_items is dropped. The candidates RULE-7 lists do not engage task 0's change order honestly (project_management_fee_pct is 0 on every tier but Commercial, and a commercial property would void the RRP factor; an engineering letter is a separate per-letter fee line for altered framing, not part of a drywall change order; material_escalation_threshold_pct governs escalation lines only). P1's sixth factor is therefore co_framing_cleaning, a real base-catalogue lever: before a drywall or insulation line closes walls, the framing is cleaned at the preceding mitigation job tier's rate (water category_3: HEPA vacuuming; fire: wet cleaning; mold: HEPA vacuuming), on the quantity written — the clean-then-coat sequence of IICRC S500/S520, priced from the water, fire and mold catalogues. It restates no base clause and P2 bills the signed change order's amount as it bills every other. Passes T1 (task 0) and T2; reads only its own bindings (A1).
- R10-01 CLOSED: P3 mirrors P1 exactly. The removed line is credited on the quantity written (P1 bills by the quantity written; the sheet floor and the minimum-labor-hour premise are gone with dc_unopened_units); the carrier price, treatment and the new framing cleaning are returned as P1 charges them; the overhead and profit returned mirrors the markup P1 charged on the addition (overhead and profit for an insurance_scope or code_required addition on an insurance_claim contract meeting the trade minimum; the tier markup for any other additive change order; nothing for contract-sum scope). P3's method is dc_carrier_price (carrier division / allowance subtraction / tier rate); dc_cleaning_return keeps its drawn count. Probe: an additive 3 h labor change order followed by a deductive 3 h credits all 3 hours.
- R10-02 CLOSED: every seeded rebuild row re-priced under the rules in force (one exhaustive pass). Re-priced: task 0 change order dd640de1-6836-4463-8404-5013ffce26cc and its charge line 65c70b09-fe6d-461b-bb85-5dee2dd1dd08; task 0 change order 9392d687-7ad4-412f-82f1-00c5a42cba8d and its charge line c8131833-be98-41c4-a2b2-50446cee3e5e (selected unit price re-seeded so no scored or sensitivity figure lands on a half cent; priced by the same rule); task 0 contract d1c30798-f0fd-4de5-81fd-c9a6b3bbaf87 (balance); task 1 change order e5bf8c39-3b14-4085-964a-72d8e0bcb51e and its charge line 0ebe59b4-0bc5-41cc-9efa-215ddefe745d; task 1 draw 181a26f1-1e8b-4d7d-b2a5-65e8ea84d683; task 1 contract 3539ec0f-e9d7-46ba-aa58-b564e176cf50 (balance). Checked and unchanged: every other change order, charge line, draw and payment of both tasks (contract_signing draws capped at the deposit maximum, task 0 drywall draw requested before both signed change orders, insurance postings, ACH payments, task 1 flooring upgrade, both pending proposals' drafted figures).
- Class sweeps: sibling pricing — P1 and P3 now price quantity, unit price, treatment, cleaning and markup alike; fixed per-change-order items (drying verification, lead-safe verification) are not returned on a removal, as the removal does not undo a completed verification. Seed pricing — seed notes for both tasks restate the current derivations.

### Round 11 checks on the final state
- compute_basis verbatim sweep and baseline/replaced_by/policy_source containment: clean.
- Ladder-text sweep (A8) on the final state: every tier of the changed factors (co_framing_cleaning, co_price_basis, dc_carrier_price, dc_overhead_return, dc_cleaning_return) and the untouched ones matches its rule sentence and compute.
- Raw-value scan: every scored, baseline and sensitivity figure more than 1e-6 from a half cent.
- Probes (scratch copies): task 0 table; task 1 table plus labor-after-labor mirror, category_2 water job, completion, release and supplement variants, earlier charges, multi-month backlogs — each as the rules read.
- Proof text swept: both tasks' argument tracing, factor traces, tier_taken, read necessity, prerequisite closure, gold-action effects, seed notes and rationales rewritten for the re-priced rows and moved figures.
REWORK round 11: gates 7/7 green

## REWORK round 12 [P3 return quantities superseded by REWORK round 13 below]
### Dispositions (renderer render_r2: blocking item and three recipe classes)
- Blocking (XF A3, P1 carrier-scope bindings) CLOSED: the plain cl_kind, cl_supplement, cl_approved and carrier_line duplicated co_price_basis's own up_* bindings and were read only by it; they are removed and the carrier-scope test is computed inside co_price_basis from up_kind, up_supplement and up_approved. The shared read sentence now lists only what the computation document uses (scope code, quantity written, unit price written); the change order type and the supplement the proposal names are stated in the price factor's own sentence, which now carries the carrier-scope definition. No scored figure moves.
- B3 same-day ties CLOSED (class): the supplement request lookups in P4 and P5 now take the request with the highest supplement number (supplements are numbered in sequence on the file, so no tie exists); the depreciation release request lookups take the latest request date and, of two on that date, the larger requested amount (rule and compute alike); P3's carrier-price referent is the signed insurance_scope change order of the scope with the highest change order number instead of "created last". Sweep: every other latest-record lookup is either unique by scope (P1 and P3 read the one proposal awaiting signature; P4 and P5 the customer draw with the highest draw number) or a date-only read where a same-day tie does not change the value.
- Supplement set-aside out of order CLOSED (verified the finding): P4 and P5 now set off the highest-numbered dwelling supplement request only when no supplement approval names it, and state a referral to a human representative when an earlier request is still undecided while a later one has been decided (B7 accepted route); the request-count comparison is gone, so rule and compute pick the request that is actually undecided or refer.
- Deductive credit over the carrier-scope quantity CLOSED (verified the finding): dc_carrier_price now decides the removed line — the carrier's approved unit price applies only up to the quantity the signed insurance_scope change orders of that scope added, and any removed quantity beyond that is credited at the tier's rate (or the written price where the scope has no tier rate), mirroring P1, which prices only a carrier-scope line's own quantity at the carrier price.
- Scored figures: none moved; task 1's removal lies within the carrier-scope quantity and its undecided request is the highest-numbered one; task 0 is untouched by these reads.

### Round 12 checks on the final state
- compute_basis verbatim sweep and baseline/replaced_by/policy_source containment: clean.
- Ladder-text sweep (A8): the changed ladders (co_price_basis, dc_carrier_price, ov_depreciation_pending, ov_supplement_pending, py_carrier_pending) match their rule sentences and compute.
- Raw-value scan: every scored, baseline and sensitivity figure more than 1e-6 from a half cent.
- Probes (scratch copies): a removal larger than the carrier-scope quantity, approvals out of order (referral residue; no supplement money set off), two release requests on one date after completion, plus both earlier probe tables — each as the rules read; no errors.
- Proof text swept: task 0's plain trace line and task 1's argument tracing, factor trace and tier_taken updated for the new referents and wording.
REWORK round 12: gates 7/7 green

## REWORK round 13
### Dispositions (audit revision_12: R12-01)
- R12-01 CLOSED (verified the finding): P3 now splits every removal into the change-order part (as much of the quantity written as the signed change orders of that scope code other than deductive ones added, less what signed deductive change orders of that scope already removed) and the contract part (the rest, off the contract's own scope). The removed line, the treatment return, the framing-cleaning return and the overhead-and-profit return apply only to the change-order part; the contract part is credited at the credit unit price (tier rate, or the written price where the scope has no tier rate) and added after the markup step with nothing returned on it. The baseline states both parts and still credits the whole quantity at the credit unit price.
- Class sweep (every P3 return): removed line, treatment, cleaning and overhead and profit all run on the change-order part; the processing deduction is a per-removal fixed item and is unaffected; no other policy prices a sibling's quantity. P1 needs no change (it charges every item on the change order's own written quantity).
- Scored figures: none moved; task 1's whole removal is change-order part.

### Round 13 checks on the final state
- compute_basis verbatim sweep and baseline/replaced_by/policy_source containment: clean.
- Ladder-text sweep (A8): dc_carrier_price's three tiers now speak of the change-order part, matching rule and compute; the other P3 ladders decide rates and are unchanged.
- Raw-value scan: every scored, baseline and sensitivity figure more than 1e-6 from a half cent.
- Probes (scratch copies): a removal larger than the change-order quantity (excess credited at the tier rate with no returns), contracted labor removal with no labor change order (credited at the tier rate, no returns), labor removed after an additive labor change order, plus the earlier probe tables — each as the rules read.
- Proof text swept: task 1's argument tracing, factor trace and rationale now state the two parts of the removal.
REWORK round 13: gates 7/7 green

## REWORK round 14
### Dispositions (KB audit revision_1: SRC-1, SRC-2, SRC-3, KB-B1)
- SRC-2 CLOSED (XF A9): P2's Texas retainage-tier sentence and fd_state_retainage's tier 2 now read "the greater of two amounts: that amount after the retainage withheld from the earlier draws that are not customer-funded is subtracted from it, or the tier's retainage percentage of the remainder" — the one reading compute uses (greater of the reduced amount and the tier percentage).
- SRC-2 class sweep (all five policies, every "greater/lesser of" and every "less ... plus/and" sentence): P5's carrier-money sentence and ladder now state the depreciation difference is floored at zero before the supplement money is added; P3's change-order-part sentence now states the deductive quantity is taken off what was added before the cap at the quantity written. The remaining instances are single-grouping or restate base text verbatim (left-to-right sums, "selected unit price less the allowance, times the quantity").
- SRC-1 not changed: coordinator ruling (realism_bar RULE-2) — the deductible assessment row is read by no gold step and is accepted residue.
- SRC-3 not changed: coordinator ruling — BLUEPRINT-KNOWN (P5 restates the base resumption/remobilization booking that no tool here writes; no task world engages it).
- KB-B1: render-side, no source change.
- Scored figures: none moved (text-only edits); compute unchanged.

### Round 14 checks on the final state
- compute_basis verbatim sweep and baseline/replaced_by/policy_source containment: clean; raw-value scan clean; task figures re-verified unchanged.
REWORK round 14: gates 7/7 green

## REWORK round 15
### Dispositions (audit revision_14: R14-01)
- R14-01 CLOSED (XF A9, ladder text): dc_carrier_price's upgrade tier now reads "the change-order part times the difference between the owner's selected unit price written and the tier's selection allowance for that line", the one reading rule and compute use.
- Class sweep of every ladder tier text (when, value, method) in all five policies for two-grouping arithmetic: also reworded dc_carrier_price's carrier tier (the change-order part up to the carrier-scope quantity times the carrier unit price, plus the rest times the tier rate) and fd_state_retainage's first tier (the Texas percentage of the difference between the current contract sum and the earlier customer-funded draws). Every other tier text is a single sum or difference, a left-to-right chain, or a product whose grouping does not change its value. Task 0's rationale card for the final draw restated the same way.
- Scored figures: none moved; compute unchanged.

### Round 15 checks on the final state
- compute_basis verbatim sweep and containment checks clean; raw-value scan clean; task figures re-verified unchanged.
REWORK round 15: gates 7/7 green

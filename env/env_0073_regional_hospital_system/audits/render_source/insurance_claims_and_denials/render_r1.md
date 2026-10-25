# Renderer findings — product claim (difficulty insurance_claims_and_denials), render round 1
Saved verbatim by the coordinator from renderer agent a23da2919b70fc37a (2026-10-21). Scan-first STOP; no document written. Gate read: `VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN`.
Source: tasks/insurance_claims_and_denials/claim.extended.yaml (8 extended policies, 45 factors, 8 tools).

Checked clean: compute_basis quotes verbatim; baseline rules and replaced_by in their rules; sibling overwrites name each other; refunded-remittance tie rule matches the tool body; MONTHS() matches policy 8's month-count wording; the "no uninsured discount" claim for the Outpatient Surgery Account in policy 3 matches encounter.yaml.

## 1. `claim_ext_retrospective_denial_refund`, factor `ecg_tracings_counted`: the rule caps per line, the compute caps the total
- Rule: "its billed units but no more than ecg_cap_per_line per line on a Commercial PPO claim".
- Compute: `MN(XSUM(... '0730', '93005' units), K('ecg_cap_per_line') * XCOUNT(... '0730', '93005'))`.
- Example: two lines with 5 and 1 units and a cap of 3 give 4 by the rule and 6 by the compute.
- Related: `ecg_value: ecg_counted * (ecg_charges / ecg_units * pct if ecg_units > 0 else 0)` has no cap at billed charges, although the rule says "replacements are made first, each never above the billed charges of the lines it values". A line billed with 0 units on an HMO claim can push the value above charges.

## 2. Same policy: two factors depend on each other (CT angiography rate and contrast handling)
- Compute: `ct_value: MN(cta_charges + (contrast_charges if contrast_method == 1 else 0), cta_units * cta_rate)`. The cap on `ct_angiography_code_rate` depends on the `contrast_handling` tier.
- CT rule words: "never above its charges together with the charges of any contrast that rate packages".
- Contrast rule words: "is packaged into the CT angiography's per-code rate, and carries no value of its own, on a Commercial PPO claim that bills the CT angiography (71275), the only scan priced at a per-code rate covering the contrast".
- Each factor document would have to describe the other. The plain `ct_value` would also put per-code-rate and packaging wording into the computation document.

## 3. `claim_ext_surgery_post_payment_refund`: the rule defines the pre-operative tests more narrowly than the compute
- Rule: "except the pre-operative tests ...: the laboratory tests (revenue code 0300), the electrocardiogram tracing (code 93005 under revenue code 0730) and the chest radiograph (code 71046 under revenue code 0324)".
- The same rule later reads "every other charge under revenue codes 0300, 0730 and 0324 by its charges", and the compute (`other_retained`) keeps every 0730 and 0324 charge.
- So any other code billed under 0730 or 0324 is refunded by the first sentence but retained by the compute.

## 4. All 8 policies: quantities read in the plain baseline that only one factor uses (recipe A.4)
- P1: `units_85025`, `units_80048`, `units_85610` used only by `sched_*` (factor `lab_schedule_method`); `typing_units` used only in the HMO branch of `blood_bank_typing_handling`. Baseline text: "each by its charges and billed units"; "together by charges and billed units".
- P2: `units_A4570` used only by `splint_pricing`.
- P3: `units_E0218` and `lines_E0218` used only by `cold_therapy_unit_valuation`; cold-pack and garment units only by their share factors. Baseline text: "the cold-therapy unit by its charges, billed units and number of lines, the cold pack and the support garment by their charges and billed units".
- P4: `r29882_units`, `r29877_units`, `r29877_charges` and the C1713/C1762 units and charges used only by `surgical_pricing_method` and `implant_pricing_method`. Baseline text: "read in total and by codes 29882 and 29877 with their billed units ... in total and by codes C1713 and C1762 with their billed units".
- P5: lab units (84484, 85025, 80053), tracing "number of lines" and contrast "(millilitres)" units each used by one factor only.
- P6: `units_J1885` used only by `ketorolac_pricing`.
- P7: "J8499, J8540 and J7613 each by its charges and billed units, and every line under revenue code 0637 as one dispensing line" — units used only by the share factors and lines only by `sad_pharmacy_dispensing_fee`.
- P8: `obs_hours` ("by the billed hours of code G0378") used only by `observation_pricing_method`.
- Rendering these as written makes the computation document list inputs it never uses (hinting adjustments exist); leaving them out drops parts of the baseline rule.

## 5. Empty-input edge cases where rule and compute disagree
- Every per-unit rate in the baseline evaluates to `... if units > 0 else 0`, so a charge billed with 0 units gets value 0. Each baseline rule instead says "charges multiplied by the payer class's expected allowed percentage"; only the "otherwise" sentence inside each factor carries "(0.00 when no unit is billed)". Affects P1, P2, P4, P5, P6, P8.
- P5 `contrast_method`: an HMO claim with contrast units of 0 falls back to "charges times the expected allowed percentage" in the compute; the rule says "its billed units times contrast_ml_hmo, on a Commercial HMO claim", which gives 0.00.

## 6. `claim_ext_self_administered_drug_closeout`: wider cap and conditions no record shows
- The rule defines the drugs as "billed under revenue code 0637 with codes J8499, J8540 and J7613" and says the value "never exceeds the drugs' charges". The compute caps at `sad_charges` (all revenue code 0637 charges) and counts every 0637 line for the dispensing fee.
- The conditions "dispensed by the inpatient pharmacy" and "from the emergency department cabinet" refer to facts no record holds; the compute only tests account class and campus.

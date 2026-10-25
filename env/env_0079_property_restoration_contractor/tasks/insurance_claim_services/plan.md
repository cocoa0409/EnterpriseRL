# insurance_claim_services — plan (rework round 4)

Draw (draw_counts.py, enforced by check_compute):
- task 0: prerequisite_problems=3, factor_counts=[6,6,6,6]
- task 1: prerequisite_problems=1, factor_counts=[5,4]

## Structural finding (BLUEPRINT-KNOWN candidate, unchanged)
The claims charter is thin on carrier-review and insured-own numeric writes. The insured's own computed writes used here:
(a) the dwelling depreciation release on a tier where the company does not request depreciation (Public Adjuster
Coordinated); (b) by a scoped overwrite of the recording clause, the insured's own submission of the final mold supplement
on a Homeowner Direct Pay file. carrier_denied_line is redefined only for the credited-line write-off, by a scoped overwrite
that names the base defining sentence and the carrier act (decline at final-invoice review).

## Trees (round 2, re-treed under the coordinator ruling)
Task 0 (Public Adjuster Coordinated, TX; one water job + one reconstruction contract): root
claims_ext_insured_depreciation_release (user) <- claims_ext_credited_line_writeoff (agent, value rl_written, action form),
<- claims_ext_category_reassessment_supplement (agent, value rl_pend_price, action form),
<- claims_ext_regulated_scope_supplement (agent, value rl_pend_scope, action form).
reassessment <- regulated_scope (value sc_reg_pending, action form; restored in round 4 through the regulated-cleanup
difference family, which fixes the supplement numbering: regulated-scope #2, reassessment #3). The write-off is free; all -> R.
Task 1 (Homeowner Direct Pay, LA; two mold jobs): root claims_ext_mold_reconciliation_supplement (user)
<- claims_ext_mold_protocol_supplement (agent, value mr_pending, action form).
Tables: worklog.md (XF tables round 4).

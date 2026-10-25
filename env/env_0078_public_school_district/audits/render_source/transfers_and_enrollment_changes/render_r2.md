# Renderer scan-first findings — product enroll, render round 2 (renderer findings filed verbatim by the coordinator)

# Render round 2 pre-scan findings: enroll (D = transfers_and_enrollment_changes), env_0078
Gate line: `VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN` (pass).
Round-1 findings F1-F7 are all closed in the reworked source:
- F1: the meal-status sentence no longer names the plan-length schedule; the order sentence now reads "fixed as the sum of the installment counts".
- F2: the waiver's plain sentence now reads "never more than that late fee", and "still standing" moved into the standing-part sentence.
- F3: "the amount of that late fee as posted, whatever credits stand against it".
- F4: the meal tiers are now named per branch, carryover tiers included.
- F5: "in whole or in part" in the rule and in the tool docstring.
- F6: lf_unpaid is now a plain binding with a plain defining sentence.
- F7: the bc_later / scope_eff month test, plus "never more than month_days_convention".
Sweep: every compute_basis quote, policy_source and replaced_by is verbatim in its rule. The base text is unchanged against blueprint/products/enroll.yaml.

## R2-F1 [A3: baseline names a constant only one factor uses] enroll_ext_eligibility_month_credit (extended yaml l.1677, l.1833-1835)
Source:
  baseline:
    rule: The basis-month credit is 0.00, the basis month remaining owed.
    params:
    - month_days_convention
month_days_convention (30) is read only inside factor basis_month_convention, by its calendar-day tier: compute credited_tuition l.1706, K('month_days_convention'), and ladder l.1769 "the tuition by calendar days on a month of month_days_convention days from the effective date". The baseline rule never uses it: the factor's baseline is credited_tuition '0.0', and no plain binding (bm_charge, scope_status, scope_eff, added, limited, result) reads it. A scripted check found this is the only one of the five policies with own-param baseline.params where a listed key isn't used by the baseline: credit_standard, school_year_billing_months and plan_installments_standard are all used by their baselines.
Consequence for the render: check_docs requires the computation document (role=baseline) to carry every baseline.params key that is the policy's own param, with its figure in the content ("computation doc does not carry default key ..."). So the computation document would have to state the 30-day month convention, which belongs to a single factor's Direct Certification / Categorical Eligibility method (XF A3; brief point 3, "baseline defining a quantity only one factor uses"). Not carrying it fails the gate, and carrying it, or planting an incidental "30" to satisfy the gate, would be rendering around the defect.
Fix direction: a metadata-only edit. Set enroll_ext_eligibility_month_credit.baseline.params to [] (as enroll_ext_late_fee_share_reversal and enroll_ext_late_fee_transition_waiver already have). No rule, compute or scored value changes. month_days_convention stays homed in the basis_month_convention factor document.

Render state: no document has been written to docs/enroll/. Drafts of 30 documents sit in scratch only (/tmp/render_enroll_0078/docs: 7 facets, 10 base policies, enroll_ext_late_fee_assessment, enroll_ext_combined_program_credit, enroll_ext_advance_payment). They can resume once the source line above changes; any yaml change invalidates the fingerprints, so they would be re-checked against the new source first.

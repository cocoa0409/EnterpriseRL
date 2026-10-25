# Renderer source-scan findings — product dwelling, render round 2 (renderer agent a5399c9fc9882fb34)
Saved verbatim by the coordinator from the renderer's final message (STOPPED, 0 docs written). Every round-1 finding is closed; two new wording mismatches, both stale text from the rework:

**New mismatch A: the cancellation credit refers to a rule that no longer exists** (`dwelling_ext_replacement_cancellation_credit`, in tasks/nfip_dwelling_servicing/dwelling.extended.yaml)
- This sentence appears in the rule, in baseline.rule and in overwrite[0].replaced_by: "For a policy whose current term carries an endorsement charge or a re-rate credit, or whose cancellation takes effect on or before the current term start, and only for such a policy, the returned days of each of the four components are taken as the returned-days rule of this policy states and each endorsement charge and re-rate credit of the term is taken back in the part this policy's fractions give…"
- The rule no longer defines a "returned-days rule", and no `returned_days` binding exists. It was replaced by "The refund-method rule decides how much of the risk premium and reserve fund assessment charges is given back…" (factor `refund_method_rule`) for those two lines, and by "The lines rule decides the other lines…" for the HFIAA surcharge and ICC premium.
- So the scope sentence points readers at a rule they can't find, and "returned days of each of the four components" no longer matches how the HFIAA and ICC lines are returned.

**New mismatch B: two effective-date sentences disagree in the three loan policies** (`dwelling_ext_coverage_increase_charge`, `dwelling_ext_contents_increase_charge`, `dwelling_ext_deductible_decrease_charge`)
- One sentence says: "The effective date is the latest of the dates the dating and limit rules of this policy give."
- A later sentence still says: "The change takes effect on the date the dating rules give, the policy takes the limits and deductibles on the request, and the rated risk premium on the policy is raised by the rise."
- The compute is `charged_days: MN(dated_days, premium_limit, transaction_limit, quote_limit)`, which applies the limit rules too. Read on its own, the later sentence leaves them out and gives a second reading of the date.
- `dwelling_ext_insured_increase_charge` was updated to "The increase takes effect on the latest of the dates the dating and limit rules give"; the three loan policies were not.

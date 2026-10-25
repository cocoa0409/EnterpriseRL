# Rework round 16 claims (strictly bounded: CG-39, CG-40)

- CG-39: the draft notice and the switch now price the residual case by the base installment schedule instead of 0.00. The residual case is two or more certificates on the term while the customer holds one on another term.
  - For a plan enrolled on its present plan, the down payment premium is the base down payment rule's figure; it needs no filing fee.
  - For a plan switched in from another, the scheduled installment premium is the one recorded on its installment 1 invoice.
  - Words and compute match in both policies.
- CG-40: every base invoice the two policies compute now bills the term's unbilled certificate filing fee with the in-scope read, reused unchanged: the filing whose backing term is the term the plan bills, owner or non-owner, no status filter, fee assessed after the latest invoice and not reversed. This covers:
  - the notice's out-of-scope branch: non-owner plans, never-autopay owner plans, two-certificate terms and moved plans' later invoices;
  - the switch's out-of-scope base invoice.
  The restated base sentences now name that fee.

Residual (declared, not changed in this bounded round): on a term backing several certificates, the reused in-scope read takes the first matching certificate, as it does in scope.

## Cells (consistent worlds: plan type, schedule, invoices, payments and balance rebuilt together; scratch copies)
| cell | policy | computed | by hand (governing base rule) | breakdown | |
|---|---|---|---|---|---|
| CG-40 Four-Pay owner plan (never autopay), enrolled | draft_notice | 287.00 | 287.00 | prem 372.0 + fee 10.0 + certificate fee 25.0 + standing -120.0 | agree |
| CG-40 two certificates on the term (customer holds no other) | draft_notice | 158.01 | 158.01 | prem 247.01 + fee 6.0 + certificate fee 25.0 + standing -120.0 | agree |
| CG-40 consistent non-owner Card plan | draft_notice | 158.01 | 158.01 | prem 247.01 + fee 6.0 + certificate fee 25.0 + standing -120.0 | agree |
| CG-40 moved plan, installment 5 (later invoice), certificate fee assessed 2026-10-01 | draft_notice | 133.74 | 133.74 | respread 128.23 + fee 9.0 + certificate fee 25.0 + standing -28.49 | agree |
| CG-40 switch outside its payment scope (base next invoice) | direct_bill_switch | 483.36 | 483.36 | prem 205.18 + fee 9.0 + certificate fee 25.0 + standing 244.18 | agree |
| CG-39 residual, notice, plan enrolled on its present plan | draft_notice | 158.01 | 158.01 | prem 247.01 + fee 6.0 + certificate fee 25.0 + standing -120.0 | agree |
| CG-39 residual, notice, plan switched in from Six-Pay (installment 1 recorded) | draft_notice | 149.08 | 149.08 | prem 238.08 + fee 6.0 + certificate fee 25.0 + standing -120.0 | agree |
| CG-39 residual, switch base next invoice, enrolled | direct_bill_switch | 483.36 | 483.36 | prem 205.18 + fee 9.0 + certificate fee 25.0 + standing 244.18 | agree |

All cells agree. No scored value moved; nothing else changed.

# rework claims — marketplace_orders_and_guarantee, round 9

The charter was regenerated and both task files were rebuilt by live recomputation and a replay of the real tools. task_tools.py is unchanged, and so is every scored computation. Evidence, including the probe table, is in worklog.md § REWORK round 9.

| item | status | where changed |
|---|---|---|
| R8-1 | closed per the route | **Waiting sentences** (market_ext_return_refund_claim_amount: on the two grants and the keep-it refund; market_ext_item_condition_claim_amount: on the not-received grant). Each now states, verbatim within the same sentence: "where that claim (that request) is referred to a human representative under its own policy, the filing is referred too and nothing is filed".<br>**Edge conditions.** The `prerequisite_closure` conditions in tasks/0.json and tasks/1.json follow.<br>**Resolvers.** The referral conditions stay record-stated in each resolver's own rule. |
| R8-2 | closed | **market_ext_keepit_unit_refund.** The units of the requested line already refunded (`r_line_unit_qty`) now belong to `r_promo_recovery`, and their definition sits in that factor's sentence. The plain sentence keeps only the return refunds the result nets. |
| O-r8a (latent; pre-empted per the route) | closed | **Grant rules** (market_ext_return_refund_claim_reimbursement, market_ext_unresponsive_claim_reimbursement, market_ext_missing_item_reimbursement). The room sentence states once and verbatim that claims on one order are decided in the order they were filed, earliest first, with same-day ties going to the one recorded first. The room read counts only the undecided claims that come before the claim in that order.<br>**Scopes and waits.** Each grant scope, and each wait on a grant, carries the coarse exact tests needed for that read: no two undecided claims of one reason, and no three filed on the claim's day.<br>**tasks/0.json.** The order_uniqueness text and the rationale name the decision order. |

All seven gates were re-run on the final form and pass.

# rework claims — marketplace_orders_and_guarantee, round 11

This round closes the renderer's scan STOP (render_r1.md) and the coordinator's two points. The charter was regenerated and both task files were rebuilt; task_tools.py is unchanged, and every scored computation and gold replay is unchanged. Evidence is in worklog.md § REWORK round 11.

| item | status | where changed |
|---|---|---|
| M1 | closed | **market_ext_keepit_unit_refund and market_ext_restocking_topup** (`overwrite[0].replaced_by`, also in each rule). Each tail now excludes its sibling by name: "a restocking top-up on such an order follows its own policy" and "a keep-it refund on such an order follows its own policy". It does so before "every other seller refund … still follows the return rule". |
| M2 | closed | **Same two fields.** For every out-of-scope refund the tail now restates the in-force deadline verbatim: "the seller must refund within seller_refund_business_days business days after the return is delivered …". The price, restocking and shipping parts are unchanged. |
| P1 (s_engaged) | closed | **market_ext_restocking_topup.**<br>- The allowance comparison moved into the factor `s_restock_schedule` (new binding `s_over_allowance`). The factor's sentence states when a top-up is owed.<br>- The plain gate `s_engaged` and its sentence no longer read or mention any factor quantity; the result gate reads the factor binding.<br>- Sweep: no other plain scope binding reads a factor-derived quantity. |
| P2 (r_req_date) | closed | **market_ext_keepit_unit_refund.** The dead binding `r_req_date` and "and the request date" in the scope sentence are removed. Sweep: no dead binding remains in the seven policies. |

All seven gates were re-run on the final form and pass.

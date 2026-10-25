# rework claims — marketplace_orders_and_guarantee, round 12

This round is bounded to R11-1. The charter was regenerated and both task files were rebuilt; task_tools.py is unchanged, and so are every scored computation and the gold replays. Evidence is in worklog.md § REWORK round 12.

| item | status | where changed |
|---|---|---|
| R11-1 | closed | **market_ext_restocking_topup.**<br>- The binding `s_withheld` (the restocking fees the seller withheld) now belongs to the factor `s_restock_schedule`.<br>- Its defining words moved into that factor's sentence ("the restocking the seller withheld is the restocking fees recorded on the return refund entries on the returned line …").<br>- The plain refunds sentence no longer mentions the withheld fees, and no plain binding reads them.<br>- `compute_basis` follows. |

All seven gates were re-run on the final form and pass.

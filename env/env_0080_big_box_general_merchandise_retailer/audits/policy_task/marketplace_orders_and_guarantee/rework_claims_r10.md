# rework claims — marketplace_orders_and_guarantee, round 10

This round follows the coordinator's route: the round-9 decision-order pre-emption is withdrawn. The charter was regenerated from the round-8 generator plus exactly the R8-1 and R8-2 edits. task_tools.py is unchanged. Both task files were rebuilt, and the gold replays unchanged. Evidence is in worklog.md § REWORK round 10.

| item | status | where changed |
|---|---|---|
| R9-1 | closed per the route (pre-emption withdrawn) | **Grant rules** (market_ext_return_refund_claim_reimbursement, market_ext_unresponsive_claim_reimbursement, market_ext_missing_item_reimbursement):<br>- the decide-in-filing-order sentence is removed;<br>- the room sentence and the room compute are back to the round-8 read, in which every other undecided claim reserves its claimed amount, and the order-of-decision bindings are removed;<br>- the scope tests "no two claims of one reason … no three … on the day" are removed from the grant scopes.<br>**Waits.** The same tests are removed from the waiting sentences and edge conditions of market_ext_return_refund_claim_amount and market_ext_item_condition_claim_amount.<br>**Task files.** tasks/0.json `order_uniqueness` and the rationale commute line are re-synced to the round-8 wording. |
| R8-1 | kept (closed) | The referral clause stays in the four waiting sentences and their edge conditions, unchanged from round 9. |
| R8-2 | kept (closed) | `r_line_unit_qty` stays in `r_promo_recovery`, unchanged from round 9. |

All seven gates were re-run on the final form and pass.

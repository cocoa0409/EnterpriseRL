# Renderer scan-first STOP, market render round 1 (saved verbatim by the coordinator from renderer agent a09483ba457906f8b's reply; no docs written)

SCAN STOP (render round 1): I found two source mismatches against XF recipe point C16, so I wrote no documents. docs/market/ was not created and no staging directory exists. I appended nothing to RENDER.log, and my scratch directory /tmp/render_market_0080 is removed.

The gate line was `VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN`, so I went on to the scan. The source is env/env_0080_big_box_general_merchandise_retailer/tasks/marketplace_orders_and_guarantee/market.extended.yaml.

**M1 (C16: a sibling that retires the same clause is not excluded by name).** Two policies retire the same `market_returns` clause, "The seller must refund within seller_refund_business_days business days after the return is delivered, the price of the returned units less a restocking fee …". Neither one's `replaced_by` excludes the other by name:
- `market_ext_keepit_unit_refund.overwrite[0].replaced_by` (yaml line 3653, tail at 3656; repeated in its rule at line 3732): "…every other seller refund, including every refund on an order paid with a Northgate Card, still follows the return rule, the price of the returned units less a restocking fee of at most the program's maximum percentage on an opened changed_mind return, plus the original shipping charge where the reason is a seller fault and never for changed_mind."
- `market_ext_restocking_topup.overwrite[0].replaced_by` (line 6087, tail at 6090; repeated in its rule at line 6168) has the same tail: "…every other seller refund, including every refund on an order paid with a Northgate Card, still follows the return rule, …"

The keep-it refund and the restocking top-up are both booked as return refunds on the order. So each policy's tail puts the other policy's refund back under the base return rule. That base rule has no partial-refund credit, no promotional recovery and no return-shipping keep-back. Both policies can be in scope on one order: one line with a refund-without-return answer and another line with a return authorization. In that world the two tails contradict each other.

The other two sibling sets name each other correctly. The claim-filing pair (`market_ext_return_refund_claim_amount` / `market_ext_item_condition_claim_amount`) does it with "a not-as-described claim on such an order follows its own policy" and the matching sentence. The three claim-payout policies (`market_ext_return_refund_claim_reimbursement` / `market_ext_unresponsive_claim_reimbursement` / `market_ext_missing_item_reimbursement`) each say the other two claim reasons keep "the figure its own policy fixes". Only the keep-it / top-up pair is missing this.

**M2 (C16: in-force content dropped from `replaced_by`).** The retired clause starts with the seller's refund deadline, "The seller must refund within seller_refund_business_days business days after the return is delivered". Both `replaced_by` texts above restate only the price, restocking and shipping parts for "every other seller refund". Neither carries the deadline. The deadline survives only inside each rule's out-of-scope quote ("elsewhere it fixes nothing, its figure is zero and the base rule stands: '…'"). The declared replacement does not restate it.

**Not blocking (placement, which I would render):**
- In `market_ext_restocking_topup`, the scope gate (`s_engaged`, rule line 6360: "A top-up is owed only where … the restocking they withheld is above the restocking the schedule below allows …") reads `s_restock`, which comes from the `s_restock_schedule` factor. I would put that comparison in that factor's document so the computation document stays silent about the schedule.
- `r_req_date` in `market_ext_keepit_unit_refund` is a dead binding: the request date is mentioned in the rule but nothing computes with it.

**Checks that came back clean:**
- Every `compute_basis` quote appears verbatim in its rule.
- All prerequisite sentences appear verbatim in the rules, in their declared forms.
- No factor reads another factor's binding, and no factor id is a substring of a tool name.
- Rounding is half up at the final figure only, with the 1e-9 epsilon, everywhere.
- Rule and compute agree on all seven extended policies, apart from the overwrite tails above.
- All seven tool docstrings match their bodies (format, positivity, external-card and reference checks), contain no example values, and none of the banned imports appear.

DOCS line: I did not run check_docs because no documents were rendered (scan-first STOP).

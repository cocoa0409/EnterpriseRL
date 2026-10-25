# Policy-KB bijection audit — order_returns_and_price_adjustments / task 1

## revision_1

Auditor: fresh KB auditor (brief kb_d4). Source: order.extended.yaml sha256 6aec2c3b…, task_tools.py 351e913f…; docs/order tree hash 4246d2268df53b62. Entry conditions: as in task0.md (DOCS OK; TRACEABILITY OK, 1.json copied 15 missing 0; instantiate gates green; policy side task1=PASS).

Policies in scope: order_ext_drive_up_return_refund (root), order_ext_late_express_credit; base order_returns, order_agg_no_receipt_limits, order_refund_tender, order_evt_fees, order_fulfilment_and_cancellation, order_placement_and_lines; the Same-Day Delivery variant; the two task-tool contracts.

## source_to_kb

### order_ext_drive_up_return_refund
| Source atom | KB home | Judgement |
|---|---|---|
| overwrite superseded clause (order_returns: "The merchandise refund is the line's net amount per unit times the units returned …") | merchandise_returns_policy §5, quoted, "no longer in force" | retired surface correct |
| replaced_by ("For a changed-mind return, made with a receipt at a store's Drive Up, of the whole of the one electronics-class line … every other return keeps the base refund …") | drive_up_changed_mind_returns "Scope of the refund rule", verbatim, with the restated base refund | equal; the out-of-scope base content (per-unit × units, RND, program restocking % for changed mind in restocking classes) is restated |
| customer may return at Drive Up; own decision; recorded as a return with a receipt; every gate of the returns rule | hub "Rule" | equal |
| tender / handoff as POLICY_NOT_COVERED | hub "Tender" ("with the reason policy not covered") | equal at entailment (unique mapping onto the transfer tool's enum) |
| baseline.rule "The standard changed-mind refund for an electronics-class line returned at a Drive Up is the line's net amount as charged, less a standard restocking fee of ten percent …" | drive_up_changed_mind_refund_computation "Standard method", complete with both "standard" | equal |
| assembly: refund = line's net amount as charged (or a schedule's amount) − restocking fee; restocking fee = line's net amount as charged × sum of percentages − reliefs, RND, ≥ 0; refund RND, ≥ 0; day count | computation "Assembly" | equal at entailment. The restocking multiplicand stays "the line's net amount as charged" and the refund side is named "the refund basis". This reproduces the source's split; see the runtime gt_comparison note on the apposition. |
| factor category_restocking_rate (computers/tablets/TV 15; smart home/video games 5; otherwise standard 10) | electronics_category_restocking_percentages | all tiers equal |
| factor holding_time_addition (>14 → 5; 8–14 → 2; else 0; fulfilled → return date) | holding_period_restocking_addition | all tiers equal, boundaries 15/14/8/7 |
| factor return_history_addition (≥2 → 5; 1 → 2; none 0; same order, changed mind) | earlier_changed_mind_returns_addition | all tiers equal |
| factor marketplace_return_addition (≥2 → 5; 1 → 2; none 0; changed-mind requests whatever the seller answered, request date fewer than twelve whole months before the return date) | marketplace_changed_mind_history_addition — names "Northgate Marketplace Orders and the Northgate Marketplace Guarantee" (the market charter's display_name) and the record kind (return requests, reason, request date) | all tiers equal; cross-product findability satisfied |
| factor late_delivery_relief (late & credit stands → half of credit; late & none → 2.00; else none) | late_delivery_restocking_relief | all tiers equal |
| factor adjusted_refund_basis (price drop → adjusted unit price × units returned; competitor match → net amount − match; else net amount) | price_adjusted_line_refund_basis | all tiers equal |
| **prerequisite** (state) "On an order paid in full by an external card with no Northgate Cash or gift card redeemed on it, the refund for a changed-mind Drive Up return is not fixed until the records carry the late-express credit owed on an express delivery fee charged above zero of an order fulfilled on a later calendar day than its order date." | drive_up_changed_mind_returns "When the refund is fixed", verbatim; in no other document | form, connective ("not fixed until") and strength intact. Resolution basis: late_express_delivery_credit entitlement ("is owed a late-express credit, booked as one refund of the order's express delivery fee with reason fee refund") + records (express fee 10.00 > 0, order 10-20, fulfilled 10-22, no refund on 0db756de…). |
| tool contract (order_id, original_event_id, quantity ≥ 1 whole, five reasons with not_applicable refused, restocking ≥ 0 2 dp, refund > 0 2 dp; tender refusal; Returned/Error returns) | hub invocation block | equal to task_tools.py and runtime schema |

### order_ext_late_express_credit
Overwrite: order_evt_fees "A fee is refunded only as stated …" → order_fee_rules retired bullet 2; replaced_by → late_express_delivery_credit "Fee refunds on such an order", verbatim. Entitlement (express promise, fee charged above zero, fulfilled later calendar day) and tender → hub. baseline.rule "The standard late-express credit is half the express delivery fee charged …" → late_express_credit_computation "Clause", complete. Assembly, cap at the fee standing, day count → same doc. Factors, every tier: lateness_rate_step (≥3 days 90; exactly 2 70; otherwise the standard half) → express_lateness_rate_schedule; basket_size_extra (≥75 → 10; 35–<75 → 5; else 0) → express_basket_size_extra; age_check_extra_step (≥2 → 10; 1 → 5; none 0; lines not units) → express_age_check_extra; grocery_standby_amount (0.75 × lines / 1.00 / 0) → express_grocery_standby_amount. Tool contract → hub invocation. PASS.

### Base policies governing the subjects
order_returns → merchandise_returns_policy (§1–§9; §5 retired; §3 with card extension and holiday start) + return_windows_and_methods (class windows, anchor, holiday start, per-program methods, label fee, restocking % / classes, fee refund reasons, defect route). order_agg_no_receipt_limits → returns_without_receipt_and_gift_receipts + proof_of_purchase_and_refund_tender. order_refund_tender → refund_tender_order_of_restoration. order_placement_and_lines → order_placement_and_line_pricing + checkout_terms_by_program. order_evt_fees / order_fulfilment_and_cancellation as in task0.md. Same-Day Delivery variant figures (min 10.00, fee 9.99, express 14.99 / 2 h, member benefit yes, methods in store / Drive Up / mail, label 0.00, restocking 0 / none, report days 2, alcohol yes) are carried in the program tables. PASS.

## kb_to_source

No normative claim without a source found in the order corpus (same sweep as task0.md). Task-specific checks: the relief document's gloss "Late-express credit standing on the order (a refund booked against its express delivery fee)" restates the source's "a late-express credit stands on the order" in record terms, the same way the depended-on hub describes the booking; it adds no condition. "Points of judgement" in the Marketplace addition ("a changed-mind request the seller declined is counted") is the source's "whatever the seller answered". (1) Cross-problem operational guidance: none. (2) Opening world state written as fact: none; no document or schema contains 9.50, 1.85 or 52.13.

## bijection_verdict

**PASS.** Both policies of this task (every overwrite, the baseline, every tier of all ten factor ladders, the prerequisite and the two tool contracts) are carried at the same strength. The apposition in the drive-up Assembly paragraph ("the refund basis, which is the line's net amount as charged") is recorded as an observation only, because the restocking sentence names its own multiplicand separately, exactly as the source does. Late-change computation B1 (task0.md) does not govern this task.

## dependency_form

- The single state-form prerequisite sentence stands verbatim in the blocked hub only. It is not restated in action form and names no tool, performer or document.
- `credit_late_express_4845a2c0` appears only in its own hub, and `return_item_at_drive_up_b4cf62ab` only in its own hub.
- No route, step list, dependency table, cross-problem FAQ or wrong-vs-right contrast.
- Titles are general subjects. "Changed-Mind Returns at Drive Up for Northgate Same-Day Delivery Orders" is the on_request policy's own request type, so it is not a mirror of this task.
- The depended-on hub is reachable through the sentence's own words ("late-express credit", "express delivery fee") and through the record's fee type express_delivery.
- Factor documents state their ladders as rules and do not point at the computation document or at one another. The relief document names the late-express credit because the source ladder reads it, and it gives no instruction to book it.
- Verdict: **PASS** (no KB-EXPLICIT RED). Blind hop H1: state-derived.

## src (policy-side notes)

- No source-layer note specific to this task. src=schema_cutoff_free_desc (task0.md) concerns the large-item program only.

## revision_2

Gate snapshot as in task0.md revision_2. No document this task's policies are carried in changed. The drive-up and late-express hubs, computation and factor documents are byte-unchanged since revision_1 (mtime 2026-10-24T23:45:44). The two changed documents govern Scheduled Large-Item Delivery only and add no claim touching this task.
- bijection_verdict: **PASS** (no regression). dependency_form: **PASS**.

## revision_3

Cross-product re-judge. The gate snapshot is as in task0.md revision_3; docs/order is unchanged.

### (1) Conditional readings, resolved
- Marketplace addition ↔ docs/market: the same objects (return requests with a reason, request date, the seller's answer). "whatever the seller answered" matches the four seller answers in "Northgate Marketplace Returns Policy". Consistent.
- Fee rows ↔ docs/membership: "Membership Delivery Benefits on Northgate Orders" (status as of the order date; same-day waived at or above the 35.00 minimum; member express fee in place of the standard express fee; the lowest single source) and "Delivery and Return-Pickup Benefit Schedule" (Northgate+ Monthly: 35.00 / 6.99 / 10.00; statuses trial, active, cancel pending). Consistent with docs/order (Same-Day membership benefits "yes").
- Card: not engaged (no card account). Nothing is conditional. **KB side: CLEAN.**

### (2) Re-pricing of every other-product row seeded in this world
| Row | Seeded | Published rule gives | Verdict |
|---|---|---|---|
| membership holding: Northgate+ Monthly, enrolled/term start 2024-04-21, external card, canceled 2026-10-21 | — | monthly cancellation "takes effect at the end of the billing period" (cancel pending, then closed on the renewal date); billing periods start on the 21st, so closing on 2026-10-21 is a renewal date | producible |
| order fee rows of 465fb8ff… priced by the membership: same-day 0.00 (standard 9.99, waiver membership), express 10.00 (standard 14.99, waiver membership) | — | order date 2026-10-20, status then cancel pending or active (benefit statuses); merchandise subtotal 118.93 ≥ 35.00 → same-day waived; member express fee 10.00 | producible |
| Northgate Cash on the order's lines | none | "Northgate Cash Earning Rule" clause 2 / consumer schedule: "a line earns only if the membership is not canceled on the fulfillment date". Fulfilled 2026-10-22, membership canceled 2026-10-21 → nothing; alcohol excluded anyway. Reversal on the phone-stand return: nothing earned, nothing reversed | producible |
| membership fee charges (12.95 monthly since 2024-04-21), the two benefit-use rows of 2026-10-20, the confirmed cancellation request | absent (find_membership_events / find_membership_requests: none) | owed by "Membership Fee Charging and Billing Periods", "Benefit uses" and "Cancellation and Resumption Terms" §1 | accepted residue (unread rows; gold reads find_membership_holdings only) |
| market holding e23ff71b… Pro Seller: order 2026-06-03, shipped 06-04, max estimated delivery 06-11, delivered 06-09 | — | handling 1 business day; 1 + 5 business days → 2026-06-11 ("Shipping and Delivery Standards") | producible |
| market lines 39.99 / 12.99 / 15.99, shipping 5.99 | — | seller's rate | producible |
| return requests 2026-06-14: speaker changed_mind, cable defective; seller answers 06-15 authorized | — | inside the 30-day Pro Seller window; answered within 2 business days | producible |
| seller refunds 2026-06-19: 39.99 (speaker), 12.99 (cable), 5.99 shipping | — | Pro Seller maximum restocking 0% → full price; original shipping "refunded with a seller-fault return" (the defective cable) and never for change of mind — one shipping refund of 5.99; net paid 15.99 | producible |
| restocking top-up | none | not owed: two return authorizations on the order, and nothing withheld ("When a top-up is owed") | producible (nothing owed) |

No other-product row of this world fails its product's published rules apart from the unread-row residue.

### (3) Owed-at-once writes
- Market: no top-up, guarantee claim or reimbursement is owed. A market write would in any case add no market_request_return changed_mind row, which is the only market read.
- Membership: no earning, reversal or refund is owed. Membership rows feed no order computation.
- Card / gift / plan: none held.
- Verdict: none moves a scored read.

### bijection_verdict / dependency_form (revision_3)
**PASS / PASS.**

## revision_4

Seed-only round; task 1's rows are unchanged and GT is unchanged. Docs and tools are unchanged. bijection / dependency_form / cross-product re-pricing: **PASS / PASS / producible** (as in revision_3).

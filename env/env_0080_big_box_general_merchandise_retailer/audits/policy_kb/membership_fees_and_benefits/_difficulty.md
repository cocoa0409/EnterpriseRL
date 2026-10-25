# KB audit close-out — membership_fees_and_benefits (product: membership)

## revision_1

| Task | Runtime blind audit | Two-way scan | Dependency form |
|---|---|---|---|
| 0 | PASS (runtime_context/membership_fees_and_benefits/0.md; blind hash d721b77c…) | PASS | PASS |
| 1 | PASS (runtime_context/membership_fees_and_benefits/1.md; blind hash 7429912c…) | PASS | PASS |

Closing checklist
- Audit files one per task, blind answers frozen before reveal, no contamination.
- Every normative atom of membership.extended.yaml (7 extended policies, 36 factors, 5 prerequisite edges, 5 distinct retired base clauses across 10 overwrite entries, base policies, variant figures) has an equivalent home in docs/membership; prerequisite sentences verbatim, state form, only in the blocked hubs; every factor ladder whole in its own document and findable from record words; no route, chain, other-problem tool name or task-mirroring title.
- Final-form gates (kb_snapshot 2026-10-24T18:55:54Z): `DOCS OK`; `TRACEABILITY OK` (2 tasks, 0 missing); EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; yaml 5d2eaec7…, task_tools e55b2956…, docs tree b60c72586c181bf2.
- Conditional: card and order corpora not yet published; card tier names and refund-reason values read from records.

Source-layer items (no effect on either task's world, KB carries them faithfully):
- src1 — membership_ext_business_cash_earning, factor payment_hold_rate: "before the date the fee of that billing period settled" is silent when that fee has not settled; compute (`held_period_settled or '9999-12-31'`) treats it as still on hold (renderer note 1).
- src2 — zero-amount class: both refund rules floor at zero ("never below zero") while confirm_annual_membership_cancellation_fe7f482c / confirm_business_membership_closure_a0a2c96c refuse `refund_amount_usd <= 0`; likewise a Business earning cut to 0.00 by the twelve-month cap ("nothing posts") against the closure prerequisite "…has its Northgate Cash earning on the membership's ledger, when that line earns Northgate Cash", with the posting tool refusing 0.00 (renderer note 3).
- Renderer note 2 (one-factor quantities filed as plain bindings): no defect.

KBVERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=src1,src2

## revision_2

Round-2 re-audit after rework revisions 5–7 and re-render round 2 (`RENDER round 2: DOCS OK`; policy `VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN`; kb_snapshot 2026-10-24T23:47:38Z all green, yaml 32dbad13…, task_tools c46346f5…, docs ecbf7356ea981202).
- src1 (payment-hold rate on an unsettled held fee): closed — rule defines "held" incl. "has not yet settled", matching compute; docs carry the definition and an unsettled-fee boundary table.
- src2 (zero-amount class): closed — zero refunds are recorded and confirmed with no refund entry, both confirm tools accept 0.00; earning prerequisites and earning rules now wait on / post only earnings of at least one cent below the Business twelve-month limit, consistent with the posting tools' positivity.
- Changed documents: 7 (annual hub + computation, Business hub + computation, both earning computations, Business payment-hold rate); 66 unchanged. Blind re-check first: both tasks' answers unchanged and equal to GT. No regression; no new defect. Observation only: the Business baseline rule now opens with the limit definition, which the KB carries in the hub and the Business earning computation, not in the closure computation (no number reads it there).

KBVERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE

## revision_3

Cross-product re-judge (all seven corpora published; validate_scenario VALID per coordinator). kb_snapshot 2026-10-25T04:51:30Z: `DOCS OK`; `TRACEABILITY OK` (0.json 22/0, 1.json 28/0); EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; yaml 32dbad13…, task_tools c46346f5…, docs/membership ecbf7356ea981202 (unchanged since revision_2). Other-product rows enumerated through db_query.py (find_* by customer): both worlds hold only order and card rows — no card_events, card/order requests, plan, market, gift or trade rows.

### (1) Conditional readings resolved
- Card tier/status for card points / cardholder courtesy: tier names in "Northgate Card Cardholder Savings… Benefit Terms by Card" and "Applications and Account Opening" equal the record values (`Northgate Store Card`, `Northgate Business Mastercard`), status `active` → unchanged tiers.
- Refund-reason values: "Fulfilment, Pickup Holds and Cancellation" — "refunded without a return with reason item not received or item damaged with no return" → `item_damaged_no_return` = damaged on arrival, `item_not_received` = never received.
- Line net amount: "Placing an Order and Pricing Its Lines" (selling price less promotions and, Northgate Card paying, the cardholder discount; what was paid before tax) = membership "net amount".

### (2) Re-pricing of every seeded other-product row, as of its posting date
Task 0 (Annual, Store Card 5 %, opened 2026-09-02):
| Row | Published rule | Repriced | Seed | OK |
|---|---|---|---|---|
| 036cd13b vacuum In-Store 2025-11-20, line 299.99 ext card | Placing an Order; In-Store fee 0 (Fee Schedule); 16-digit receipt | 299.99, no fee | 299.99 | yes |
| 683dc818 LEGO Order Pickup, ready 01-09, fulfilled 01-10 | Pickup hold 5 days; Pickup fee 0 | fulfilled within hold | as seeded | yes |
| c5fa18c7 mixer Ship to Home 07-14: line 429.99 − 30.00 promo = 399.99; shipping 5.99 waived | Fee Rules: threshold 35.00, tie order threshold → membership → card, source `order_threshold`; membership records a use on a tie (Delivery Benefits) | fee 0.00 `order_threshold`; benefit use 5.99 | same | yes |
| 5a4b1848 price drop 07-24, 30.00 | Price Drop: 14 days from order date (≤ 07-28); (399.99 − 369.99) × 1, external card | 30.00 | 30.00 | yes |
| 2faf4e07 return 10-14, 369.99, not_as_described, in store, receipt | Returns §3: GM 90 days from fulfilled 07-17 (≤ 10-15), no card extension (ext card); refund never exceeds paid net of earlier refunds (Refund Tender) → 399.99 − 30.00; no fee-refund reason, fee 0 | 369.99; order → returned | same | yes |
| a5fd913b towels In-Store 08-21, 64.00 | line 64.00; Cash 10.20 redeemed in store (Annual channels in store) | 64.00 | 64.00 (amount_paid = lines − refunds, per schema) | yes |
| b8bbf791 wipes Same-Day 10-06 app: 3 × 10.99 = 32.97 − 5 % 1.65 = 31.32; fee 9.99 → 6.99 member same-day (32.97 < 35.00), source `membership`; card free shipping not open to Same-Day | Placing an Order; Card Benefits (5 %, half up per line, applied last); Fee Schedule; Delivery Benefits | 31.32, fee 6.99, benefit use 3.00 | same | yes |
| 1e145ea7 never-received refund 10-07, 1 unit 10.44 | report within 2 days; one unit of the paid line 31.32/3; fee kept ("only when the whole order was not received or under the returns rule", restated in Missed-Appointment Credit doc) | 10.44, no fee refund | same | yes |
| card 25c809aa Store Card: in store 2026-09-02, limit 1500.00, balance 27.87 | Applications; Credit Line terms 300–10000; balance = 31.32 + 6.99 − 10.44 | consistent | same | yes |

Task 1 (Business, Business Mastercard 3 %, no free shipping, 0 extra return days):
| Row | Published rule | Repriced | Seed | OK |
|---|---|---|---|---|
| f7b44318 chairs Ship to Home 2025-07-08: 990.00 − 29.70 | 3 % half up; fee 5.99 waived `order_threshold`, membership tie use 5.99 | 960.30 / 0.00 | same | yes |
| 9c776ee3 laptop 2025-11-03: 1249.00 − 37.47 | same | 1211.53 / 0.00 | same | yes |
| b1226e10 towels In-Store 2026-02-17: 194.94 − 5.85 | 3 % of 194.94 = 5.8482 → 5.85 | 189.09 | same | yes |
| af30f010 monitors 04-09: 1119.96 − 33.60 = 1086.36; fee waived, tie use 5.99 | 3 % of 1119.96 = 33.5988 → 33.60 | 1086.36 | same | yes |
| 047ca675 BestBuy.com match 04-20 to 259.99 | window to 04-23; BestBuy.com on Ship to Home list; (279.99 − 259.99) × 4 net of 3 % | 77.60 | 77.60 | yes |
| cc520a87 return 1 monitor 05-12 defective, in store | electronics 30 days from 04-14 (≤ 05-14), 0 extra days; refund = paid net of discount and adjustment per unit (1086.36 − 77.60)/4; defective is a fee-refund reason but the fee was 0.00 | 252.19 | 252.19 | yes |
| e5e36ac1 coffee maker Ship to Home 04-30 ext card 189.99; fee waived threshold, tie use 5.99 (membership active 04-30) | | 189.99 / 0.00 | same | yes |
| d921f4c0 price drop 05-12, 20.00 | window to 05-14; after fulfilment 05-04 | 20.00 | 20.00 | yes |
| c7793dee damaged refund 05-25, 169.99 | Ship to Home report days 30 from 05-04; paid 189.99 − 20.00; order → returned | 169.99 | same | yes |
| 646cd231 printers Order Pickup 05-16 (membership on payment hold): 698.00 − 20.94; ready 05-17, collected 05-18 | Pickup fee 0, no benefit to withhold during the hold; hold 5 days | 677.06 | same | yes |
| 807b183d printer damaged refund at counter 05-18 | Pickup report days 2; one unit 677.06/2 | 338.53 | same | yes |
| d3ebf256 wipes Ship to Home 05-29 placed, 28.50 < 35.00; fee 5.99 → 0.00 `membership`, use 5.99 | membership active on the order date (hold cleared 05-20) | 0.00 `membership` | same | yes |
| card a7b77abb Business Mastercard, opened 2024-02-22, limit 10000.00, 2 authorized users, balance 338.53 | Credit Line terms 2500–50000, ≤ 25 users; business profile; balance = printer purchase net of its refund after the 05-12 statement | consistent | same | yes |

No seeded row differs from what its owning product's published rules produce. Accepted residue (not RED, per brief/XF 29): card purchases, credits and statements behind both card balances are not seeded as card_events; the 10.20 Northgate Cash tender on task 0's towel order has no order-side tender row (the order_events tender enum has no Northgate Cash value). Neither is read by any gold step.

### (3) Owed-at-once writes that could move a scored read
None found:
- Order: no express Same-Day order (late-express credit not engaged); no large-item order (missed-appointment, late-change, haul-away credits not engaged); every price-adjustment window closed except task 0's wipes order (order 10-06, last day 10-20) where an adjustment needs a customer request and a lower qualifying price, and would not change Cash already earned ("Northgate Cash already earned on the line is not changed"; the closing-share factor reads price adjustments only on the returned mixer line, already adjusted once); no fee refund owed on the partial never-received wipes refund.
- Card: no credit balance, late fee, dispute or statement row exists; nothing owed at once.
- Plan / market / gift / trade: no holdings in either world.
- Membership itself: task 1's older printer refund 807b183d falls under the base reversal rule, "which no schedule of these membership rules prices or posts", and reverse_unreturned_refund_cash_522719bc refuses it ("not the member's most recent damaged-on-arrival or never-received refund"), so no write can be made on it — observation only.

### Verdict
Both tasks PASS on all three parts; no KB defect; no source defect; nothing regressed.

KBVERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=NONE

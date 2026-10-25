# Runtime-context blind audit — order_returns_and_price_adjustments / task 0

## revision_1

freeze declaration: the blind_answer below was written to disk before any source-layer material (extended yaml, task_tools.py, task JSON GT fields) was read. freeze hash (sha256 of the blind_answer body, first 16 hex): d14da8e32bf5aaf3

## blind_answer

- auditor: fresh KB auditor (erl-kb-doc-policy-audit, brief kb_d4), independent of the renderer and of the policy-side auditor.
- freeze time: 2026-10-24T23:59Z (UTC wall clock of the audit run); docs/order tree hash 4246d2268df53b62 (56 files, from kb_snapshot.sh).
- visible materials used: docs/order/*.json title/content only (no meta); runtime tool schemas (share read tools, verify_customer_identity, transfer_to_human_agent, and the six order task-tool schemas exposed on unlock); `.audit_views/runtime/order_returns_and_price_adjustments/task0.runtime.json` (frozen_time + user_scenario); DB through the tool-shaped `db_query.py` path (find_customers, find_order_holdings/events/requests, find_plan_holdings/events/requests, find_membership/card/gift/market/trade_holdings, find_verification_log, find_handoff_log, KB_search).
- forbidden and not read before this freeze: order.extended.yaml, task_tools.py, tasks/*.json (evaluation_criteria, computations, expected, charter_scope, design_rationale, solvability_contract, initial_state), doc meta, render plan, verification scripts, tool implementations, existing GT and audits (only the policy-side VERDICT tail line, as the brief required).
- DB side: blind (tool-shaped queries only).

### 1. Request, timing, authorisation, simulator behaviour
Marisol Navarro asks to move the delivery of order 4108836215 to 2026-10-31 and nothing else; she is willing to pay a "reasonable" late-change fee and accepts the figure the agent gives. Identity: phone 3035550124 and DOB 1984-06-17 (two details; `verify_customer_identity` "confirms identity only when at least 2 details agree"). The simulator is passive: it volunteers nothing about earlier dates, fees or the old fridge unless asked; it "let[s] the agent go ahead" with credits the agent says are owed; it runs the user-owned reschedule tool when handed over with order 4108836215, 2026-10-31 and the fee stated. Authorisation mode: the reschedule is "the customer's own decision ... confirmed by the customer" and the tool is "the customer's own tool" (owner=user); the three credits are agent-side tools.

### 2. Act now / wait / refuse at 2026-10-24 08:10 MDT
Act now, but the late-change fee cannot be fixed yet. Grounds:
- find_order_holdings: order e6af873a…, `variant_name` Northgate Scheduled Large-Item Delivery, `status` placed, `order_date` 2026-10-08, `scheduled_date` 2026-10-24, `reschedule_count` 5, `payment_method_type` external_card, amount_paid 2677.98. No Northgate Cash / gift-card rows on the order (find_order_events) and no gift holdings → "paid in full by an external card with no Northgate Cash or gift card redeemed on it" → booked at the care desk, no handoff.
- Hub "Scheduled Large-Item Delivery Appointment Changes": "may be rescheduled by the customer at any time down to the scheduled day itself, whatever tender paid the order" → the request today (the scheduled day) is allowed.
- Same hub, "When the late-change fee is fixed": three sentences (missed-appointment credit, replacement haul-away credit, late-change goodwill refund must be on the records first) — see item 6; each waited-on state does not hold now (no refund rows on the order).

### 3. Object, keys, include/exclude
Order e6af873a-4a61-4ab9-bd90-e896d4aa8e3b (#4108836215). Exclude the 2024 order 9b7fd990 (#4024315587, fulfilled; its own 49.00 delivery fee is a different order — "nothing on one order is netted against another"). Rows on the target order: line 1 Arcadia refrigerator 1699.99 (major_appliances, qty 1); line 2 Arcadia range 799.99 (major_appliances, qty 1); fee 17d35d6a… large_item_delivery 49.00 (standard 49.00, waiver none); fee db70d792… haul_away 50.00 (standard 50.00); fee a52f4d88… late_cancellation 79.00 dated 2026-10-19 (the only late-change fee row). find_order_requests: 3 confirmed reschedule_delivery requests (10-09, 10-12, 10-19). Northgate moves = reschedule count 5 − 3 confirmed requests = 2. Plan records: Northgate Protect Standard 3-Year plan on the old 2024 fridge; settlements 2025-06-20 repair 186.40 and 2026-10-06 `reimbursement_egift_card` 663.59, `covered_item_category` major_appliances. Most recent settlement = 2026-10-06 reimbursement (the only settlement that day).

### 4. Scored parameters
(a) Missed-appointment credit (doc "Amount of the Missed-Appointment Credit" + factors). Base 20% of the delivery fee charged 49.00. Factors found from the records: wait length order date 10-08 → scheduled date carried now 10-24 = 16 days → +10% ("Fourteen days or more"); haul-away items 50.00/25.00 = 2 old items → +5%; order value 1699.99+799.99 = 2499.98 → +5% ("2,000.00 or more"); repeated Northgate moves 2 → +20%; reschedule allowance 3 confirmed requests = exactly one above the 2 free → +5%; major-appliance flat 2 units × 5.00 = 10.00. Percentage 65% × 49.00 = 31.85 + 10.00 = 41.85; cap delivery fee standing 49.00 → **41.85**.
(b) Replacement haul-away credit. Settlement read 2026-10-06 reimbursement, major_appliances; order carries major_appliances; distance 10-06 → 10-08 = 2 days (0–90) → owed. Credited haul-away factor: settlements of the category the same day = 1, old items booked 2 → "the program's haul-away fee for one item" 25.00. Extras: kind major appliance +20%; settled value 663.59 → +5% (500–<1000); timing 2 days → +40%. 25% + 65% = 90% × 25.00 = 22.50; cap haul-away standing 50.00 → **22.50**.
(c) Late-change goodwill refund. Latest late-change fee row > 0: a52f4d88… 79.00 (2026-10-19). Base 25%. Extras: Northgate moves 2 → +25%; haul-away crew 2 old items → +10%; recency 10-19 → scheduled date carried now 10-24 = 5 days → +25%; installation-crew standby 2 units × 2.50 = 5.00. 85% × 79.00 = 67.15 + 5.00 = 72.15; cap 79.00 − 0 refunded → **72.15**.
(d) Late-change fee (after a–c). Request day 10-24 to scheduled 10-24 = 0 days ahead → not free (also 3 confirmed requests ≥ 2 free). Baseline notice charge = program late cancellation fee 49.00 (fee schedule). Factors: short notice "the request falls on the scheduled day itself" → delivery fee still standing 49.00 − 41.85 = 7.15; installation surcharge 2 units → 20.00; crew charge, haul-away standing 50.00 − 22.50 = 27.50 > 0, request on the scheduled day → 27.50; repeat late-change surcharge, late-change fees standing 79.00 − 72.15 = 6.85 (above 0, below 49) → 10.00; repeated reschedule requests 3 = one above the free 2 → 5.00; courtesy reduction 2 Northgate moves → −30.00. Total 7.15 + 20.00 + 27.50 + 10.00 + 5.00 − 30.00 = **39.65** (never below zero; rounded to the cent).
Tier provenance (cross-product): (b)'s owed test, credited-haul-away count, kind, value and timing tiers rest on find_plan_events returns of Northgate Protect Protection Plans (plan_settle_claim 2026-10-06, settlement_method reimbursement_egift_card, amount 663.59, covered_item_category major_appliances). All other tiers rest on this order's rows and requests.

### 5. Tool sequence, owners, dependencies, terminal state
find_customers(phone 3035550124) → verify_customer_identity(customer_id, phone, DOB) → find_order_holdings / find_order_events / find_order_requests → find_plan_holdings / find_plan_events → [agent] credit_missed_appointment_73d9a081(order e6af873a…, fee_event_id 17d35d6a…, 41.85); [agent] credit_replacement_haul_away_849732e1(order, db70d792…, 22.50); [agent] refund_late_change_fee_56da608d(order, a52f4d88…, 72.15) — these three in any order among themselves (none reads another's refund), all before the fee is worked out → [user, handed over] reschedule_large_item_delivery_d930ab59(order e6af873a…, 2026-10-31, 39.65). Terminal: order scheduled 2026-10-31, reschedule count 6, one late-change fee row 39.65, three fee refunds booked.

### 6. Problem tree derived from the visible materials
Root: customer's reschedule (customer write). Blocked-side sentences, hub "Scheduled Large-Item Delivery Appointment Changes", "When the late-change fee is fixed":
- H1 "the late-change fee is fixed only after the records carry the missed-appointment credit owed on a large-item delivery fee charged above zero for an order on which Northgate itself moved an appointment." Records: delivery fee 49.00 > 0; moves 2; no refund against 17d35d6a… → state does not hold. Searching "missed-appointment credit" finds "Missed-Appointment Credit on Northgate Scheduled Large-Item Delivery", whose entitlement ("is owed a missed-appointment credit on that fee, booked as one refund of that fee with reason fee refund") describes the write. **state-derived**.
- H2 "the late-change fee is not fixed until the records carry the replacement haul-away credit owed on a haul-away charge above zero of an order placed zero to ninety days after a Northgate Protect claim settlement that replaced or reimbursed an item of a merchandise category the order carries." Records: haul-away 50.00; plan settlement 2026-10-06 reimbursement of a major_appliances item; order 2026-10-08 carries major_appliances; no refund on db70d792… → not held. "Replacement Haul-Away Credit for Northgate Protect Settlements" describes the booking. **state-derived**.
- H3 "before the late-change fee is fixed, the records must carry the late-change goodwill refund owed on the latest late-change fee row with an amount above 0.00 on an order on which Northgate itself moved an appointment." Records: late-change fee row 79.00, moves 2, no refund → not held. "Late-Change Goodwill Refund — Northgate Scheduled Large-Item Delivery" describes the booking. **state-derived**.
- Second level: the three depended-on documents carry no "fixed/waits" sentence of their own; no further hop. Order: H1, H2, H3 (any order among them) → root. The numbers confirm the order matters: the fee's short-notice, crew and repeat-surcharge factors read the delivery fee, haul-away and late-change fees *standing*, which change only once the credits are on the records; the credits' wait-length and recency factors read the scheduled date the order carries "when the credit is worked out", which the reschedule would move.
No hop pre-solved: no document of the reschedule names another tool, route or chain.

### Counter-proofs
- "Do only the reschedule": excluded — the hub says the fee is "fixed only after" / "not fixed until" / "before ... the records must carry" each credit; booking the reschedule now would book a fee the visible rule says is not yet fixed. It would also give a different fee (notice 49.00 standing instead of 7.15, crew 50.00, repeat 20.00 → 49.00+20+50+20+5−30 = 114.00).
- Closest alternatives: free reschedule excluded by 0 days ahead and 3 ≥ 2 requests; baseline 49.00 notice charge replaced by the short-notice tier for "the request falls on the scheduled day itself"; old 2024 order excluded (each order stands on its own); 2025 repair settlement excluded as not the most recent (and "A settlement by repair ... owe[s] no replacement haul-away credit"); the 79.00 row is the late-change fee (fee type late_cancellation per hub: "charged on the order as a fee of the late cancellation type").
- Fall-back numbers (computation documents only): missed-appointment 20% × 49.00 = 9.80; haul-away 25% × 50.00 = 12.50; goodwill 25% × 79.00 = 19.75; late-change fee = notice charge = late cancellation fee 49.00. All definite and different from 41.85 / 22.50 / 72.15 / 39.65.
- Factor findability: each factor was reached from record words — "haul_away" fee row (haul-away items / crew docs), "major_appliances" lines (flat amounts, surcharge), reschedule_count vs confirmed `reschedule_delivery` requests (Northgate moves, allowance, repeated requests, courtesy), order/scheduled dates (wait length, recency), `late_cancellation` row (repeat surcharge), plan_settle_claim rows of Northgate Protect (KB_search "Northgate Protect claim settlement reimbursement major appliances haul-away" returns the four haul-away factor docs and the computation doc in the top 7). No computation document hinted that a variation exists.

### Residual observations (visible side, for step 2)
- "Pickup Holds, Cancellation Statuses and Delivery Changes" still describes the cutoff-hours column as "hours ... before which a large-item order can be canceled or rescheduled without a fee" and free reschedules as "made before the cutoff", while the hub's in-force test is "two or more calendar days ahead" with a fee "every other reschedule"; not triggered here (0 days ahead, 3 requests).
- The goodwill refund cap reads "refunds already booked against the order's late-change fees", the missed-appointment cap "the large-item delivery fee standing" — distinct ledgers, so the three credits do not order one another.

## gt_comparison

- reveal time: 2026-10-25T00:05Z, after the blind_answer above was on disk (freeze hash d14da8e32bf5aaf3). Revealed: order.extended.yaml (sha256 6aec2c3b…), task_tools.py (351e913f…), tasks/0.json evaluation_criteria / computations / prerequisite_closure.
- item-by-item:

| Item | Blind answer | Source / GT | Same? |
|---|---|---|---|
| root problem | customer's reschedule of e6af873a… | root_problem order_ext_late_change_fee | same |
| edges | H1 missed-appointment, H2 replacement haul-away, H3 goodwill refund, all state-derived, all before the root | three `form: state` edges root → order_ext_missed_appointment_credit / order_ext_replacement_haul_away_credit / order_ext_late_fee_goodwill_refund; policy_source sentences identical to the hub's three bullets | same |
| missed-appointment credit | 41.85 (fall-back 9.80) | expected 41.85, baseline_result 9.80 | same |
| replacement haul-away credit | 22.50 (fall-back 12.50) | expected 22.5, baseline_result 12.5 | same |
| late-change goodwill refund | 72.15 (fall-back 19.75) | expected 72.15, baseline_result 19.75 | same |
| late-change fee | 39.65 (fall-back 49.00) | expected 39.65, baseline_result 49.0 | same |
| fee_event_ids / order_id / date | 17d35d6a…, db70d792…, a52f4d88…, e6af873a…, 2026-10-31 | same ids and date in evaluation_criteria | same |
| owners | three agent-side credits, user-owned reschedule handed over | agent unlock+call ×3, unlock_user + user call | same |
| reads | customer, verify (phone+DOB), order holdings/events/requests, plan holdings/events | same, plus a confirmatory find_order_events on the 2024 order | same (extra read is confirmation only) |

- tool schemas/owners/effects match the source contracts (task_tools.py error paths: tender refusal, YYYY-MM-DD, non-negative 2-dp fee; fee-type reference checks for the credits).
- The blind residual on the cutoff-hours / free-reschedule column descriptions is not triggered in this world; carried to the policy_kb file as a source-layer note.
- Verdict: **PASS** (no KB-RUNTIME RED). Every hop state-derived; no hop pre-solved.

## revision_2

- re-audit time 2026-10-25T00:10Z; docs/order tree hash 7f236facbf67bf41 (round 1: 4246d2268df53b62). Changed documents (mtime after the round-1 audit): late_change_fee_computation_642f339e.json and pickup_hold_and_order_changes_table_e8466089.json. The other 54 are unchanged.
- contamination_disclosure: this auditor read the source layer and GT in revision_1, so no fresh blind answer is possible. Revision_2 re-reads the changed visible surface only. The revision_1 blind_answer above stays frozen and is not rewritten.
- Re-check against the changed documents. §3 of the computation document now reads "The standard late-change notice charge is the program's late cancellation fee, and the standard late-change fee is that notice charge …". The baseline is a default again, and the short-notice tier ("the request falls on the scheduled day itself" → the delivery fee still standing) applies without a competing unconditional sentence. The new "Rule in force …" paragraph of the pickup/changes table restates the in-force reschedule rule; on this world it gives the same not-free outcome (0 days ahead, 3 confirmed requests ≥ 2 free). The derivation still reaches 41.85 / 22.50 / 72.15 / 39.65. The problem tree is unchanged: three state-derived hops, none pre-solved.
- Verdict: **PASS**.

## revision_3

- Re-audit 2026-10-25T04:55Z (cross-product re-judge; all seven products published). docs/order tree hash 7f236facbf67bf41, unchanged since revision_2. Same contamination_disclosure as revision_2: non-blind, and the revision_1 blind answer stays frozen.
- Conditional readings resolved. The plan-side factor and owed-test documents read the most recent settlement, its method, covered item category, date and amount. Those words match the published plan corpus ("Settlement of Approved Northgate Protect Claims": settlements "by repair, replacement or reimbursement"; "A reimbursement is issued as a Northgate eGift Card"). Northgate Card readings (return-window extension, cardholder discount) are not engaged, since the customer has no card account. The derivation from visible materials still gives 41.85 / 22.50 / 72.15 / 39.65.
- The seeded plan rows are not what the published plan rules produce; see policy_kb task0 revision_3, src items. The runtime derivation reads them as authoritative records and is unaffected. The customer's line "this month paid you back with an eGift card" has no gift-card holding behind it (find_gift_holdings: none). This is accepted unread-row residue.
- Verdict: **PASS**.

## revision_4

- Seed-only round (rework_claims_r7). Re-check 2026-10-25T05:15Z. This is non-blind (same contamination_disclosure as revision_2); the revision_1 blind answer stays frozen.
- Changed visible rows (via db_query.py):
  - the 2024 order 9b7fd990… line, now Frostline 28 cu. ft. 1799.99 (selling 1899.99, promo 100.00), amount paid 1848.99;
  - the plan holding (price 1799.99, premium 199.00, liability remaining 149.00, fulfilled 2026-10-06);
  - the plan ledger: registration 1948.99; repairs 374.00 (2025-04-25), 374.00 (2025-11-14) and 404.00 (2026-05-18); final mechanical-failure claim settled 2026-10-06 by reimbursement_egift_card 647.99.
- Blind-view derivation with the new figures:
  - The settlement read is still 2026-10-06, a reimbursement, major_appliances, 2 days before the order date. The owed test holds.
  - Tiers: timing 40%, kind 20%, value 5% (647.99 is in the 500.00–<1000.00 band), credited haul-away 25.00 (one replacement/reimbursement settlement of the category that day, two old items).
  - Credit 25.00 × 90% = **22.50**, unchanged. The earlier repairs are not the settlement read and do not count among same-day replacement or reimbursement settlements.
  - No order row of e6af873a… changed, so 41.85 / 72.15 / 39.65 are unchanged. GT expected values are unchanged.
- Persona: tasks/0.json user_scenario now says "the Northgate plan had the fridge repaired three times and, when it broke again this fall and that model was discontinued, paid you back with an eGift card". This is consistent with the new plan ledger.
- Note for the coordinator: `.audit_views/runtime/order_returns_and_price_adjustments/task0.runtime.json` (mtime 2026-10-24T13:58) still carries the old line "repaired it once last year". The audit view is stale against tasks/0.json. It is not a KB or seed defect, but it should be refreshed before any later blind audit.
- Verdict: **PASS**.

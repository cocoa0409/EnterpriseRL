# rework claims — order_returns_and_price_adjustments, round 2

All round-1 items were verified against the artifacts before any change; none is disputed.

| Round-1 item | Status | Location changed |
| --- | --- | --- |
| F1 (unreachable fall-throughs) | closed | order.extended.yaml: order_ext_missed_appointment_credit.northgate_moves_extra and order_ext_late_fee_goodwill_refund.goodwill_moves_extra ladders now three-or-more / two / single move; order_ext_late_express_credit.lateness_rate_step now three-or-more / two / single day; express_price_extra replaced by age_check_extra_step (alcohol lines); order_ext_replacement_haul_away_credit.credited_haul_basis tiers now two-or-more items / one item charged below its pre-benefit amount / otherwise. Class swept over all factors; every ladder's three tiers are reachable inside its policy's scope. tasks/0.json and tasks/1.json worlds moved off each fall-through (two Northgate moves; two days late). |
| F2 (facts no record holds; edge conditions weaker than sentences) | closed | order_ext_late_fee_goodwill_refund rule (no move timing; record test "an order on which Northgate itself moved an appointment"); order_ext_replacement_haul_away_credit rule and replaced_by (record test "placed on or after the date of the customer's most recent Northgate Protect claim settlement"); order_ext_late_change_fee prerequisite edges B and C policy_source and condition rewritten to the same strength; tasks/0.json prerequisite_closure why_false and design_rationale. |
| F3 (goodwill cap vs base net-of-refund cap) | closed | order_ext_late_fee_goodwill_refund: acts on the most recent late-change fee row (tie: first recorded) and never exceeds that fee less refunds already booked against late-change fees. Class swept: order_ext_missed_appointment_credit, order_ext_replacement_haul_away_credit and order_ext_late_express_credit caps now use the fee standing (charged less refunds). |
| F4 (adjustment on the line vs whole-order read) | closed | order_ext_drive_up_return_refund scope (replaced_by and rule): every price adjustment on the order stands on the returned line; out of scope the base refund applies. |
| F5 (kept merchandise omits adjustments) | closed | removed with the small-order deduction (F7); order_ext_drive_up_return_refund no longer reads kept merchandise. |
| F6 (membership first-match read) | closed | order_ext_drive_up_return_refund no longer reads membership; its cross-category read is the Marketplace return ledger (customer-scoped count, no first match). |
| F7 (small-order deduction vs membership single statement) | closed | order_ext_drive_up_return_refund: small_order_deduction_step removed; new factor marketplace_return_addition (cross-difficulty market); tasks/1.json computations, tracing, read nodes (Marketplace holdings and events), seed (Marketplace order with a changed-mind and a defective return). |
| F8 (late_delivery_relief gated) | closed | order_ext_drive_up_return_refund baseline restocking is the standard ten percent for an electronics-class changed-mind Drive Up return (declared overwrite of the base refund sentence), so the relief moves the result alone; relief tiers are now multi-source. |
| F9 (zero-amount owed credits) | closed | de minimis record tests ("charged above zero") in the rules of order_ext_missed_appointment_credit, order_ext_replacement_haul_away_credit, order_ext_late_fee_goodwill_refund, order_ext_late_express_credit and in the policy_source and condition of all four prerequisite edges. |
| F10 (undeclared tender override) | closed | order_ext_drive_up_return_refund scope limited to orders paid with an external card alone with no Northgate Cash or gift card redeemed; the rule restates the refund tender rule for that case. |
| O1 (hard-coded external card) | closed | every fee-credit rule and the late-change rule now name the external payment card and route any other tender to the refund tender rule. |
| O2 (gross caps) | closed | see F3 class sweep. |
| O3 (reschedule before the cutoff unpriced) | closed | order_ext_late_change_fee overwrite and rule: free reschedules two or more days ahead carry no fee, every other reschedule carries this fee; compute carries the free-reschedule branch. |
| O4 (days ahead below zero) | closed (no change) | rule scope "down to the scheduled day itself" already excludes requests after the scheduled date. |
| O5 (lateness compensated twice) | closed (no change) | kept as a stated relief tier; noted in worklog as a company schedule choice. |
| O6 (waiting extra grows with booking delay) | closed | order_ext_missed_appointment_credit waiting extra counts to the scheduled date the order carries. |
| O7 (present request counted or not) | closed | order_ext_late_change_fee rule states the customer's requests already on the order, the request being made not counted. |
| T0 finding 1 (two solutions, goodwill timing) | closed | as F2; tasks/0.json closure and rationale. |
| T0 finding 2 (unreachable fall-throughs) | closed | as F1. |
| T0 finding 3 (no near-miss in the replacement credit) | closed | tasks/0.json initial_state: an older repair settlement on the same plan (the most-recent read excludes it); plan ledger kept consistent with plan_claim_settlement. |
| T0 finding 4 (seeded late-change fee not producible) | closed | tasks/0.json initial_state late-change fee row reseeded at the value the charter's late-change rule gives on that day's world (re-run recorded in worklog); order amount and seed_consistency updated. |
| T0 finding 5 (bought to replace) | closed | as F2. |
| T1 finding 1 (small-order deduction) | closed | as F7. |
| T1 finding 2 (late-express fall-throughs) | closed | as F1. |
| T1 finding 3 (relief gated) | closed | as F8. |

# premium_billing_and_grace — instantiate worklog

- Step 0: draw_counts --tasks 2 -> task 0 {prerequisite_problems 1, factor_counts [5,6]}; task 1 {prerequisite_problems 2, factor_counts [5,5,4]}.
- Constraint: billing_reinstate / billing_lapse / billing_binder_expired trigger dental/vision/dhmo events, so no tool writes them; customer-owned numeric writes are payments only.
- Task 0: vision termination credit (agent, 5 factors) -> grace-cure card payment (user, 6 factors); gold credit 57.11 (2026-08, 3 months), payment 232.12. Per-task gates green after two fixes (empty-string FKs -> null; unread provider rows dropped).
- Task 1: dental tier-difference credit (agent, 5) + rider credit (agent, 4) -> renewal card payment (user, 5); gold 171.99, 46.28, 975.80. Fixes: rc_months cross flag cleared; r_credit renamed r_giveback (substring of a tool name); rc_months given its own evidence binding.
- XF sweep (both tasks): transitive factor independence, verbatim compute_basis, decoy/absent probes, scoped overwrites, assembly cleanup (g_fshare -> g_relief, interest factors decide amounts, g_hold decides the held amount); values unchanged.
- Final block: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (branches mean 96.50, steps 14.00, history max 65, branch max 131), GROUNDING OK, SCOPE OK.
INSTANTIATE round 1: gates 7/7 green

## Rework round 2
- Policies regenerated from per-policy generators; worlds reseeded (task 0: out-of-network vision claims priced per Select 130, rule-produced prior vision credit, second returned bank payment and AutoPay removal to Direct Bill, held grace-cure check; task 1: departure moved to 2025-11-30 with rule-produced 2025-12-05 prior credits, no overpayment credit, no tier-change date, member_spouse vision applied after the stale renewal invoice, returned renewal check with fee). Removed: g_tol, dtc_basis, r_vtier, r_vstart, r_giveback. Added: vtc_feeback, rc_int, r_vbinder, r_fee, r_relief. Credit tools post against the coverage month of the invoice issued last (docstrings updated, format only).

### (a) Decoy / absent-record probes (scratch copies; gold vs probed result, or the named binding)
| policy | read | probe | gold | probed | moves | expected | ok |
|---|---|---|---|---|---|---|---|
| vision_term_credit | XLATEST vision_plans (subscriber, voluntary) | second record: earlier voluntary-terminated subscriber unit (2024-12-31) | 99.56 | 99.56 | no | no move | ok |
| vision_term_credit | XLATEST vision_plans (subscriber, voluntary) | cancelled: subscriber application withdrawn with a later date | 99.56 | 99.56 | no | no move | ok |
| vision_term_credit | XLATEST vision_plans (subscriber, voluntary) | absent: no voluntary-terminated subscriber unit | 99.56 | 0.00 | yes | moves | ok |
| vision_term_credit | LATEST invoice coverage_month | second record: same-day duplicate invoice recorded later for 2026-11 | 99.56 | 99.56 | no | no move | ok |
| vision_term_credit | XSUM vision_claims plan_paid | denied: DENIED_FREQUENCY exam inside the window | 99.56 | 99.56 | no | no move | ok |
| vision_term_credit | XSUM vision_claims plan_paid | prior benefit year: paid exam 2025-10-10, before the coverage effective date | 99.56 | 99.56 | no | no move | ok |
| vision_term_credit | XSUM vision_claims plan_paid | after termination: exam 2026-07-15 denied DENIED_NOT_ELIGIBLE | 99.56 | 99.56 | no | no move | ok |
| vision_term_credit | XSUM vision_claims plan_paid | after termination: paid service 2026-08-20 (outside the window) | 99.56 | 99.56 | no | no move | ok |
| vision_term_credit | XSUM vision_claims plan_paid | reversed: reverse the Mateo frame payment | 99.56 | 164.56 | yes | moves | ok |
| vision_term_credit | XLATEST vision_coverage_requests (unit, confirmed) | withdrawn: a later withdrawn termination request for the unit | 99.56 | 99.56 | no | no move | ok |
| vision_term_credit | XLATEST vision_coverage_requests (unit, confirmed) | second record: confirmed request on Tomas's enrollment, registered later | 99.56 | 99.56 | no | no move | ok |
| vision_term_credit | XLATEST vision_coverage_requests (unit, confirmed) | absent: no request | 99.56 | 79.56 | yes | moves | ok |
| grace_cure_payment | LATEST fee (last_fee) | prior year: returned-payment fee booked 2025-03-10 | 242.62 | 242.62 | no | no move | ok |
| grace_cure_payment | COUNT returns 24m (relief) | prior year: returned payment 2025-03-10 before the grace period | 242.62 | 315.12 | yes | moves | ok |
| grace_cure_payment | LATEST grace-cure check [held_amt] | second record: older grace-cure check 2026-09-02 | 20.00 | 20.00 | no | no move | ok |
| grace_cure_payment | LATEST invoice [last_amt] | second record: same-day invoice recorded later | 156.34 | 156.34 | no | no move | ok |
| grace_cure_payment | LATEST eft return months_covered=1 | decoy: one-time transfer return (months_covered 0) only | 242.62 | 0.00 | yes | moves | ok |
| dental_tier_credit | XLATEST dental_plans (LOE) | second record: earlier LOE dependent (2023-06-30, tier family) | 682.15 | 682.15 | no | no move | ok |
| dental_tier_credit | XLATEST dental_plans (subscriber, active) | cancelled: subscriber row cancelled with later effective date | 682.15 | 682.15 | no | no move | ok |
| dental_tier_credit | XLATEST dental_plans (LOE) | absent: no LOE dependent | 682.15 | 0.00 | yes | moves | ok |
| dental_tier_credit | LATEST invoice | second record: same-day invoice recorded later with lower amount | 682.15 | 682.15 | no | no move | ok |
| rider_end_credit | XLATEST ortho_riders (terminated) | cancelled: withdrawn rider application (seeded decoy) with a later date | 174.77 | 174.77 | no | no move | ok |
| rider_end_credit | XLATEST ortho_riders (terminated) | second record: earlier terminated rider 2024-06-30 | 174.77 | 174.77 | no | no move | ok |
| rider_end_credit | XLATEST ortho_riders (terminated) | absent: no terminated rider | 174.77 | 0.00 | yes | moves | ok |
| rider_end_credit | XLATEST vision_plans (subscriber, not terminated) | terminated: older voluntary-terminated subscriber vision row | 174.77 | 174.77 | no | no move | ok |
| renewal_payment | XLATEST vision_plans (subscriber, not terminated) | cancelled: withdrawn subscriber application effective later | 337.15 | 337.15 | no | no move | ok |
| renewal_payment | XLATEST vision_plans (subscriber, not terminated) | absent: no subscriber vision row | 337.15 | 14.94 | yes | moves | ok |
| renewal_payment | LATEST fee | prior year: fee 2025-02-14 for an older return | 337.15 | 337.15 | no | no move | ok |
| renewal_payment | XLATEST dental_plans (LOE) | second record: earlier LOE dependent | 337.15 | 337.15 | no | no move | ok |
| renewal_payment | XLATEST ortho_riders (terminated) | second record: earlier terminated rider | 337.15 | 337.15 | no | no move | ok |
| renewal_payment | LATEST invoice | base-priced invoice: renewal invoice at the in-force composition (1254.41) | 337.15 | 659.36 | yes | moves | ok |
fails 0

### (b) All-pairs method-shape table (each tier's formula evaluated on a world in every tier's domain)
| method factor | world in the domain of | T1 formula | T2 formula | T3 formula | own tier differs from every other tier there |
|---|---|---|---|---|---|
| vtc_offset | T1 | 79.76 | -65.36 | 0 | yes |
| vtc_offset | T2 | -33.04 | 44.64 | 0 | yes |
| vtc_offset | T3 | -888.4 | -235.36 | 0 | yes |
| g_next | T1 | 156.34 | 0.0 | 0 | yes |
| g_next | T2 | 156.34 | 1.0 | 0 | yes |
| g_next | T3 | 156.34 | 1.0 | 0 | yes |
| dtc_window / rc_months | T1 | 13 | 12 | 25 | yes |
| dtc_window / rc_months | T2 | 2 | 3 | 4 | yes |
| dtc_window / rc_months | T3 | 3 | 3 | 4 | yes |
| r_vbinder | T1 | 322.2144 | 26.8512 | 0 | yes |
| r_vbinder | T2 | 322.2144 | 26.8512 | 0 | yes |
| r_vbinder | T3 | 322.2144 | 26.8512 | 0 | yes |
Shape notes (XF-15): vtc_offset T1 subtracts premium x the unit's coverage months, T2 subtracts 12 x premium over the twelve-month-capped sum (T1 adds the tenure input); g_next T1 adds the invoice amount, T2 the arrangement's AutoPay discount (different inputs); dtc_window / rc_months read the paid-through date, the credit date and the invoice issued last respectively; r_vbinder T1 multiplies by the invoice's months covered, T2 takes one month.

### (c) Mechanical transitive factor-independence check (bindings closure over the compute graph; assembly happens only in result)
| policy | factor | owned bindings | transitive reads of other factors' bindings | plain bindings reading it | verdict |
|---|---|---|---|---|---|
| vision_term_credit | vtc_month | annual_12, draft_rets_12, drafts_12, vtc_month | none | none | ok |
| vision_term_credit | vtc_offset | after_window, ben_12, ben_unit, cov_window, vtc_offset | none | none | ok |
| vision_term_credit | vtc_prior | prior_change, prior_term, vtc_prior | none | none | ok |
| vision_term_credit | vtc_int | days_late, vtc_int | none | none | ok |
| vision_term_credit | vtc_recover | req_date, req_lead, vtc_recover | none | none | ok |
| vision_term_credit | vtc_feeback | err_rets, vtc_feeback | none | none | ok |
| grace_cure_payment | g_next | cures_12, draft_ret_in_grace, g_next, last_draft_ret | none | none | ok |
| grace_cure_payment | g_disc | bank_rets_12, cure_in_grace, drafts_hist, g_disc, last_cure_pay | none | none | ok |
| grace_cure_payment | g_fee | fees_grace, g_fee, rets_12 | none | none | ok |
| grace_cure_payment | g_relief | g_relief, open_months, rets_before | none | none | ok |
| grace_cure_payment | g_hold | any_ret, g_hold, hc_amt, hc_date, he_amt, he_date, held_amt, last_ret_any, pick_check, ret_days | none | none | ok |
| dental_tier_credit | dtc_window | annual_12w, dtc_window | none | none | ok |
| dental_tier_credit | dtc_dup | dtc_dup, prior_change, prior_term | none | none | ok |
| dental_tier_credit | dtc_int | dtc_int, lag_days | none | none | ok |
| dental_tier_credit | dtc_recover | billed_old, dtc_recover, rebill_days | none | none | ok |
| rider_end_credit | rc_months | annual_12m, rc_months | none | none | ok |
| rider_end_credit | rc_basis | annual_12r, draft_rets_12r, drafts_12r, rc_basis | none | none | ok |
| rider_end_credit | rc_dup | prior_rprepay, prior_rterm, rc_dup | none | none | ok |
| rider_end_credit | rc_int | rc_int, rlag_days | none | none | ok |
| rider_end_credit | rc_recover | bills_rider, cd_plan, cd_rate, cd_tier, cv_plan, cv_rate, cv_tier, rc_recover, rebill_r | none | none | ok |
| renewal_payment | r_dental | bills_old, dd_end, dd_old, dd_tier, r_dental, tier_diff | none | none | ok |
| renewal_payment | r_rider | bills_rider, r_rider, rr_end, rr_plan, rr_rate | none | none | ok |
| renewal_payment | r_vbinder | r_vbinder, v_after, v_app, v_eff | none | none | ok |
| renewal_payment | r_fee | fees_inv, r_fee, rets_12 | none | none | ok |
| renewal_payment | r_relief | open_months, r_relief, rets_inv, rets_lb | none | none | ok |

### (d) compute_basis quote sweep
quote sweep: every compute_basis value of the 5 policies is a verbatim substring of its rule; failures=0

### (e) Trigger rule
- billing_premium_credit (book_vision_term_credit_956578a0, book_dental_tier_credit_2a6e4a9b, book_rider_end_credit_fb22198c) -> base triggers: billing:billing_paid_through_update (same category).
- billing_payment_received (submit_grace_cure_payment_5521c4c8, submit_renewal_payment_53926ce3) -> base triggers: billing:billing_paid_through_update (same category).
- billing_paid_through_update -> no triggers. No tool writes billing_reinstate, billing_lapse or billing_binder_expired (they book dental/vision/dhmo rows).

### Gate block
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 63/63, 1.json 19/19 closure match); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
REWORK round 2 claims: C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, T0-F1, T0-F2, T0-F3, T0-F4, T0-F5, T0-F6, T0-O1, T0-O2, T0-O3, T1-F1, T1-F2, T1-F3, T1-F4, T1-F5, T1-F6, T1-F7, T1-F8, O-T1-1, O-T1-2, O-T1-3
REWORK round 2: gates 7/7 green

## Rework round 3
- Edits in place on billing.extended.yaml (scripted, per policy) and on the task files; worlds unchanged. VTC: AutoPay tier read from the arrangement record; vtc_feeback removed; new method vtc_window (prepaid / begun / billed months), months covered = months counted less months already credited. GCP: g_disc and g_fee read 'left AutoPay' from the arrangement record; g_fee tiers follow the arrangement (left AutoPay / no AutoPay discount / drafts); automatic draft = returned bank draft that paid 1, 3 or 12 months; a returned grace-cure payment is never held. DTC / REC / RNP: what the renewal invoice billed is read by pricing the plans it could bill and testing equality to the cent (former tier / ended rider priced in), vision applied after the invoice never priced; DTC and REC months covered follow their months factor; REC one shared annual-invoice binding and AutoPay tier from the arrangement record; RNP r_vbinder tier 2 = months from start through the renewal year's end at the monthly premium without the prepay discount; r_fee tiers follow the arrangement. Draw kept: task 0 [5,6], task 1 [5,5,4].

### (a) Decoy / absent-record probes (scratch copies; gold vs probed result, or the named binding)
| policy | read | probe | gold | probed | moves | expected | ok |
|---|---|---|---|---|---|---|---|
| vision_term_credit | XLATEST vision_plans (subscriber, voluntary) | second record: earlier voluntary-terminated subscriber unit | 38.62 | 38.62 | no | no move | ok |
| vision_term_credit | XLATEST vision_plans (subscriber, voluntary) | cancelled: withdrawn subscriber application dated later | 38.62 | 38.62 | no | no move | ok |
| vision_term_credit | XLATEST vision_plans (subscriber, voluntary) | absent: no voluntary-terminated unit | 38.62 | 0.0 | yes | moves | ok |
| vision_term_credit | LATEST invoice coverage_month | second record: same-day invoice recorded later | 38.62 | 38.62 | no | no move | ok |
| vision_term_credit | XSUM vision_claims plan_paid | denied: DENIED_FREQUENCY exam in the window | 38.62 | 38.62 | no | no move | ok |
| vision_term_credit | XSUM vision_claims plan_paid | prior benefit year: paid exam 2025-10-10 | 38.62 | 38.62 | no | no move | ok |
| vision_term_credit | XSUM vision_claims plan_paid | after termination: paid service 2026-08-20 | 38.62 | 38.62 | no | no move | ok |
| vision_term_credit | XSUM vision_claims plan_paid | reversed: reversal of the Mateo frame | 38.62 | 103.62 | yes | moves | ok |
| vision_term_credit | XLATEST vision_coverage_requests (unit) | withdrawn: later withdrawn request for the unit | 38.62 | 38.62 | no | no move | ok |
| vision_term_credit | XLATEST vision_coverage_requests (unit) | second record: confirmed request on Tomas's enrollment | 38.62 | 38.62 | no | no move | ok |
| vision_term_credit | XLATEST vision_coverage_requests (unit) | absent: no request | 38.62 | 18.62 | yes | moves | ok |
| vision_term_credit | AutoPay record [ap_record] | C13: arrangement Quarterly Bill (accepts eft, no AutoPay discount) | 1 | 0 | yes | moves | ok |
| grace_cure_payment | LATEST fee | prior year: fee 2025-03-10 | 303.56 | 303.56 | no | no move | ok |
| grace_cure_payment | COUNT returns 24m (relief) | prior year: return 2025-03-10 before the grace period | 303.56 | 376.06 | yes | moves | ok |
| grace_cure_payment | held payment [held_amt] | C10-r2: no 09-19 check, so the latest transfer is the returned 60.00 | 20.0 | 0 | yes | moves | ok |
| grace_cure_payment | held payment [he_ok] | C10-r2: the returned 60.00 transfer is never held | 0 | 0 | no | no move | ok |
| grace_cure_payment | held payment [held_amt] | second record: older unreturned grace-cure check 2026-09-02 | 20.0 | 20.0 | no | no move | ok |
| grace_cure_payment | LATEST invoice [last_amt] | second record: same-day invoice recorded later | 156.34 | 156.34 | no | no move | ok |
| grace_cure_payment | automatic draft [draft_ret_in_grace] | C9-r2 iii: draft that paid 3 months (quarterly) returned in grace | 1 | 1 | no | no move | ok |
| grace_cure_payment | automatic draft [draft_ret_in_grace] | decoy: only the one-time transfer return (paid no month) | 1 | 0 | yes | moves | ok |
| grace_cure_payment | left AutoPay [left_ap] | C9-r2 i / C13: arrangement Quarterly Bill | 1 | 0 | yes | moves | ok |
| dental_tier_credit | XLATEST dental_plans (LOE) | second record: earlier LOE dependent | 682.15 | 682.15 | no | no move | ok |
| dental_tier_credit | XLATEST dental_plans (subscriber, active) | cancelled: subscriber row cancelled, later effective date | 682.15 | 682.15 | no | no move | ok |
| dental_tier_credit | XLATEST dental_plans (LOE) | absent: no LOE dependent | 682.15 | 0.0 | yes | moves | ok |
| dental_tier_credit | invoice reading [billed_old] | C3-r2: correctly priced invoice with active rider and family vision | 1 | 0 | yes | moves | ok |
| rider_end_credit | XLATEST ortho_riders (terminated) | cancelled: seeded withdrawn application (no change) | 174.77 | 174.77 | no | no move | ok |
| rider_end_credit | XLATEST ortho_riders (terminated) | second record: earlier terminated rider | 174.77 | 174.77 | no | no move | ok |
| rider_end_credit | XLATEST ortho_riders (terminated) | absent: no terminated rider | 174.77 | 0.0 | yes | moves | ok |
| rider_end_credit | invoice reading [bills_rider] | C3-r2: vision applied after the invoice is not priced (family tier) | 1 | 1 | no | no move | ok |
| rider_end_credit | invoice reading [bills_rider] | C3-r2: correctly priced invoice | 1 | 0 | yes | moves | ok |
| rider_end_credit | AutoPay record [ap_record_r] | C13 / P2-a: annual payments made by eft | 0 | 0 | no | no move | ok |
| renewal_payment | XLATEST vision_plans (subscriber, not terminated) | cancelled: withdrawn application effective later | 337.15 | 337.15 | no | no move | ok |
| renewal_payment | XLATEST vision_plans (subscriber, not terminated) | absent: no subscriber vision row | 337.15 | 14.94 | yes | moves | ok |
| renewal_payment | LATEST fee | prior year: fee 2025-02-14 | 337.15 | 337.15 | no | no move | ok |
| renewal_payment | XLATEST dental_plans (LOE) | second record: earlier LOE dependent | 337.15 | 337.15 | no | no move | ok |
| renewal_payment | XLATEST ortho_riders (terminated) | second record: earlier terminated rider | 337.15 | 337.15 | no | no move | ok |
| renewal_payment | invoice reading [bills_old] | C3-r2 / P2-d: correctly priced invoice | 1 | 0 | yes | moves | ok |
| renewal_payment | invoice reading [bills_rider] | C3-r2: correctly priced invoice | 1 | 0 | yes | moves | ok |
| renewal_payment | fee tier [r_fee] | C13: annual payments made by eft (no AutoPay record) | 25.0 | 25.0 | no | no move | ok |
fails 0

### (b) All-pairs method-shape table
| method factor | world in the domain of | T1 formula | T2 formula | T3 formula | own tier differs from every other tier there |
|---|---|---|---|---|---|
| vtc_offset | T1 | 79.76 | -65.36 | 0 | yes |
| vtc_offset | T2 | -33.04 | 44.64 | 0 | yes |
| vtc_offset | T3 | -888.4 | -235.36 | 0 | yes |
| g_next | T1 | 156.34 | 0.0 | 0 | yes |
| g_next | T2 | 156.34 | 1.0 | 0 | yes |
| g_next | T3 | 156.34 | 1.0 | 0 | yes |
| vtc_window | T1 | 13 | 12 | 25 | yes |
| vtc_window | T2 | 2 | 3 | 4 | yes |
| vtc_window | T3 | 3 | 3 | 4 | yes |
| dtc_window | T1 | 13 | 12 | 25 | yes |
| dtc_window | T2 | 2 | 3 | 4 | yes |
| dtc_window | T3 | 3 | 3 | 4 | yes |
| rc_months | T1 | 13 | 12 | 25 | yes |
| rc_months | T2 | 2 | 3 | 4 | yes |
| rc_months | T3 | 3 | 3 | 4 | yes |
| r_vbinder | T1 | 322.2144 | 335.64 | 0 | yes |
| r_vbinder | T2 | 322.2144 | 251.73 | 0 | yes |
| r_vbinder | T3 | 322.2144 | 531.43 | 0 | yes |
Shape notes (XF-15): vtc_window / dtc_window / rc_months read the paid-through date, the credit date and the invoice issued last respectively; vtc_offset T1 adds the tenure input; g_next T1 the invoice amount, T2 the arrangement's AutoPay discount; r_vbinder T1 uses the prepay tariff, T2 the plan's start date (data-selected month count) at the undiscounted premium.

### (c) Mechanical transitive factor-independence check
| policy | factor | owned bindings | transitive reads of other factors' bindings | plain bindings reading it | verdict |
|---|---|---|---|---|---|
| vision_term_credit | vtc_month | ap_record, drafts_12, vtc_month | none | none | ok |
| vision_term_credit | vtc_window | book_months, vtc_window | none | none | ok |
| vision_term_credit | vtc_offset | after_window, ben_12, ben_unit, cov_window, vtc_offset | none | none | ok |
| vision_term_credit | vtc_prior | prior_change, prior_term, vtc_prior | none | none | ok |
| vision_term_credit | vtc_int | days_late, vtc_int | none | none | ok |
| vision_term_credit | vtc_recover | req_date, req_lead, vtc_recover | none | none | ok |
| grace_cure_payment | g_next | cures_12, draft_ret_in_grace, g_next, last_draft_ret | none | none | ok |
| grace_cure_payment | g_disc | bank_rets_12, cure_in_grace, g_disc, last_cure_pay | none | none | ok |
| grace_cure_payment | g_fee | fees_12, fees_grace, g_fee | none | none | ok |
| grace_cure_payment | g_relief | g_relief, open_months, rets_before | none | none | ok |
| grace_cure_payment | g_hold | any_ret, g_hold, hc_amt, hc_date, hc_ok, he_amt, he_date, he_ok, held_amt, last_ret_any, pick_check, rc_amt, rc_date, re_amt, re_date, ret_days | none | none | ok |
| dental_tier_credit | dtc_window | annual_12w, book_months, dtc_window | none | none | ok |
| dental_tier_credit | dtc_dup | dtc_dup, prior_change, prior_term | none | none | ok |
| dental_tier_credit | dtc_int | dtc_int, lag_days | none | none | ok |
| dental_tier_credit | dtc_recover | billed_old, d_act_r, d_c_both, d_c_old, d_span, d_vinv, dr_plan, dr_rate, dtc_recover, dv_app, dv_plan, dv_tier, rebill_days | none | none | ok |
| rider_end_credit | rc_months | book_months, rc_months | none | none | ok |
| rider_end_credit | rc_basis | ap_record_r, drafts_12r, rc_basis | none | none | ok |
| rider_end_credit | rc_dup | prior_rprepay, prior_rterm, rc_dup | none | none | ok |
| rider_end_credit | rc_int | rc_int, rlag_days | none | none | ok |
| rider_end_credit | rc_recover | bills_rider, cd_plan, cd_rate, cd_tier, cv_app, cv_plan, cv_tier, q_act_r, q_c_both, q_c_rid, q_span, q_vinv, qd_old, qd_tier, rc_recover, rebill_r | none | none | ok |
| renewal_payment | r_dental | bills_old, dd_end, r_dental, tier_diff | none | none | ok |
| renewal_payment | r_rider | bills_rider, r_rider, rr_end | none | none | ok |
| renewal_payment | r_vbinder | r_vbinder, v_after, v_eff | none | none | ok |
| renewal_payment | r_fee | drafts_12, fees_12, left_ap, r_fee | none | none | ok |
| renewal_payment | r_relief | open_months, r_relief, rets_inv, rets_lb | none | none | ok |

### (d) compute_basis quote sweep
sweep: compute_basis quotes verbatim, one owner per binding, no duplicated selection expression; failures=0

### (e) Trigger rule
- billing_premium_credit (book_vision_term_credit_956578a0, book_dental_tier_credit_2a6e4a9b, book_rider_end_credit_fb22198c) -> billing:billing_paid_through_update (same category).
- billing_payment_received (submit_grace_cure_payment_5521c4c8, submit_renewal_payment_53926ce3) -> billing:billing_paid_through_update (same category).
- billing_paid_through_update -> no triggers; no tool writes billing_reinstate, billing_lapse or billing_binder_expired.

### Gate block
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
REWORK round 3 claims: C3-r2, C6-r2, C7-r2, C9-r2, C10-r2, C12, C13, T0-R2-F1, T0-R2-O1, T1-R2-F1, T1-R2-F2
REWORK round 3: gates 7/7 green

## Rework round 4
- In-place scripted edits; worlds unchanged. C12-r3: r_fee removed (RNP standard = full balance due, fees included; r_relief waives by tenure); new DTC factor dtc_basis (prepay rate / exchange APTC net difference / filed difference) keeps the draw [5,5,4] with tiers reachable in DTC's scope. C3-r3: the invoice reading in DTC, REC and RNP prices the subscriber's dental plan, every active or applied rider (riders of one plan applied after the invoice's date, i.e. on that plan's latest application date when later than the invoice, left out), the subscriber's DHMO and vision enrollments when applied on or before the invoice's date. C10-r3: held payment = later of the latest grace-cure check and the latest grace-cure transfer that no returned payment names (original_billing_txn_id), never substituting an earlier one. T0-R3-O1: VTC's standard counts billed months that have begun; vtc_window counts every billed month when the account is in grace with its automatic draft returned in it (the case in which GCP collects the invoice issued last), prepaid months on prepay; task 0 values move accordingly (prior 2026-07-08 credit still reproduced).

### (a) Decoy / absent-record probes (scratch copies; gold vs probed result or named binding; seed checks replay the rule on the ledger of the booking date)
| policy | read | probe | gold | probed | moves | expected | ok |
|---|---|---|---|---|---|---|---|
| vision_term_credit | XLATEST vision_plans (subscriber, voluntary) | second record: earlier voluntary-terminated subscriber unit | 74.56 | 74.56 | no | no move | ok |
| vision_term_credit | XLATEST vision_plans (subscriber, voluntary) | cancelled: withdrawn subscriber application dated later | 74.56 | 74.56 | no | no move | ok |
| vision_term_credit | XLATEST vision_plans (subscriber, voluntary) | absent: no voluntary-terminated unit | 74.56 | 0.0 | yes | moves | ok |
| vision_term_credit | LATEST invoice coverage_month | second record: same-day invoice recorded later | 74.56 | 74.56 | no | no move | ok |
| vision_term_credit | XSUM vision_claims plan_paid | denied: DENIED_FREQUENCY exam in the window | 74.56 | 74.56 | no | no move | ok |
| vision_term_credit | XSUM vision_claims plan_paid | prior benefit year: paid exam 2025-10-10 | 74.56 | 74.56 | no | no move | ok |
| vision_term_credit | XSUM vision_claims plan_paid | after termination: paid service 2026-08-20 | 74.56 | 74.56 | no | no move | ok |
| vision_term_credit | XSUM vision_claims plan_paid | reversed: reversal of the Mateo frame | 74.56 | 139.56 | yes | moves | ok |
| vision_term_credit | XLATEST vision_coverage_requests (unit) | withdrawn: later withdrawn request for the unit | 74.56 | 74.56 | no | no move | ok |
| vision_term_credit | XLATEST vision_coverage_requests (unit) | second record: confirmed request on Tomas's enrollment | 74.56 | 74.56 | no | no move | ok |
| vision_term_credit | XLATEST vision_coverage_requests (unit) | absent: no request | 74.56 | 54.56 | yes | moves | ok |
| vision_term_credit | months counted [vtc_window] | T0-R3-O1: no draft returned in the grace period (only the transfer return) -> begun months | 4 | 3 | yes | moves | ok |
| vision_term_credit | seed check [result] | prior credit: ledger as of 2026-07-08 gives the seeded 10.00 | 74.56 | 10.0 | yes | moves | ok |
| grace_cure_payment | LATEST fee | prior year: fee 2025-03-10 | 267.62 | 267.62 | no | no move | ok |
| grace_cure_payment | held payment [held_amt] | C10-r3 / P3-b: returned transfer A and unreturned same-amount transfer B (later) -> B held | 20.0 | 60.0 | yes | moves | ok |
| grace_cure_payment | held payment [held_amt] | C10-r3 / P3-c: unreturned 30.00 before the returned 60.00 -> set aside, no substitute, nothing held | 20.0 | 0 | yes | moves | ok |
| grace_cure_payment | held payment [he_ok] | returned transfer is set aside (matched by original_billing_txn_id) | False | False | no | no move | ok |
| grace_cure_payment | LATEST invoice [last_amt] | second record: same-day invoice recorded later | 156.34 | 156.34 | no | no move | ok |
| grace_cure_payment | automatic draft [draft_ret_in_grace] | draft that paid 3 months returned in grace | True | True | no | no move | ok |
| grace_cure_payment | left AutoPay [left_ap] | arrangement Quarterly Bill | True | False | yes | moves | ok |
| dental_tier_credit | XLATEST dental_plans (LOE) | second record: earlier LOE dependent | 682.15 | 682.15 | no | no move | ok |
| dental_tier_credit | XLATEST dental_plans (LOE) | absent: no LOE dependent | 682.15 | 0.0 | yes | moves | ok |
| dental_tier_credit | invoice reading [billed_old] | C3: correctly priced invoice (active rider, family vision applied before it) | True | False | yes | moves | ok |
| dental_tier_credit | invoice reading [billed_old] | C3-r3 / P3-a: applied child rider billed with the stale family tier | True | True | no | no move | ok |
| dental_tier_credit | invoice reading [billed_old] | C3-r3: rider applied after the invoice is left out | True | True | no | no move | ok |
| dental_tier_credit | invoice reading [billed_old] | C3-r3: DHMO enrollment funded by the account billed with the stale tier | True | True | no | no move | ok |
| dental_tier_credit | basis [month_diff] | exchange account with APTC 30.00 (no prepay) | 48.24 | 50.25 | yes | moves | ok |
| dental_tier_credit | seed check [result] | prior credit: ledger as of 2025-12-05 gives the seeded 48.24 | 682.15 | 48.24 | yes | moves | ok |
| rider_end_credit | XLATEST ortho_riders (terminated) | second record: earlier terminated rider | 174.77 | 174.77 | no | no move | ok |
| rider_end_credit | XLATEST ortho_riders (terminated) | absent: no terminated rider | 174.77 | 0.0 | yes | moves | ok |
| rider_end_credit | invoice reading [bills_rider] | vision applied after the invoice is not priced | True | True | no | no move | ok |
| rider_end_credit | invoice reading [bills_rider] | C3-r3 / P3-a analogue | True | True | no | no move | ok |
| rider_end_credit | invoice reading [bills_rider] | correctly priced invoice | True | False | yes | moves | ok |
| rider_end_credit | seed check [result] | prior credit: ledger as of 2025-12-05 gives the seeded 12.10 | 174.77 | 12.1 | yes | moves | ok |
| renewal_payment | XLATEST vision_plans (subscriber, not terminated) | absent: no subscriber vision row | 337.15 | 14.94 | yes | moves | ok |
| renewal_payment | LATEST fee | prior year: fee 2025-02-14 | 337.15 | 362.15 | yes | moves | ok |
| renewal_payment | invoice reading [bills_old] | correctly priced invoice | True | False | yes | moves | ok |
| renewal_payment | invoice reading [bills_old] | C3-r3 / P3-a: applied child rider billed with the stale family tier | True | True | no | no move | ok |
| renewal_payment | invoice reading [bills_rider] | C3-r3: DHMO enrollment billed with the stale composition | True | True | no | no move | ok |
fails 0

### (b) All-pairs method-shape table
| method factor | world in the domain of | T1 formula | T2 formula | T3 formula | own tier differs from every other tier there |
|---|---|---|---|---|---|
| vtc_offset | T1 | 79.76 | -65.36 | 0 | yes |
| vtc_offset | T2 | -33.04 | 44.64 | 0 | yes |
| vtc_offset | T3 | -888.4 | -235.36 | 0 | yes |
| vtc_window | T1 | 6 | 7 | 3 | yes |
| vtc_window | T2 | 2 | 4 | 3 | yes |
| vtc_window | T3 | 5 | 6 | 3 | yes |
| g_next | T1 | 156.34 | 0.0 | 0 | yes |
| g_next | T2 | 156.34 | 1.0 | 0 | yes |
| g_next | T3 | 156.34 | 1.0 | 0 | yes |
| dtc_window | T1 | 13 | 12 | 25 | yes |
| dtc_window | T2 | 2 | 3 | 4 | yes |
| dtc_window | T3 | 3 | 3 | 4 | yes |
| rc_months | T1 | 13 | 12 | 25 | yes |
| rc_months | T2 | 2 | 3 | 4 | yes |
| rc_months | T3 | 3 | 3 | 4 | yes |
| r_vbinder | T1 | 322.2144 | 335.64 | 0 | yes |
| r_vbinder | T2 | 322.2144 | 251.73 | 0 | yes |
| r_vbinder | T3 | 322.2144 | 531.43 | 0 | yes |
Shape notes (XF-15): vtc_window T1 reads the paid-through date, T2 the invoice issued last, T3 the credit date capped by the billed months; dtc_window / rc_months as before; vtc_offset T1 adds the tenure input; g_next T1 invoice amount vs T2 AutoPay discount; r_vbinder T1 prepay tariff vs T2 the plan's start date at the undiscounted premium.

### (c) Mechanical transitive factor-independence check
| policy | factor | owned bindings | transitive reads of other factors' bindings | plain bindings reading it | verdict |
|---|---|---|---|---|---|
| vision_term_credit | vtc_month | ap_record, drafts_12, vtc_month | none | none | ok |
| vision_term_credit | vtc_window | book_months, v_draft_in_grace, v_draft_ret, vtc_window | none | none | ok |
| vision_term_credit | vtc_offset | after_window, ben_12, ben_unit, cov_window, vtc_offset | none | none | ok |
| vision_term_credit | vtc_prior | prior_change, prior_term, vtc_prior | none | none | ok |
| vision_term_credit | vtc_int | days_late, vtc_int | none | none | ok |
| vision_term_credit | vtc_recover | req_date, req_lead, vtc_recover | none | none | ok |
| grace_cure_payment | g_next | cures_12, draft_ret_in_grace, g_next, last_draft_ret | none | none | ok |
| grace_cure_payment | g_disc | bank_rets_12, cure_in_grace, g_disc, last_cure_pay | none | none | ok |
| grace_cure_payment | g_fee | fees_12, fees_grace, g_fee | none | none | ok |
| grace_cure_payment | g_relief | g_relief, open_months, rets_before | none | none | ok |
| grace_cure_payment | g_hold | any_ret, g_hold, hc_amt, hc_date, hc_id, hc_ok, he_amt, he_date, he_id, he_ok, held_amt, last_ret_any, pick_check, ret_days | none | none | ok |
| dental_tier_credit | dtc_basis | aptc, month_diff, net_new, net_old | none | none | ok |
| dental_tier_credit | dtc_window | book_months, dtc_window | none | none | ok |
| dental_tier_credit | dtc_dup | dtc_dup, prior_change, prior_term | none | none | ok |
| dental_tier_credit | dtc_int | dtc_int, lag_days | none | none | ok |
| dental_tier_credit | dtc_recover | billed_old, d_act_r, d_c_both, d_c_old, d_dh_app, d_dh_plan, d_dh_rate, d_dh_tier, d_span, d_vinv, dr_plan, dr_rate, dtc_recover, dv_app, dv_plan, dv_tier, rebill_days | none | none | ok |
| rider_end_credit | rc_months | book_months, rc_months | none | none | ok |
| rider_end_credit | rc_basis | ap_record_r, drafts_12r, rc_basis | none | none | ok |
| rider_end_credit | rc_dup | prior_rprepay, prior_rterm, rc_dup | none | none | ok |
| rider_end_credit | rc_int | rc_int, rlag_days | none | none | ok |
| rider_end_credit | rc_recover | bills_rider, cd_plan, cd_rate, cd_tier, cv_app, cv_plan, cv_tier, q_act_r, q_c_both, q_c_rid, q_dh_app, q_dh_plan, q_dh_rate, q_dh_tier, q_span, q_vinv, qd_old, qd_tier, rc_recover, rebill_r | none | none | ok |
| renewal_payment | r_dental | bills_old, dd_end, r_dental, tier_diff | none | none | ok |
| renewal_payment | r_rider | bills_rider, r_rider, rr_end | none | none | ok |
| renewal_payment | r_vbinder | r_vbinder, v_after, v_eff | none | none | ok |
| renewal_payment | r_relief | open_months, r_relief, rets_inv, rets_lb | none | none | ok |

### (d) compute_basis quote sweep
sweep: compute_basis quotes verbatim, one owner per binding, no duplicated selection expression; failures=0

### (e) Trigger rule
- billing_premium_credit (book_vision_term_credit_956578a0, book_dental_tier_credit_2a6e4a9b, book_rider_end_credit_fb22198c) -> billing:billing_paid_through_update (same category).
- billing_payment_received (submit_grace_cure_payment_5521c4c8, submit_renewal_payment_53926ce3) -> billing:billing_paid_through_update (same category).
- billing_paid_through_update -> no triggers; no tool writes billing_reinstate, billing_lapse or billing_binder_expired.

### Gate block
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
REWORK round 4 claims: C12-r3, C3-r3, C10-r3, T1-R3-F1, T0-R3-O1
REWORK round 4: gates 7/7 green

## Rework round 5
- C3-r4 closed by the coordinator route: the rebuilt-invoice reading in DTC, REC and RNP is scoped by a self-naming sentence to accounts on which, for each rider plan, the applied riders were all applied on or before the invoice's date or all on one date (record-decidable: the plan's latest application date is not later than the invoice, or every applied rider of the plan carries that date); riders applied after the invoice's date are left out. Out of scope the invoice is not taken to have billed the former tier / ended rider: DTC and REC add no re-billing amount, RNP deducts neither saving (rule words == compute: the in-scope test gates bills_old / bills_rider). No scored value moved; combination sentences untouched.

### (a) Probes of the scoped reading (scratch copies, task 1 world)
| case | policy | in scope | bills test | amount | expected in scope | ok |
|---|---|---|---|---|---|---|
| P4-b: two Child 1500 riders applied 2026-11-18 and 2026-11-20 (two post-invoice dates) | dental_tier_credit | False | False | 0 | False | ok |
| P4-b: two Child 1500 riders applied 2026-11-18 and 2026-11-20 (two post-invoice dates) | rider_end_credit | False | False | 0 | False | ok |
| P4-b: two Child 1500 riders applied 2026-11-18 and 2026-11-20 (two post-invoice dates) | renewal_payment | False | False | 0 | False | ok |
| two riders of one plan applied together 2026-11-20 (one post-invoice date) | dental_tier_credit | True | True | 25.0 | True | ok |
| two riders of one plan applied together 2026-11-20 (one post-invoice date) | rider_end_credit | True | True | 10.0 | True | ok |
| two riders of one plan applied together 2026-11-20 (one post-invoice date) | renewal_payment | True | True | 578.88 | True | ok |
| one rider applied 2026-11-02 (before) and one 2026-11-20 (after) of one plan | dental_tier_credit | False | False | 0 | False | ok |
| one rider applied 2026-11-02 (before) and one 2026-11-20 (after) of one plan | rider_end_credit | False | False | 0 | False | ok |
| one rider applied 2026-11-02 (before) and one 2026-11-20 (after) of one plan | renewal_payment | False | False | 0 | False | ok |
| one rider applied 2026-11-02, invoice billed with it and the stale tier | dental_tier_credit | True | True | 25.0 | True | ok |
| one rider applied 2026-11-02, invoice billed with it and the stale tier | rider_end_credit | True | True | 10.0 | True | ok |
| one rider applied 2026-11-02, invoice billed with it and the stale tier | renewal_payment | True | True | 578.88 | True | ok |
fails 0
Earlier probe rows (round 4) are unchanged: task 1 has no applied rider, so every reading there is in scope.

### (b) All-pairs method-shape table: no method factor changed in round 5; the round-4 table stands.

### (c)/(d) Mechanical transitive factor-independence check and compute_basis quote sweep
| policy | factor | transitive reads of other factors' bindings | plain bindings reading it | verdict |
|---|---|---|---|---|
| vision_term_credit | vtc_month | none | none | ok |
| vision_term_credit | vtc_window | none | none | ok |
| vision_term_credit | vtc_offset | none | none | ok |
| vision_term_credit | vtc_prior | none | none | ok |
| vision_term_credit | vtc_int | none | none | ok |
| vision_term_credit | vtc_recover | none | none | ok |
| grace_cure_payment | g_next | none | none | ok |
| grace_cure_payment | g_disc | none | none | ok |
| grace_cure_payment | g_fee | none | none | ok |
| grace_cure_payment | g_relief | none | none | ok |
| grace_cure_payment | g_hold | none | none | ok |
| dental_tier_credit | dtc_basis | none | none | ok |
| dental_tier_credit | dtc_window | none | none | ok |
| dental_tier_credit | dtc_dup | none | none | ok |
| dental_tier_credit | dtc_int | none | none | ok |
| dental_tier_credit | dtc_recover | none | none | ok |
| rider_end_credit | rc_months | none | none | ok |
| rider_end_credit | rc_basis | none | none | ok |
| rider_end_credit | rc_dup | none | none | ok |
| rider_end_credit | rc_int | none | none | ok |
| rider_end_credit | rc_recover | none | none | ok |
| renewal_payment | r_dental | none | none | ok |
| renewal_payment | r_rider | none | none | ok |
| renewal_payment | r_vbinder | none | none | ok |
| renewal_payment | r_relief | none | none | ok |

sweep: compute_basis quotes verbatim, one owner per binding, no duplicated selection expression; failures=0

### (e) Trigger rule: unchanged (billing_premium_credit and billing_payment_received -> billing:billing_paid_through_update only).

### Gate block
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
REWORK round 5 claims: C3-r4
REWORK round 5: gates 7/7 green

## Rework round 6 (render pre-scan render_r1.md, findings 1-8)
- 1: GCP g_fee tier 2 (no AutoPay discount otherwise) now collects the returned-payment fee booked last when it counts as booked in the grace period (two-date DAYS test); the whole-month fee window is gone. 2, 3: GCP g_relief and RNP r_relief state their windows exactly as measured (anniversary-counted whole-month windows; a return just before the grace start / renewal invoice counts with the latter; one exactly at the lookback edge with neither). 4: the invoice reading in DTC/REC/RNP leaves out active riders applied after the invoice's date too; scope sentence covers active and applied riders of each plan separately. 5: vtc_window / dtc_window / rc_months state that an account with no paid-through date is taken under the following cases. 6: the departed dependent is the subscriber's child, spouse or domestic partner (compute filters enrollee_relationship; tie order child, spouse, domestic partner, then recorded first) in DTC, REC and RNP; r_dental's cross-difficulty flag dropped (its dependent read is shared). 7: DTC/REC invoice reading names the vision enrollment funded by the account. 8: REC states the tie rule for the subscriber's current dental tier. Whole class swept in all five policies; placement-only notes not changed. No scored value moved (every expected value, baseline and factor sensitivity recomputed and unchanged).

### (a) Probes of the changed reads (scratch copies)
| finding | read | probe | value | expected | ok |
|---|---|---|---|---|---|
| 1 | GCP g_fee | Direct Bill never on AutoPay, only fee booked 2026-08-28 (before the 2026-09-01 grace start) -> not collected | 0 | 0 | ok |
| 2 | GCP rets_before | return dated exactly 24 whole months before the payment date counts in neither window (as stated) | 0 | 0 | ok |
| 4 | DTC billed_old | active rider applied 2026-11-20, after the 2026-11-17 invoice -> left out, invoice still read as billing the former tier | True | True | ok |
| 4 | RNP bills_rider | same world, renewal reading | True | True | ok |
| 6 | DTC dep_end | subscriber's own loss-of-eligibility row dated later is not the departed dependent | 2025-11-30 | 2025-11-30 | ok |
| 6 | REC qd_tier | spouse's loss of eligibility 2026-02-28 (later) is the departed dependent | member_spouse | member_spouse | ok |
| 5 | DTC dtc_window | prepay arrangement with no paid-through date -> next case (months billed after the drop) | 25 | 25 | ok |
fails 0
The round-4/5 probe tables stand for every other read (unchanged).

### (b) All-pairs method-shape table: no method formula changed in round 6; the round-4 table stands.

### (c)/(d) Mechanical transitive factor-independence check and compute_basis quote sweep
| policy | factor | transitive reads of other factors' bindings | plain bindings reading it | verdict |
|---|---|---|---|---|
| vision_term_credit | vtc_month | none | none | ok |
| vision_term_credit | vtc_window | none | none | ok |
| vision_term_credit | vtc_offset | none | none | ok |
| vision_term_credit | vtc_prior | none | none | ok |
| vision_term_credit | vtc_int | none | none | ok |
| vision_term_credit | vtc_recover | none | none | ok |
| grace_cure_payment | g_next | none | none | ok |
| grace_cure_payment | g_disc | none | none | ok |
| grace_cure_payment | g_fee | none | none | ok |
| grace_cure_payment | g_relief | none | none | ok |
| grace_cure_payment | g_hold | none | none | ok |
| dental_tier_credit | dtc_basis | none | none | ok |
| dental_tier_credit | dtc_window | none | none | ok |
| dental_tier_credit | dtc_dup | none | none | ok |
| dental_tier_credit | dtc_int | none | none | ok |
| dental_tier_credit | dtc_recover | none | none | ok |
| rider_end_credit | rc_months | none | none | ok |
| rider_end_credit | rc_basis | none | none | ok |
| rider_end_credit | rc_dup | none | none | ok |
| rider_end_credit | rc_int | none | none | ok |
| rider_end_credit | rc_recover | none | none | ok |
| renewal_payment | r_dental | none | none | ok |
| renewal_payment | r_rider | none | none | ok |
| renewal_payment | r_vbinder | none | none | ok |
| renewal_payment | r_relief | none | none | ok |

sweep: compute_basis quotes verbatim, one owner per binding, no duplicated selection expression; failures=0

### (e) Trigger rule: unchanged (billing_premium_credit and billing_payment_received -> billing:billing_paid_through_update only).

### Gate block
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
REWORK round 6 claims: render_r1-1, render_r1-2, render_r1-3, render_r1-4, render_r1-5, render_r1-6, render_r1-7, render_r1-8
REWORK round 6: gates 7/7 green

## Rework round 7 (KB audit KB-B0-1 / SRC-1)
- VTC: the unit is now defined as the vision charter's plan unit (every vision enrollment of the subscriber funded by the account, read from the terminated subscriber enrollment), and the vision benefits paid are the plan payments on the services of every enrollment in it. Since vision claims are read customer-wide, the offset is taken only when every vision enrollment the subscriber holds is funded by the account (new bindings v_all / v_acct owned by vtc_offset); otherwise no offset is deducted. Compute scope unchanged on every in-scope account; no scored value moved (all expected values, baselines and sensitivities recomputed and unchanged).
- Whose-records sweep over all five policies: every cross-category read is scoped to the billing account (rule: 'funded by the account' / 'the account funds') or to the unit's subscriber enrollment (termination request), except the vision claims and the subscriber-wide enrollment count, whose scope the rule now states; ledger reads are the account's own (holding-scoped).

### (a) Probes (scratch copies, task 0 world)
| probe | binding | gold | probed | expected |
|---|---|---|---|---|
| subscriber also holds a vision enrollment funded by another account | vtc_offset | 79.76 | 0 | no offset (0) |
| only the subscriber enrollment's own claims (household claims removed) | ben_unit | 370.0 | 45.0 | household claims counted: value falls |
| a paid service dated after the unit ended (2026-08-20) | ben_unit | 370.0 | 370.0 | outside the window: unchanged |

### Whose-records table (every cross-category read)
| policy | binding | cross read | scope in compute | scope in rule |
|---|---|---|---|---|
| vision_term_credit | vt_date | vision.vision_plans | billing account | funded by the account / the account funds |
| vision_term_credit | vt_eff | vision.vision_plans | billing account | funded by the account / the account funds |
| vision_term_credit | vt_pid | vision.vision_plans | billing account | funded by the account / the account funds |
| vision_term_credit | vt_tier | vision.vision_plans | billing account | funded by the account / the account funds |
| vision_term_credit | vt_plan | vision.vision_plans | billing account | funded by the account / the account funds |
| vision_term_credit | plan_units | ortho.ortho_riders | billing account | funded by the account / the account funds |
| vision_term_credit | v_all | vision.vision_plans | customer (subscriber) | the subscriber's vision claims / enrollments (stated) |
| vision_term_credit | v_acct | vision.vision_plans | billing account | funded by the account / the account funds |
| vision_term_credit | ben_unit | vision.vision_claims | customer (subscriber) | the subscriber's vision claims / enrollments (stated) |
| vision_term_credit | ben_12 | vision.vision_claims | customer (subscriber) | the subscriber's vision claims / enrollments (stated) |
| vision_term_credit | req_date | vision.vision_coverage_requests | unit enrollment | the unit's subscriber enrollment |
| dental_tier_credit | dl_e_child | dental.dental_plans | billing account | funded by the account / the account funds |
| dental_tier_credit | dl_t_child | dental.dental_plans | billing account | funded by the account / the account funds |
| dental_tier_credit | dl_e_spouse | dental.dental_plans | billing account | funded by the account / the account funds |
| dental_tier_credit | dl_t_spouse | dental.dental_plans | billing account | funded by the account / the account funds |
| dental_tier_credit | dl_e_domestic_partner | dental.dental_plans | billing account | funded by the account / the account funds |
| dental_tier_credit | dl_t_domestic_partner | dental.dental_plans | billing account | funded by the account / the account funds |
| dental_tier_credit | sub_tier | dental.dental_plans | billing account | funded by the account / the account funds |
| dental_tier_credit | sub_plan | dental.dental_plans | billing account | funded by the account / the account funds |
| dental_tier_credit | dr_plan | ortho.ortho_riders | billing account | funded by the account / the account funds |
| dental_tier_credit | dv_tier | vision.vision_plans | billing account | funded by the account / the account funds |
| dental_tier_credit | dv_plan | vision.vision_plans | billing account | funded by the account / the account funds |
| dental_tier_credit | dv_app | vision.vision_plans | billing account | funded by the account / the account funds |
| dental_tier_credit | d_act_r | ortho.ortho_riders | billing account | funded by the account / the account funds |
| dental_tier_credit | d_inscope | ortho.ortho_riders | billing account | funded by the account / the account funds |
| dental_tier_credit | d_dh_tier | dhmo.dhmo_plans | billing account | funded by the account / the account funds |
| dental_tier_credit | d_dh_plan | dhmo.dhmo_plans | billing account | funded by the account / the account funds |
| dental_tier_credit | d_dh_app | dhmo.dhmo_plans | billing account | funded by the account / the account funds |
| rider_end_credit | r_end | ortho.ortho_riders | billing account | funded by the account / the account funds |
| rider_end_credit | r_plan | ortho.ortho_riders | billing account | funded by the account / the account funds |
| rider_end_credit | plan_units | ortho.ortho_riders | billing account | funded by the account / the account funds |
| rider_end_credit | cd_tier | dental.dental_plans | billing account | funded by the account / the account funds |
| rider_end_credit | cd_plan | dental.dental_plans | billing account | funded by the account / the account funds |
| rider_end_credit | cv_tier | vision.vision_plans | billing account | funded by the account / the account funds |
| rider_end_credit | cv_plan | vision.vision_plans | billing account | funded by the account / the account funds |
| rider_end_credit | cv_app | vision.vision_plans | billing account | funded by the account / the account funds |
| rider_end_credit | qe_e_child | dental.dental_plans | billing account | funded by the account / the account funds |
| rider_end_credit | qe_t_child | dental.dental_plans | billing account | funded by the account / the account funds |
| rider_end_credit | qe_e_spouse | dental.dental_plans | billing account | funded by the account / the account funds |
| rider_end_credit | qe_t_spouse | dental.dental_plans | billing account | funded by the account / the account funds |
| rider_end_credit | qe_e_domestic_partner | dental.dental_plans | billing account | funded by the account / the account funds |
| rider_end_credit | qe_t_domestic_partner | dental.dental_plans | billing account | funded by the account / the account funds |
| rider_end_credit | q_act_r | ortho.ortho_riders | billing account | funded by the account / the account funds |
| rider_end_credit | q_inscope | ortho.ortho_riders | billing account | funded by the account / the account funds |
| rider_end_credit | q_dh_tier | dhmo.dhmo_plans | billing account | funded by the account / the account funds |
| rider_end_credit | q_dh_plan | dhmo.dhmo_plans | billing account | funded by the account / the account funds |
| rider_end_credit | q_dh_app | dhmo.dhmo_plans | billing account | funded by the account / the account funds |
| renewal_payment | rl_e_child | dental.dental_plans | billing account | funded by the account / the account funds |
| renewal_payment | rl_t_child | dental.dental_plans | billing account | funded by the account / the account funds |
| renewal_payment | rl_e_spouse | dental.dental_plans | billing account | funded by the account / the account funds |
| renewal_payment | rl_t_spouse | dental.dental_plans | billing account | funded by the account / the account funds |
| renewal_payment | rl_e_domestic_partner | dental.dental_plans | billing account | funded by the account / the account funds |
| renewal_payment | rl_t_domestic_partner | dental.dental_plans | billing account | funded by the account / the account funds |
| renewal_payment | ds_tier | dental.dental_plans | billing account | funded by the account / the account funds |
| renewal_payment | ds_plan | dental.dental_plans | billing account | funded by the account / the account funds |
| renewal_payment | rr_end | ortho.ortho_riders | billing account | funded by the account / the account funds |
| renewal_payment | rr_plan | ortho.ortho_riders | billing account | funded by the account / the account funds |
| renewal_payment | v_eff | vision.vision_plans | billing account | funded by the account / the account funds |
| renewal_payment | v_app | vision.vision_plans | billing account | funded by the account / the account funds |
| renewal_payment | v_tier | vision.vision_plans | billing account | funded by the account / the account funds |
| renewal_payment | v_plan | vision.vision_plans | billing account | funded by the account / the account funds |
| renewal_payment | act_r | ortho.ortho_riders | billing account | funded by the account / the account funds |
| renewal_payment | inscope | ortho.ortho_riders | billing account | funded by the account / the account funds |
| renewal_payment | dh_tier | dhmo.dhmo_plans | billing account | funded by the account / the account funds |
| renewal_payment | dh_plan | dhmo.dhmo_plans | billing account | funded by the account / the account funds |
| renewal_payment | dh_app | dhmo.dhmo_plans | billing account | funded by the account / the account funds |

### (b) Method-shape: no method formula changed (vtc_offset gains an all-tiers-off guard outside its scope); round-4 table stands. (c)/(d) Independence and quote sweep:
sweep (25 factors): no factor reads another factor's binding, no plain binding reads a factor binding, one owner per binding, compute_basis quotes verbatim, no duplicated selection; failures=0

(e) Trigger rule unchanged (billing_premium_credit and billing_payment_received -> billing:billing_paid_through_update only).

### Gate block
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
REWORK round 7 claims: KB-B0-1, SRC-1, R0-1
REWORK round 7: gates 7/7 green

## Rework round 8 (C-r7-1)
- VTC guard rewritten so rule words == compute: the offset is skipped only when a vision enrollment of the subscriber funded by another account is applied or active, or ended by termination within the unit's coverage window (whole months from its termination date to the credit date no more than those from the unit's coverage effective date, the same test a service passes); cancelled enrollments and enrollments that ended before the window are not counted (binding v_other replaces v_all / v_acct). Whole-class sweep: every status test in the five policies listed below with its rule wording; the 'not terminated' vision and DHMO selections in DTC / REC / RNP now read 'applied or active (neither terminated nor cancelled)', exactly the compute's termination_reason='not_terminated'. No scored value or world row moved (all expected values, baselines and sensitivities recomputed and unchanged).

### (a) Probes (scratch copies, task 0 world; first five lines: recomputed task values unchanged)
# 0 billing_ext_vision_term_credit True True []
# 0 billing_ext_grace_cure_payment True True []
# 1 billing_ext_dental_tier_credit True True []
# 1 billing_ext_rider_end_credit True True []
# 1 billing_ext_renewal_payment True True []
| probe | v_other | vtc_offset | expected offset | ok |
|---|---|---|---|---|
| P7-a: other-account enrollment terminated voluntarily 2021-12-31 | 0 | 79.76 | 79.76 | ok |
| other-account enrollment active now | 1 | 0 | 0 | ok |
| other-account application cancelled (withdrawn) | 0 | 79.76 | 79.76 | ok |
| other-account enrollment terminated 2026-03-31, inside the unit's window | 1 | 0 | 0 | ok |
| other-account enrollment terminated 2025-10-31, the day before the unit's start (same whole-month count as the start: counted, as the rule states) | 1 | 0 | 0 | ok |
fails 0

### Status-test sweep (every holds/has/status test, all five policies)
| policy | binding | status test in compute | rule wording (compute_basis, abridged) |
|---|---|---|---|
| vision_term_credit | vt_date | termination_reason=voluntary | The vision plan unit is the plan unit of the subscriber's vision enrollment funded by the account that shows a voluntary termination, that is every vi |
| vision_term_credit | vt_tier | termination_reason=voluntary | The unit's filed monthly premium is the monthly premium of the unit's vision plan for the unit's coverage tier. |
| vision_term_credit | plan_units | status=active | counted as two plan units for its dental and vision plans plus one for each active orthodontic rider it funds |
| vision_term_credit | ap_record | arrangement AutoPay discount, arrangement accepts bank draft | which the account's arrangement shows either by carrying an AutoPay discount or, where the arrangement does not accept bank draft, by regular automati |
| vision_term_credit | v_draft_in_grace | account status | whose automatic draft, a returned payment by bank draft that had paid one, three or twelve coverage months, was returned on or after the grace-period  |
| vision_term_credit | v_other | status=active, status=applied, status=terminated | so the benefits paid are counted only when no vision enrollment of the subscriber funded by another account could carry services inside the unit's cov |
| vision_term_credit | req_date | request_status=confirmed | the confirmed voluntary-termination request for the unit's subscriber enrollment, taken as the one registered last (of two registered at the same mome |
| grace_cure_payment | g_next | arrangement AutoPay discount | The invoice issued last is added by how the grace period arose: when an automatic draft was returned on or after the grace-period start date and the i |
| grace_cure_payment | left_ap | arrangement AutoPay discount, arrangement accepts bank draft | The account left AutoPay when its arrangement carries no AutoPay discount and does not accept bank draft and the account nevertheless collected at lea |
| grace_cure_payment | g_disc | arrangement AutoPay discount | An AutoPay discount is withdrawn and added: when two or more payments of the account by bank draft or card were returned within twelve months before t |
| grace_cure_payment | g_fee | arrangement AutoPay discount | Returned-payment fees are collected according to how the account pays: when the account left AutoPay, every returned-payment fee booked within twelve  |
| dental_tier_credit | dl_e_child | termination_reason=loss_of_eligibility | The departed dependent is the subscriber's child, spouse or domestic partner whose dental enrollment funded by the account ended for loss of eligibili |
| dental_tier_credit | sub_tier | status=active | The tier after the drop and the plan are those recorded on the subscriber's active dental enrollment funded by the account, taken as the one with the  |
| dental_tier_credit | dtc_window | account status | The months counted are replaced by how the account is billed: on an arrangement that carries a prepay discount and has issued a twelve-month invoice w |
| dental_tier_credit | dr_plan | status=terminated | the ended orthodontic rider (the account's terminated rider with the latest termination date, the one recorded first on a tie) priced in at its plan's |
| dental_tier_credit | dv_tier | termination_reason=not_terminated | each orthodontic rider the account funds that is active or applied at its plan's monthly premium per covered person, riders applied for after the invo |
| dental_tier_credit | d_act_r | status=active, status=applied | each orthodontic rider the account funds that is active or applied at its plan's monthly premium per covered person, riders applied for after the invo |
| dental_tier_credit | d_inscope | status=active, status=applied | This reading of the invoice issued last is made only on an account on which, for each orthodontic rider plan, its active riders and, separately, its a |
| dental_tier_credit | d_dh_tier | termination_reason=not_terminated | the subscriber's DHMO enrollment funded by the account that is not terminated (the one with the latest coverage effective date, the one recorded first |
| rider_end_credit | r_end | status=terminated | The ended rider is the orthodontic rider funded by the account whose status is terminated, and where more than one is on record, the one with the late |
| rider_end_credit | r_plan | status=terminated | its rider premium is the rider plan's monthly premium per covered person |
| rider_end_credit | plan_units | status=active | counted as two plan units for its dental and vision plans plus one for each active orthodontic rider |
| rider_end_credit | rc_months | account status | The rider months are replaced by how the account is billed: on an arrangement that carries a prepay discount and has issued a twelve-month invoice wit |
| rider_end_credit | ap_record_r | arrangement AutoPay discount, arrangement accepts bank draft | which the account's arrangement shows either by carrying an AutoPay discount or, where the arrangement does not accept bank draft, by regular automati |
| rider_end_credit | cd_tier | status=active | its current tier being the coverage tier recorded on the subscriber's active dental enrollment funded by the account with the latest coverage effectiv |
| rider_end_credit | cv_tier | termination_reason=not_terminated | each orthodontic rider the account funds that is active or applied at its plan's monthly premium per covered person, riders applied for after the invo |
| rider_end_credit | qe_e_child | termination_reason=loss_of_eligibility | that is the coverage tier recorded on the dental enrollment funded by the account of the subscriber's child, spouse or domestic partner that ended for |
| rider_end_credit | q_act_r | status=active, status=applied | each orthodontic rider the account funds that is active or applied at its plan's monthly premium per covered person, riders applied for after the invo |
| rider_end_credit | q_inscope | status=active, status=applied | This reading of the invoice issued last is made only on an account on which, for each orthodontic rider plan, its active riders and, separately, its a |
| rider_end_credit | q_dh_tier | termination_reason=not_terminated | the subscriber's DHMO enrollment funded by the account that is not terminated (the one with the latest coverage effective date, the one recorded first |
| renewal_payment | rl_e_child | termination_reason=loss_of_eligibility | The departed dependent is the subscriber's child, spouse or domestic partner whose dental enrollment funded by the account ended for loss of eligibili |
| renewal_payment | ds_tier | status=active | the subscriber's current dental tier and plan are those of the subscriber's active dental enrollment funded by the account with the latest coverage ef |
| renewal_payment | rr_end | status=terminated | The ended rider is the orthodontic rider funded by the account whose status is terminated, the one with the latest termination date (of two with the s |
| renewal_payment | rr_plan | status=terminated | its premium is the rider plan's monthly premium per covered person |
| renewal_payment | v_eff | termination_reason=not_terminated | The subscriber's vision enrollment is the subscriber's vision enrollment funded by the account that is not terminated, the one with the latest coverag |
| renewal_payment | act_r | status=active, status=applied | each orthodontic rider the account funds that is active or applied at its plan's monthly premium per covered person, riders applied for after the rene |
| renewal_payment | inscope | status=active, status=applied | This reading of the renewal invoice is made only on an account on which, for each orthodontic rider plan, its active riders and, separately, its appli |
| renewal_payment | dh_tier | termination_reason=not_terminated | the subscriber's DHMO enrollment funded by the account that is not terminated (the one with the latest coverage effective date, the one recorded first |

(b) Method formulas unchanged; round-4 table stands. (e) Trigger rule unchanged.

(c)/(d) sweep: no factor reads another factor's binding, no plain binding reads a factor binding, one owner per binding, compute_basis quotes verbatim, no duplicated selection; failures=0

### Gate block
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
REWORK round 8 claims: C-r7-1
REWORK round 8: gates 7/7 green

## Rework round 9 (C-r8-1, coordinator route)
- VTC guard replaced by one exact, coarse record test stated verbatim in the rule: the vision benefits paid are counted only when no vision enrollment of the subscriber other than a cancelled application has ever been funded by another billing account; otherwise no offset is deducted. Compute v_other = (subscriber's vision enrollments - cancelled ones) - (those funded by this account - cancelled ones); offset 0 when v_other > 0. Purpose clause and every window/overlap reasoning removed. No scored value or world row moved.

### (a) Probes (scratch copies; first lines: recomputed task values unchanged)
# task 0 billing_ext_vision_term_credit expected True baseline True sensitivities-mismatch []
# task 0 billing_ext_grace_cure_payment expected True baseline True sensitivities-mismatch []
# task 1 billing_ext_dental_tier_credit expected True baseline True sensitivities-mismatch []
# task 1 billing_ext_rider_end_credit expected True baseline True sensitivities-mismatch []
# task 1 billing_ext_renewal_payment expected True baseline True sensitivities-mismatch []
| probe | v_other | vtc_offset | expected offset (stated test) | ok |
|---|---|---|---|---|
| auditor's case: group vision enrollment on an employer account starting after the unit's window (2026-08-01, active) | 1 | 0 | 0 | ok |
| cancelled application on another account | 0 | 79.76 | 79.76 | ok |
| enrollment on another (closed) account that ended 2021-12-31 | 1 | 0 | 0 | ok |
| current active enrollment on another account | 1 | 0 | 0 | ok |
| no other-account enrollment (task 0 world as seeded) | 0 | 79.76 | 79.76 | ok |
fails 0

(b) Method formulas unchanged. (e) Trigger rule unchanged. Status-test sweep of round 8 stands; the VTC v_other row now reads: status=cancelled excluded, any other status counted, ever, on another billing account.

(c)/(d) sweep: no factor reads another factor's binding, no plain binding reads a factor binding, one owner per binding, compute_basis quotes verbatim, no duplicated selection; failures=0

### Gate block
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
REWORK round 9 claims: C-r8-1
REWORK round 9: gates 7/7 green

## Rework round 10 (C-r9-1, text only)
- VTC guard wording now names exactly what the compute exempts: 'no vision enrollment of the subscriber other than one whose status is cancelled (an application withdrawn before its start, an application cancelled for an unpaid binder, or a plan returned in the free-look period) has ever been funded by another billing account' — the three vision lifecycle events that end in status cancelled. Compute byte-identical; worlds and values unchanged.

### (a) Probes (scratch copies; first lines: recomputed task values unchanged)
# task 0 billing_ext_vision_term_credit expected True baseline True sensitivities-mismatch []
# task 0 billing_ext_grace_cure_payment expected True baseline True sensitivities-mismatch []
# task 1 billing_ext_dental_tier_credit expected True baseline True sensitivities-mismatch []
# task 1 billing_ext_rider_end_credit expected True baseline True sensitivities-mismatch []
# task 1 billing_ext_renewal_payment expected True baseline True sensitivities-mismatch []
| probe | v_other | vtc_offset | expected offset (stated test) | ok |
|---|---|---|---|---|
| 2019 plan on another account returned in the free-look period (status cancelled, free_look) | 0 | 79.76 | 79.76 | ok |
| application on another account withdrawn before its start (status cancelled, application_withdrawn) | 0 | 79.76 | 79.76 | ok |
| application on another account cancelled for an unpaid binder (status cancelled, binder_not_paid) | 0 | 79.76 | 79.76 | ok |
| enrollment on another account that ended 2021-12-31 (status terminated) | 1 | 0 | 0 | ok |
fails 0

(b) Method formulas unchanged. (c)/(d) Compute unchanged; compute_basis quotes re-checked verbatim. (e) Trigger rule unchanged.

### Gate block
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
REWORK round 10 claims: C-r9-1
REWORK round 10: gates 7/7 green

## Rework round 11 (KB cross-product re-judge SRC-R3-1, SRC-R3-2, SRC-R3-3; seed only)
- billing.extended.yaml (50297dc0208bd324) and task_tools.py (b19f12afdf2130ae) byte-identical.
- Exhaustive other-product pass, both worlds, every row re-priced from the published docs as of its date:
  | world | rows | docs give | action |
  |---|---|---|---|
  | 0 | dental_plans x4 (Classic 1250 family, eff 2022-07-01) and premium 107.66 | as recorded | none |
  | 0 | vision_plans x5, vision_coverage_requests x2, Select 130 family 36.28 | as recorded | none |
  | 0 | exam claims x5 (45.00 OON), lens claims x2 (30.00), duplicate exam + reversal | as recorded | none |
  | 0 | frame claims 38308cc5 (Lucia, 13), d1840869 (Mateo, 10) at 65.00 | children's OON frame amount 90.00 | re-priced (SRC-R3-1) |
  | 0 | ortho_riders 99429870 (active), 1da95e2f (withdrawn) eff 2025-06-01 | permitted start 2026-01-01 | re-dated; invoices and drafts 2025-07..12 re-priced without the rider: 106.66 / 142.94 (SRC-R3-3) |
  | 1 | dental_plans x3, Gabriel's LOE end 2025-11-30, premiums 131.17 / 80.92 | as recorded | none |
  | 1 | ortho_riders 2b9dff86, 261b5f8d and Family 1500 12.60 | as recorded | none |
  | 1 | vision_plans 08852f82, c1a26c05 eff 2027-01-01 applied 2026-11-20 | first of the month after receipt | application re-dated 2026-12-02, frozen_time 2026-12-04 10:20:00 PST, persona updated (SRC-R3-2) |
  | both | DHMO, group, savings, provider, dental claims, ortho cases | none seeded | none |
- Scored values moved: task 0 vision credit (24.56, coverage month 2026-10, 3 months) and grace-cure payment (317.62); task 1 dental credit (684.53), rider credit (175.37) and renewal payment (334.17). Gold args, expected values, baselines, factor sensitivities, traces, argument tracing, closure, business effects, seed checks, personas and rationales updated consistently; every factor still bears weight (recomputed sensitivities all differ from gold) and every prerequisite edge still holds.

### (a) Seed-date replays and load-bearing checks
| check | value |
|---|---|
| VTC on the 2026-07-08 ledger (seeded prior credit 10.00) | 10.0 |
| DTC on the 2025-12-05 ledger (seeded 48.24) | 48.24 |
| REC on the 2025-12-05 ledger (seeded 12.10) | 12.1 |
| GCP skipping the vision credit | 342.18 |
| RNP skipping the dental credit | 1018.7 |
| RNP skipping the rider credit | 509.54 |

(b)/(c)/(d) Charter unchanged (byte-identical): method-shape table, independence check and quote sweep of round 10 stand. (e) Trigger rule unchanged.

### Gate block
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK. (TRACEABILITY OK as well.)
REWORK round 11 claims: SRC-R3-1, SRC-R3-2, SRC-R3-3
REWORK round 11: gates 7/7 green

# worklog — home_delivery_orders_and_billing (category mail, M=2)

## Step 0 — draws (scripts/draw_counts.py --tasks 2)
```
{"task": 0, "key": "env_0047_pharmacy_benefit_manager/home_delivery_orders_and_billing/0", "prerequisite_problems": 3, "problems": 4, "factor_counts": [6, 6, 6, 6]}
{"task": 1, "key": "env_0047_pharmacy_benefit_manager/home_delivery_orders_and_billing/1", "prerequisite_problems": 2, "problems": 3, "factor_counts": [6, 6, 6]}
```

## Step 0 — difficulty pre-check (base charter mail)
- Writable events with no cross-category trigger: mail_activate, mail_release, mail_close, mail_preferences_update,
  mail_rx_received, mail_order_placed, mail_order_cancelled, mail_order_replaced, mail_shipping_charged,
  mail_payment_posted, mail_credit_issued (shipping_fee_waived / small_balance_writeoff only), mail_refund_issued.
- EXCLUDED: mail_order_shipped (triggers plan:plan_ded_post / plan_oop_post whenever deductible/accumulator != 0, i.e. every
  real charge) and pharmacy_error credits (trigger plan reversals) — no task tool may write them.
- Holds are avoided in every seed: a release write has no computation and could not be a problem of a tree.
- Numeric writes available: shipping fee, credits, payments (member card), payment-plan terms, order days supply.
- Owner=user writes in the charter: member card payments, payment-plan confirmation.

## Space budget (Principle C)
- task 0 (4 problems): payment-plan tree — root payment plan (user) <- plan down payment (user) <- unbilled expedited
  fee (agent) and <- missed-delivery fee credit (agent).
- task 1 (3 problems): first-fill tree — root first fill of a new prescription (agent) <- past-due payment (user) <-
  plan installment due (user).
- The two trees share no policy, tool or edge; task 1 keeps an order-placement core and a past-due/installment core that
  task 0 never touches.

## Task 0 progress
- Policies written: mail_ext_expedited_fee_catchup (book_expedited_fee_b4b37c53, agent), mail_ext_missed_delivery_credit
  (credit_missed_delivery_02a65815, agent), mail_ext_plan_down_payment (pay_plan_down_payment_b796ac1b, user),
  mail_ext_installment_terms (confirm_payment_plan_4c427b9b, user, root). check_task_tools: TASK TOOL CONTRACT OK.
- Seed built (Premier program, Anchorage AK member, opening balance 162.46).
- Handling-time recompute: fee 12.36, credit 40.92, down payment 14.73, plan 6 months x 19.47.
- Revision: down-payment all-baseline equalled gold (net rate 0.10 = default 0.10) -> long-tenure reduction changed
  5 -> 4 points; rate 0.11, down payment 14.73, installment 19.47. All 24 factors move result on this world.
- Note: the missed-delivery credit's overwrite quotes the mail_shipping credit-back clause, which the gate scripts read
  as retiring mail_shipping.one_fee_per_order; the fee-booking write still declares that dedup gate (tolerated) and
  books one fee on an order carrying none.
- Gold path revised: added find_mail_prescriptions and find_retail_benefits reads (closure), dropped unread sponsor,
  formulary and specialty-fill rows (replay closure mismatch 16 rows -> 0). Inlined the account lookup in each tool
  (a module-level helper was mistaken for an undiscoverable tool by check_extended).
- tasks/0.json written. Per-task gates (task 0): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK,
  COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.
- Manual values gates (task 0): tree fee+credit -> down payment -> plan; every prerequisite false at the opening by row
  evidence; owner=user writes are the member's own card payment and plan confirmation; persona raises only monthly
  payments; no real-world wait (all writes are bookings on the spot; the replacement already shipped 2026-08-10).
- Revision: the T11 historical fee and the task-1 2025 credit were reseeded at the charter formula's own rounding
  (22.45, 12.72) so history never contradicts the rule; task 0 figures unchanged (opening balance 162.45).

## Task 1
- Policies: mail_ext_dispensing_delay_credit (credit_dispensing_delay_47b21103, agent), mail_ext_installment_catchup
  (pay_plan_installment_04171a93, user), mail_ext_past_due_settlement (pay_past_due_balance_de0abde8, user, root).
- Tree: settlement <- installment catch-up (state_gate, state form) and <- dispensing-delay credit (value_input, state form).
- Seed: Maintenance 90 account in Honolulu, June 2026 plan recomputed with the task-0 down-payment/plan policies on
  2026-06-15 (down 7.57, 4 x 34.72). Figures: credit 48.12, installments 3-4 70.19, settlement 58.62.
- Revision: MAX of installment numbers returned a float that missed the integer filter -> cast with int() in compute.

## Final difficulty run (no --task)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK (suite means branches 48.50, steps 18.00;
history_rows_max 92; branches_max 54) / GROUNDING OK / CACHE-DIFF INFO / SCOPE OK. check_traceability skipped (no KB yet).
Coverage: 7 extended policies, task 0 claims 4, task 1 claims 3, disjoint.

## Round 2 — audit rework (audits/policy_task/home_delivery_orders_and_billing/)
- Charter: G-F1 windows relabelled parameter; honest method factors added (fee late_booking_treatment, missed-delivery
  lost_supply_allowance, down-payment tenure_rate_reduction, dispensing-delay dispensing_delay_share, settlement
  shipment_volume_rate: per-unit / flat / none). G-F2 dispensing delay counted in business days (base S6, no override).
  G-F3 waiver combination stated (shares of the original charge, added, taken off once). G-F4 settlement period stated
  as a whole-month convention, contradiction removed. G-F5 PD-1/PD-2/PS-2 name the account's most recent
  shipment/replacement. G-OBS-1 cold-chain: no expedited fee. G-OBS-3 record words cancelled/completed. G-OBS-4 shipped
  orders only.
- Task 0 (T0-F1, T0-F2): September order placed 2026-09-03 (1 business day, within promise); recomputed fee 23.72,
  credit 40.42, down 18.22, plan 6 x 18.97; per-task gates green.
- Task 1 (T1-F1, T1-F2, T1-F3): seed moved to Northbridge Home Delivery Advantage (June plan balance after down payment
  157.50 >= 150 plan minimum; pre-plan shipments within the 200.00 limit); 2025 Jardiance order ships 1 business day late,
  its credit 7.61 and the June plan (down 10.95, 4 x 38.13) recomputed with the charter; persona card wording FSA (Plus is
  copay-only, not HDHP). New figures: delay credit 31.04, installments 3-4 77.01, settlement 56.58; per-task gates green.

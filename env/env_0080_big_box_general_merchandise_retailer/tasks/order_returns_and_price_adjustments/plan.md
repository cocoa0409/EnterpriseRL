# plan — order_returns_and_price_adjustments (category order), M=2  (v2, supersedes v1)

Draw (draw_counts.py --tasks 2): task 0 prereq=3 factors=[4,6,4,6]; task 1 prereq=1 factors=[4,6]

Hard constraints (reasoning in worklog.md):
- Trigger rule: every tool fixes payment_method_type=external_card, refund_method=original_payment, plan_id="",
  fee_waiver_source=none -> no order event written by a task tool lands in card/gift/plan/membership.
- Owed-write: no refunded line earned Northgate Cash (task 1 membership canceled on fulfilment date; task 0 order
  not fulfilled), no plan covers a refunded unit, no card-paid line.
- DSL: order-level aggregates over literal attributes (fee_type set on refund rows = refunded fee's type).

Task 0 (4 problems) — Scheduled Large-Item Delivery order, placed, delivery is today (day-of):
 root U0 order_ext_late_change_fee     user tool: customer reschedules inside the cutoff + late-change fee (6)
 E0 order_ext_misbooked_change_fee_refund agent: refund a late-change fee booked on a change no customer requested (4)
 D0 order_ext_missed_appointment_credit   agent: credit on the delivery fee for an appointment Northgate moved (4)
 H0 order_ext_replacement_haul_away_credit agent: haul-away credit for an old appliance settled under a Northgate
                                          Protect claim (cross-difficulty plan) (6)
 edges U0<-E0 value (late-change fees standing), U0<-D0 value (delivery charges standing / cap),
       U0<-H0 value (haul-away standing)

Task 1 (2 problems) — Same-Day Delivery express order (member price on order date), delivered next day:
 root B1 order_ext_drive_up_return_refund  user tool: customer's own changed-mind Drive Up return (6)
 C1 order_ext_late_express_credit          agent: credit on the express fee for a missed express promise (4)
 edge B1<-C1 value (restocking rate tier reads the late-delivery credit standing on the order)
 cross-difficulty: membership (tier/status on order date -> small-order deduction)

Files: order.extended.yaml, task_tools.py, tasks/0.json, tasks/1.json, worklog.md.
Scratch: /tmp/order_returns_and_price_adjustments_0080/ (builder + evaluator scripts).

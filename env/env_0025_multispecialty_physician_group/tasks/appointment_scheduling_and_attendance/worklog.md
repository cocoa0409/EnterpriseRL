# worklog: appointment_scheduling_and_attendance (erl-task-instantiate, round 1)

## Step 0: difficulty pre-check (done), then STOPPED on a blueprint capability gap

Draw (`draw_counts.py <diff> --tasks 2`):
- task 0: prerequisite_problems=3, problems=4, factor_counts=[5, 4, 4, 5]
- task 1: prerequisite_problems=2, problems=3, factor_counts=[6, 6, 4]

So the difficulty needs 7 extended policies. Each one needs its own task tool, disjoint across tasks,
and each one needs a scored write parameter computed from 4 to 6 load-bearing factors. Each task also
needs at least one owner=user task tool that carries a computed value.

### The scored writes the appointment charter allows under the skill's hard rules

| event (appointment charter) | trigger into another category | base gates (check_solvability) | numeric/computable field it writes |
|---|---|---|---|
| appointment_fee_assessed | billing:billing_charge_posted for fee_type no_show_fee and late_cancel_fee (every real fee) | late_timing_recorded / visit_missed | amount. FORBIDDEN (Principle D trigger rule) |
| appointment_fee_waived | billing:billing_adjustment_posted whenever applies_to_event_id is not empty | documentation_window: kind time, authority mixed, one correlation field. `{system, caller}` cannot both bind a single gate_field, so it can never pass. waive_once: dedup on applies_to_event_id | amount. FORBIDDEN after assessment; unsatisfiable at assessment |
| appointment_deposit_released | billing for applied_to_visit and forfeited_to_fee | policy_scope | amount; only disposition=refunded is legal |
| appointment_deposit_collected | none | one_deposit (appointment_id) | amount |
| appointment_cancelled | own category only | policy_scope | no number; cancel_timing enum |
| appointment_rescheduled | none | open_for_reschedule, under_reschedule_limit | reschedule_count (previous + 0 or 1 by base rule) |
| appointment_confirmed (lifecycle by: user) | none | policy_scope | nothing computable (status, confirmed_date = handling date) |
| appointment_booked | none | no_duplicate_same_day needs a system-sourced scheduled_date; referral_covers_visit needs a referral_id | nothing numeric |
| appointment_checked_in / completed / no_show_recorded | completed triggers referral | front desk / system transitions | not a phone-desk write |

The DSL has no date constructor. The history primitives are scoped to one appointment, and the own
category cannot be read as a cross category, so another appointment's rows are never readable by a
computation.

### What that leaves

- Money-bearing writes with a real multi-factor computation: exactly two event families,
  deposit_collected (in) and deposit_released/refunded (out). The only partial refund the base allows
  (the part above a forfeited fee) needs a forfeited_to_fee row, which is forbidden.
- Other computable decisions: cancel_timing (a genuine timely/late classification) and
  reschedule_count (a 0/1 increment by base rule, with no ladder of 4 to 6 real factors).
- Owner=user writes that carry a computed value: only the patient paying their own booking deposit.
  Confirming attendance, which the blueprint names as the patient's own act, writes no computable
  value.

The draw needs 7 distinct task tools, each with a 4 to 6 factor computation, and 2 distinct
owner=user tools that carry computed values. At most 3 or 4 business-distinct computed writes exist,
and only 1 of them is a user write. Filling the gap would take one of three moves, and the skill
forbids all three:
- writing fee rows that trigger billing (Principle D);
- near-synonym tools or invented factor ladders (Principles A and C);
- editing the blueprint (the skill says to fix the blueprint, and this run is forbidden to modify it).

### Blueprint fixes that would unblock this difficulty (for the coordinator)

1. Let appointment fees be scored inside the appointment category. Either drop the billing triggers
   from appointment_fee_assessed, appointment_fee_waived and appointment_deposit_released
   (forfeited_to_fee), or add appointment-side events whose billing posting is not a trigger. The
   no-show fee, late-cancellation fee, waiver and forfeiture computations are the core the difficulty
   summary describes.
2. Make fee_waiver.documentation_window satisfiable. Either change the authority from mixed to
   system_record (the documentation receipt date is a record), or add a second correlation field, so
   a mixed gate can bind a caller value and a system value.
3. Add a second patient-owned write that carries a quantity. Examples: the patient's acknowledgement
   of a late-cancellation charge with its amount, or the patient's own payment of an assessed
   appointment fee.

No extended yaml, task tools or task files were written. Writing them would mean breaking the rules
above, and they would fail the policy audit.

## Round 2: route-around decisions (the blueprint stays frozen; the finding is logged as BLUEPRINT-KNOWN)

Coordinator decision: the blueprint will not be edited, and stopping is not an outcome, so every
defect is routed around inside the extended policies, task tools and tasks. Decisions:

R1. Fees are never assessed by a task tool. Every no-show or late-cancellation fee in this difficulty
    is decided as a Medicaid fee prohibition AT ASSESSMENT: an appointment_fee_waived row with
    applies_to_event_id empty. That is the row shape whose billing trigger never fires. The scored
    value is the fee the visit carries, which the waiver records.
R2. fee_waiver.documentation_window (a mixed-authority gate on one field, which can never pass) and
    fee_waiver.waive_once (dedup on an empty applies_to_event_id) do not fit a waiver recorded at
    assessment. The two fee-prohibition policies name both sentences in `overwrite` and replace them
    with their own sentences for the at-assessment prohibition. Base text is untouched.
R3. Deposit releases are only ever disposition=refunded (applied_to_visit and forfeited_to_fee trigger
    billing). Refund amounts come from the deposit ledger less the part of the fee the visit carries
    that no recorded prohibition covers; the gold world always carries a full prohibition.
R4. Deposit collections have no trigger. The patient pays them in person (owner=user): the booking
    deposit (task 0) and the deposit balance after a patient move (task 1). The balance is a second
    collection on the same visit, so that policy overwrites "One deposit is collected per
    appointment." and "A reschedule carries the deposit to the new slot."
R5. The compute DSL cannot read a time of day, so cancellation timing is decided in whole calendar
    days. The timing policy overwrites the base full-elapsed-hours sentence; the required days start
    from cancel_notice_hours / 24, rounded up.
R6. Seven distinct task tools, disjoint across tasks:
    - task 0: cancel_patient_appointment_f57629ba (agent), record_late_cancel_fee_prohibition_784c7051
      (agent), refund_late_cancel_deposit_f012ee38 (agent), pay_booking_deposit_d4a062b3 (user);
    - task 1: record_no_show_fee_prohibition_783ac881 (agent), refund_missed_visit_deposit_4264223f
      (agent), pay_deposit_balance_07a1fa0e (user).
R7. Value flows only within one appointment (history reads are holding-scoped), so value_input edges
    link problems on the same visit:
    - cancellation -> late-cancel fee prohibition (reads the recorded timing and the cancellation date);
    - fee prohibition -> deposit refund (reads the waived amount).
    Each deposit payment on another visit links to its refund through a state_gate edge. The refund
    waits until the patient's other open self-pay visits hold the deposit they owe.

## Task 0 closed (2026-09-25)
- Draw [3 prerequisite problems; factor counts 5,4,4,5]. Root: appointment_ext_late_cancel_deposit_refund.
- Tree (topological order): cancellation_notice_days (4 factors, agent) -> late_cancel_fee_prohibition (5 factors, agent, value_input) -> self_pay_booking_deposit (4 factors, user, state_gate) -> refund (5 factors, value_input).
- Gold: cancellation timing late; fee prohibition 47.50; booking deposit 125.00; refund 300.00.
- All-factors-at-baseline figures: timely / 40.00 / 100.00 / 307.50.
- Per-task gates for task 0, all green: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

## Task 1 closed, and the difficulty closed (2026-09-25)
- Draw [2 prerequisite problems; factor counts 6,6,4]. Root: appointment_ext_missed_visit_deposit_refund.
- Tree:
  - refund -> no_show_fee_prohibition: 6 factors, agent, value_input.
  - refund -> moved_visit_deposit_balance: 4 factors, user (pay_deposit_balance_07a1fa0e), state_gate.
- Gold: fee prohibition 222.50; deposit balance 25.00; refund 390.00.
- All-factors-at-baseline figures: 150.00 / 0.00 / 462.50.
- Per-task gates for task 1, all green.
- Coverage: 7 extended policies and 7 task tools across the two tasks, pairwise disjoint.
- Suite metrics: branches mean 53.00; steps mean 13.50; history_rows_max 8; branches_max 56.
- Final gate block, all green: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO (optional diagnostic), SCOPE OK.
- Traceability was skipped by instruction (the KB is not published yet).
- The temporary authoring scripts (scratchpad/appt_inst) have been removed.

## Rework round 2 (audit audits/policy_task/appointment_scheduling_and_attendance, revision 1)
Charter changes, persisted before the task rebuild:
- F1: P1 now also overwrites cancellation_timing s7 (cancel-to-rebook) and appointment_reschedule's
  hours parenthetical, so all three timeliness sentences use the notice-days rule. appointment_reschedule
  is added to P1's base_policy_refs.
- F2: the fee-history windows of P2/P3 now end on "the day the fee is decided" / "the refund date", the
  same anchor the compute uses (NOW).
- F3: every rate ladder is relabelled `parameter`. The honest method factors are:
  - P1: the preparation-day anchor, kept.
  - P2/P3: a preparation-day anchor for the notice counted for the fee (the day the notice is counted to).
  - P4/P7: the unpaid-balance selection. This is a selection rule: the balance less the remaining plan
    balance when a payment plan is active, the balance reduced by the hardship percentage when an approval
    stands, otherwise the whole balance.
  - P5/P6: the held-slot anchor (counted from the latest move, the confirmation date or the booking date).
- F4: removed from P2/P3/P5/P6 the unpaid-balance surcharge, the deposit-size credit and the
  payment-plan fee adjustment.
  - New multi-source factor in P2/P3/P5/P6: attendance escalation. Two or more fees with at least one
    no-show raise the fee by half; at least one fee otherwise raises it by a quarter. It reads two distinct
    ledger categories.
  - P5/P6 gain a hardship reduction (approval covering the visit date gives the approved percentage;
    approval ended within 90 days gives half) and a courtesy credit for account age.
- Factor counts now: P1 5, P2 4, P3 4, P4 5 (task 0 multiset {5,4,4,5}); P5 6, P6 6, P7 4 (task 1).
- Observations addressed:
  - The action-form restatements ("once ... decided") are removed from P3/P6.
  - P4 now has a floor of zero ("none is owed where the visit type's self-pay booking deposit is 0.00 or
    where the figure worked out is zero or less").
Tasks rebuilt on the reworked charter:
- Task 0 world:
  - the consult moves to 2026-10-01, confirmed 2026-09-20;
  - a 50.00 move balance was collected on 2026-09-01;
  - a 3-month plan was added (133.33 remaining) with its self-pay visit charge and first installment;
  - a find_payment_plans read node was added (the call steps shift to 8/10/12/14).
  - Gold: late / 47.50 / 125.00 / 350.00.
- Task 1 world:
  - the CT was moved on 2026-07-12, with a 35.00 balance collected that day (held 425.00);
  - the consult's first-move balance is split 20.00 + 15.00; its latest move was 2026-09-12 to 2026-09-25;
  - a 20 percent hardship approval runs through 2026-12-31.
  - Gold: 174.00 / 25.00 / 425.00.
- Full final gate block green: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK
  (branches mean 59.00, steps mean 14.00, history_rows_max 8, branches_max 64), GROUNDING OK,
  CACHE-DIFF INFO, SCOPE OK.
- Traceability was skipped by instruction. The temporary scripts (scratchpad/appt_rw) have been removed.
